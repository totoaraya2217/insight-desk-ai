import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";
import TextoAgente from "./TextoAgente.jsx";

const SUGERENCIAS = [
  "¿Cuál es el resumen de ventas?",
  "¿Qué productos tienen bajo rendimiento?",
  "¿Qué categoría genera más ingresos y qué recomiendas?",
];

const NOMBRES_HERRAMIENTAS = {
  consultar_resumen_ventas: "Resumen de ventas",
  consultar_ventas_por_producto: "Ventas por producto",
  consultar_ventas_por_categoria: "Ventas por categoría",
};

// Turnos previos que se envían como contexto (el backend acepta hasta 20).
const MAX_HISTORIAL = 10;

export default function AgentPanel({ health }) {
  const [mensajes, setMensajes] = useState([]);
  const [entrada, setEntrada] = useState("");
  const [enviando, setEnviando] = useState(false);
  const finRef = useRef(null);

  const configurado = health.data?.agent_configured;
  const disponible = Boolean(configurado) && !health.error;

  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [mensajes, enviando]);

  async function preguntar(texto) {
    const pregunta = texto.trim();
    if (!pregunta || enviando) return;

    const historial = mensajes
      .filter((m) => !m.error)
      .slice(-MAX_HISTORIAL)
      .map((m) => ({ rol: m.rol, texto: m.texto }));

    setMensajes((ms) => [...ms, { rol: "usuario", texto: pregunta }]);
    setEntrada("");
    setEnviando(true);
    try {
      const r = await api.chat(pregunta, historial);
      setMensajes((ms) => [
        ...ms,
        { rol: "modelo", texto: r.respuesta, herramientas: r.herramientas_usadas, fundamentada: r.fundamentada },
      ]);
    } catch (err) {
      setMensajes((ms) => [...ms, { rol: "modelo", texto: err.message, error: true }]);
    } finally {
      setEnviando(false);
    }
  }

  function alPresionarTecla(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      preguntar(entrada);
    }
  }

  return (
    <aside className="agent-panel" aria-label="Asistente de IA">
      <header className="panel-header">
        <div>
          <h2>Asistente IA</h2>
          <p className="muted">Pregunta sobre tus ventas en lenguaje natural</p>
        </div>
        <EstadoAgente health={health} />
      </header>

      <div className="chat" aria-live="polite">
        {mensajes.length === 0 && (
          <div className="chat-vacio">
            <p className="muted pequeno">
              {disponible
                ? "Las respuestas se basan solo en los datos registrados. Prueba con:"
                : health.error
                  ? "Sin conexión con el backend."
                  : "Define GEMINI_API_KEY en el entorno del backend y reinícialo para habilitar el asistente."}
            </p>
            {disponible && (
              <div className="sugerencias">
                {SUGERENCIAS.map((s) => (
                  <button key={s} type="button" className="chip" onClick={() => preguntar(s)}>
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {mensajes.map((m, i) => (
          <Mensaje key={i} mensaje={m} />
        ))}

        {enviando && (
          <div className="burbuja burbuja-modelo">
            <span className="spinner" aria-hidden /> <span className="muted">Consultando datos…</span>
          </div>
        )}
        <div ref={finRef} />
      </div>

      <form
        className="agent-input"
        onSubmit={(e) => {
          e.preventDefault();
          preguntar(entrada);
        }}
      >
        <textarea
          rows={2}
          maxLength={2000}
          value={entrada}
          onChange={(e) => setEntrada(e.target.value)}
          onKeyDown={alPresionarTecla}
          placeholder={disponible ? "Escribe tu pregunta… (Enter para enviar)" : "Asistente no disponible"}
          disabled={!disponible || enviando}
          aria-label="Pregunta al asistente"
        />
        <button type="submit" className="btn btn-primary" disabled={!disponible || enviando || !entrada.trim()}>
          {enviando ? "Consultando…" : "Enviar"}
        </button>
      </form>
    </aside>
  );
}

function Mensaje({ mensaje: m }) {
  if (m.rol === "usuario") return <div className="burbuja burbuja-usuario">{m.texto}</div>;
  if (m.error)
    return (
      <div className="burbuja burbuja-error" role="alert">
        ⚠ {m.texto}
      </div>
    );

  const fuentes = [...new Set((m.herramientas ?? []).map((h) => NOMBRES_HERRAMIENTAS[h.nombre] ?? h.nombre))];
  return (
    <div className="burbuja burbuja-modelo">
      <TextoAgente texto={m.texto} />
      {fuentes.length > 0 ? (
        <p className="fuentes">Datos consultados: {fuentes.join(" · ")}</p>
      ) : (
        <p className="fuentes fuentes-aviso">▲ Respuesta sin consulta a datos</p>
      )}
    </div>
  );
}

function EstadoAgente({ health }) {
  if (health.loading && !health.data) return <span className="badge">Verificando…</span>;
  if (health.error) return <span className="badge badge-error">Sin conexión</span>;
  return health.data?.agent_configured ? (
    <span className="badge badge-ok">● Activo</span>
  ) : (
    <span className="badge">Sin configurar</span>
  );
}
