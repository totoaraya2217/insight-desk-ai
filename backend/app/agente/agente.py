"""Agente comercial sobre Gemini (SDK google-genai) con function calling controlado por el backend.

El bucle es manual (llamada automática del SDK desactivada) para que cada invocación pase
por `ejecutar_herramienta`, quede registrada en la traza y tenga un número máximo de pasos.
Los errores del proveedor se traducen a `AgenteError` con mensajes seguros para el cliente.
"""
import json
import logging
from functools import lru_cache
from typing import Callable

import httpx  # instalado por google-genai; el SDK lanza httpx.TimeoutException al vencer el timeout
from google import genai
from google.genai import errors, types
from sqlalchemy.orm import Session

from ..config import settings
from ..schemas import LlamadaHerramienta, RespuestaChat, TurnoChat
from .herramientas import declaraciones, ejecutar_herramienta

log = logging.getLogger(__name__)

INSTRUCCIONES = """Eres InsightDesk AI, analista comercial de la empresa.

Reglas obligatorias:
1. Toda cifra que menciones debe provenir de resultados de herramientas obtenidos en esta conversación. Nunca estimes ni inventes números.
2. Si una herramienta devuelve hay_datos=false, una lista vacía o un error, dilo explícitamente e indica qué dato falta. No completes el hueco con suposiciones.
3. Las herramientas entregan totales históricos; no puedes filtrar por período. Si te piden un período específico, explica esa limitación y ofrece los totales disponibles, indicando el rango de fechas.
4. Interpreta los resultados: destaca líderes, rezagados y concentración de ingresos (participación %).
5. Recomienda acciones comerciales concretas y cita la cifra que respalda cada recomendación.
6. Solo puedes consultar datos; no puedes registrar, modificar ni eliminar información.
7. Responde en español, breve y estructurado. Formatea montos como $1.234.567.
"""

GenerarFn = Callable[[list[types.Content], types.GenerateContentConfig], types.GenerateContentResponse]


class AgenteError(Exception):
    """Error del agente con código HTTP y mensaje apto para mostrar al usuario (sin secretos)."""

    def __init__(self, status_code: int, mensaje: str):
        super().__init__(mensaje)
        self.status_code = status_code
        self.mensaje = mensaje


@lru_cache
def _cliente() -> genai.Client:
    return genai.Client(
        api_key=settings.gemini_api_key,
        http_options=types.HttpOptions(
            timeout=int(settings.gemini_timeout_s * 1000),
            # Sin reintentos automáticos: el timeout configurado es el tiempo máximo real de espera.
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def generar_con_gemini(contenidos: list[types.Content], config: types.GenerateContentConfig) -> types.GenerateContentResponse:
    return _cliente().models.generate_content(model=settings.gemini_model, contents=contenidos, config=config)


def traducir_error(exc: Exception) -> AgenteError:
    """Convierte errores del SDK/red en AgenteError. Nunca incluye el texto original (podría filtrar datos)."""
    if isinstance(exc, AgenteError):
        return exc
    if isinstance(exc, (httpx.TimeoutException, TimeoutError)):
        return AgenteError(504, "Gemini tardó demasiado en responder. Intenta nuevamente.")
    if isinstance(exc, errors.APIError):
        code, status, detalle = exc.code, (exc.status or ""), str(exc)
        if code in (401, 403) or status in ("UNAUTHENTICATED", "PERMISSION_DENIED") or "API_KEY_INVALID" in detalle:
            return AgenteError(503, "El agente no pudo autenticarse con Gemini. Revisa la configuración de la clave en el servidor.")
        if code == 429 or status == "RESOURCE_EXHAUSTED":
            return AgenteError(429, "Se alcanzó el límite de uso de Gemini. Intenta más tarde.")
        if code == 404:
            return AgenteError(502, "El modelo de Gemini configurado no está disponible.")
        if code == 504 or status == "DEADLINE_EXCEEDED":
            # El servidor de Gemini agotó su plazo (modelo saturado o lento).
            return AgenteError(504, "Gemini tardó demasiado en responder (modelo saturado). Intenta nuevamente o usa otro modelo.")
        if isinstance(exc, errors.ServerError):
            return AgenteError(502, "El servicio de Gemini no está disponible en este momento.")
        return AgenteError(502, "Gemini rechazó la solicitud.")
    if isinstance(exc, httpx.HTTPError):
        return AgenteError(502, "No se pudo conectar con Gemini.")
    return AgenteError(500, "Error inesperado del agente.")


def _texto_o_error(respuesta: types.GenerateContentResponse) -> str:
    """Extrae el texto final o lanza AgenteError si la respuesta está vacía o bloqueada."""
    feedback = respuesta.prompt_feedback
    if feedback and feedback.block_reason:
        raise AgenteError(422, "La consulta fue bloqueada por los filtros de seguridad de Gemini. Reformúlala.")
    if not respuesta.candidates:
        raise AgenteError(502, "Gemini devolvió una respuesta vacía. Intenta nuevamente.")
    candidato = respuesta.candidates[0]
    partes = candidato.content.parts if candidato.content and candidato.content.parts else []
    texto = "".join(p.text for p in partes if p.text and not p.thought).strip()
    if texto:
        return texto
    if candidato.finish_reason == types.FinishReason.SAFETY:
        raise AgenteError(422, "La respuesta fue bloqueada por los filtros de seguridad de Gemini.")
    if candidato.finish_reason == types.FinishReason.MAX_TOKENS:
        raise AgenteError(502, "La respuesta de Gemini se cortó antes de completarse. Intenta una pregunta más acotada.")
    raise AgenteError(502, "Gemini devolvió una respuesta vacía. Intenta nuevamente.")


class Agente:
    def __init__(self, db: Session, generar: GenerarFn = generar_con_gemini, max_pasos: int = settings.agente_max_pasos):
        self.db = db
        self.generar = generar
        self.max_pasos = max_pasos

    @staticmethod
    def _config() -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=INSTRUCCIONES,
            tools=[types.Tool(function_declarations=declaraciones())],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=0.2,
        )

    def _llamar_modelo(self, contenidos, config) -> types.GenerateContentResponse:
        try:
            respuesta = self.generar(contenidos, config)
        except Exception as exc:
            error = traducir_error(exc)
            # Se registra el tipo y código, no el mensaje del proveedor.
            log.warning("Fallo al invocar Gemini: %s (code=%s) -> HTTP %s", type(exc).__name__, getattr(exc, "code", None), error.status_code)
            raise error from exc
        if respuesta is None:
            raise AgenteError(502, "Gemini devolvió una respuesta vacía. Intenta nuevamente.")
        return respuesta

    def responder(self, mensaje: str, historial: list[TurnoChat] | None = None) -> RespuestaChat:
        rol = {"usuario": "user", "modelo": "model"}
        contenidos = [types.Content(role=rol[t.rol], parts=[types.Part.from_text(text=t.texto)]) for t in historial or []]
        contenidos.append(types.Content(role="user", parts=[types.Part.from_text(text=mensaje)]))
        config = self._config()
        traza: list[LlamadaHerramienta] = []

        for _ in range(self.max_pasos):
            respuesta = self._llamar_modelo(contenidos, config)
            llamadas = respuesta.function_calls or []
            if not llamadas:
                texto = _texto_o_error(respuesta)
                return RespuestaChat(respuesta=texto, herramientas_usadas=traza, fundamentada=bool(traza))

            # Se conserva el turno del modelo tal cual (incluye firmas de pensamiento de Gemini 2.5).
            contenidos.append(respuesta.candidates[0].content)
            partes = []
            for llamada in llamadas:
                argumentos = dict(llamada.args or {})
                resultado = ejecutar_herramienta(self.db, llamada.name, argumentos)
                resultado = json.loads(json.dumps(resultado, default=str))  # JSON puro hacia el modelo
                traza.append(LlamadaHerramienta(nombre=llamada.name, argumentos=argumentos, resultado=resultado))
                partes.append(types.Part.from_function_response(name=llamada.name, response={"result": resultado}))
            contenidos.append(types.Content(role="user", parts=partes))

        raise AgenteError(502, "La consulta requirió demasiados pasos. Formula una pregunta más específica.")
