# plan.md — Plan de implementación

## Fase 1 — Inicialización ✅ (2026-10-28)
- [x] Crear frontend React + Vite.
- [x] Crear backend FastAPI.
- [x] Configurar Git y .gitignore. — Git 2.56.0, rama `main`, commit inicial `59f56b8`.
- [x] Instalar dependencias autorizadas.

**Dependencias aprobadas:** las de spec.md + `uvicorn` (aprobado). No aprobadas: `httpx` y `python-dotenv`.

**Verificaciones:**
- `pytest`: 4/4 pruebas de humo OK (ruta de salud, clave leída del entorno y nunca impresa, ruta absoluta de SQLite).
- `uvicorn app.main:app` + `GET /api/health` → `{"status":"ok","agent_configured":false}`.
- `npm run build` (Vite 6.4.5): OK, 26 módulos.
- Instalado: fastapi 0.162.0, uvicorn 0.54.0, SQLAlchemy 2.1.6, google-genai 2.33.0, pytest 9.2.0 · react 18.3.1, recharts 2.15.4, vite 6.4.5.

**Decisiones abiertas:**
1. ~~Precio en ventas~~ → resuelto en Fase 2: el backend copia `precio_unitario` del producto; si el cliente lo envía → 422.
2. ~~Stock~~ → resuelto en Fase 2: no se agrega (no está en spec.md).
3. `consultar_ventas_por_producto` debe incluir productos sin ventas (Fase 4).
4. Recharts 2.x está deprecado; propuesta, fijar Recharts 3 (Fase 3, requiere aprobación).
5. spec.md contiene texto ajeno al final (firma y una copia de plan.md); conviene limpiarlo.

## Fase 2 — Datos ✅ (2026-10-28)
- [x] Crear modelos Producto y Venta. — `app/models.py`: campos de spec.md, `CHECK` de precio/cantidad > 0, FK activa (`PRAGMA foreign_keys=ON`).
- [x] Configurar SQLite. — `app/database.py` con SQLAlchemy 2.1; archivo `backend/insightdesk.db` (ruta absoluta); tablas creadas al iniciar.
- [x] Generar datos de demostración. — `python -m app.seed [--reset]`: 8 productos, 4 categorías, **50 ventas** con `random.Random(42)` y fechas fijas 2026-01-01..2026-06-30.
- [x] Implementar endpoints REST. — `GET/POST /api/productos`, `GET/POST /api/ventas`, `GET /api/indicadores`. Validación Pydantic con `extra="forbid"`: nombre/categoría no vacíos, precio > 0, cantidad 1..10.000, fecha no futura. Errores: 422 validación, 404 producto inexistente, 409 nombre duplicado.
- [x] Verificar indicadores con pruebas. — ingresos, cantidad vendida, ticket promedio y ventas por categoría, calculados en SQL (`app/services/indicadores.py`).

**Evidencia:**
- `pytest`: **24/24 OK** (1,5 s). `test_api.py` (9), `test_indicadores.py` (4), `test_seed_y_persistencia.py` (7), `test_smoke.py` (4).
  - Indicadores con valores calculados a mano (ingresos 342, ticket 114, por categoría X=300 / Y=42) y consistencia con `GET /api/ventas`.
  - Sin ventas → `hay_datos=false`, `ticket_promedio=null` (no se inventa).
  - Seed: 50 ventas, idéntico en dos bases distintas, rangos respetados, no duplica.
  - Persistencia: datos intactos tras cerrar y reabrir el engine sobre archivo.
- Servidor real (`uvicorn` + seed): 8 productos, 50 ventas; `/api/indicadores` → 50 ventas, 143 unidades, ingresos $35.313.570, ticket $706.271,40. Por categoría: Computación $18.209.690 · Telefonía $10.224.690 · Audio $4.899.580 · Accesorios $1.979.610 (suma = total).
- Sin dependencias nuevas. `TestClient` usa `httpx`, que ya instala `google-genai` (dependencia transitiva, no declarada).
- Corrección: la prueba de humo de Fase 1 usaba `route.path`, que falla con routers incluidos en FastAPI 0.162; ahora valida rutas vía OpenAPI.

## Fase 3 — Frontend ✅ (2026-10-28)
- [x] Construir dashboard. — Layout con cabecera, área principal y panel lateral del agente (sticky; pasa abajo en < 1100 px y a una columna en móvil). Modo claro/oscuro por `prefers-color-scheme`.
- [x] Mostrar indicadores y gráficos. — KPI de ingresos totales, unidades vendidas y ticket promedio; gráfico Recharts de ingresos por categoría (barras horizontales, una serie, tooltip, etiquetas de valor y vista "Ver como tabla"); tabla de las 10 ventas más recientes.
- [x] Crear formulario de ventas. — Producto, cantidad y fecha (máx. hoy). Envía solo `producto_id`, `cantidad` y `fecha`; el total mostrado tras guardar es el que devuelve el backend. Muestra errores 422/404 del backend.
- [x] Conectar frontend con backend. — Solo `GET /api/indicadores`, `GET /api/ventas?limit=10`, `GET /api/productos`, `POST /api/ventas` y `GET /api/health`, vía proxy `/api` de Vite. Sin datos simulados. Al registrar una venta se recargan KPI, gráfico y tabla.
- [x] Panel lateral para el futuro agente. — Marcador "Próximamente" con entrada deshabilitada; muestra si la clave de Gemini está configurada (`/api/health`). Sin integración con Gemini.

**Componentes reutilizables** (`frontend/src`): `api.js` (cliente único + mensajes de error), `hooks/useApi.js` (carga/error/recarga), `Panel` (título + estados de carga, error y vacío), `Estados` (`EstadoCarga`, `EstadoError` con "Reintentar", `EstadoVacio`), `KpiCard`, `KpiRow`, `CategoryChart`, `SalesTable`, `SaleForm`, `AgentPanel`, `format.js`.

**Evidencia:**
- `npm run build`: OK, sin advertencias. Corrección: el bundle único pesaba 540 kB (> límite de 500 kB de Vite) → separado por librería; el mayor chunk ahora es recharts con 231 kB.
- Contra el backend del usuario (solo GET, vía proxy de `vite preview`): KPI $35.313.570 · 143 unidades · $706.271,40; coinciden con `/api/indicadores`.
- Backend temporal con base en carpeta temporal (sin tocar `insightdesk.db`): `POST /api/ventas` vía proxy → venta #51, total $1.799.980 con precio tomado del producto; POST con cantidad 0 → 422; tras el POST, el dashboard muestra 51 ventas, $37.113.550 y la venta en la tabla (captura con Edge headless).
- Backend apagado (proxy a puerto vacío): cada panel muestra "El backend no responde…" con botón Reintentar; KPI en "—"; panel del agente "sin conexión".
- Correcciones visuales tras revisar capturas: ticket promedio con 2 decimales ($706.271,40); etiqueta "$2 M" ya no se parte en dos líneas.
- `pytest` backend: 25/25 OK (sin cambios en backend).
- Recharts se mantiene en 2.15.4 (la v3 no fue aprobada). `vite.config.js` acepta `API_TARGET` para apuntar el proxy a otro backend (por defecto `127.0.0.1:8000`).

## Fase 4 — Agente ✅ (2026-10-28)
- [x] Configurar Gemini. — SDK oficial `google-genai` (`app/agente/agente.py`). Clave solo desde `GEMINI_API_KEY` (entorno); modelo `GEMINI_MODEL` (por defecto `gemini-2.5-flash`); `GEMINI_TIMEOUT_S` (30 s) vía `HttpOptions.timeout`, sin reintentos automáticos.
- [x] Implementar herramientas de consulta. — `app/agente/herramientas.py`: `consultar_resumen_ventas`, `consultar_ventas_por_producto` (incluye productos sin ventas y % de participación), `consultar_ventas_por_categoria`. Consultan SQLite con SQLAlchemy a través de `services/indicadores.py` (misma fuente que el dashboard). Lista blanca de nombres, sin parámetros declarados y se rechaza cualquier argumento → no hay vía para SQL arbitrario. Solo lectura.
- [x] Integrar function calling. — Bucle manual (`automatic_function_calling.disable=True`): el modelo propone, el backend valida y ejecuta, el resultado vuelve como `function_response`. Máx. 5 pasos. Instrucciones de sistema: cifras solo de herramientas, declarar faltas de datos (`hay_datos=false`), interpretar y recomendar citando cifras, explicar que no hay filtro por período.
- [x] Crear endpoint de chat. — `POST /api/agente/chat` con Pydantic: `SolicitudChat {mensaje (1..2000), historial (≤ 20 turnos, rol usuario|modelo)}`, `extra="forbid"`; `RespuestaChat {respuesta, herramientas_usadas [nombre, argumentos, resultado], fundamentada}`.
  - Errores → HTTP: sin clave 503 · autenticación (401/403/`API_KEY_INVALID`) 503 · cuota (429/`RESOURCE_EXHAUSTED`) 429 · timeout 504 · modelo inexistente / 5xx / conexión 502 · respuesta vacía o cortada 502 · bloqueo de seguridad 422 · inesperado 500. Mensajes fijos: nunca se reenvía el texto del proveedor; el log registra solo tipo y código.
- [x] Construir interfaz conversacional. — `AgentPanel` habilitado: sugerencias, historial (10 turnos), Enter para enviar, estado "Consultando datos…", errores en burbuja, línea "Datos consultados: …" o aviso "Respuesta sin consulta a datos". `TextoAgente` muestra listas y negritas sin `innerHTML`.

**Evidencia:**
- `pytest`: **71/71 OK** (4,8 s). Nuevo `tests/test_agente.py` (46 casos) con **Gemini simulado** usando los tipos reales del SDK. Sin red ni costo.
  - Herramientas: cifras iguales a `/api/indicadores`; producto sin ventas incluido; `hay_datos=false` con base vacía; nombres fuera de la lista blanca y argumentos (`{"sql": "DELETE…"}`) rechazados sin modificar registros.
  - Bucle: llamada → resultado real de SQLite enviado como `function_response` → respuesta; varias llamadas en un turno; límite de pasos; historial con roles correctos; texto de "pensamiento" oculto.
  - Vacías/bloqueadas: sin candidatos, texto vacío, SAFETY, MAX_TOKENS, prompt bloqueado, `None`.
  - Errores: 401, 403, 400 `API_KEY_INVALID`, 429, 404, 400 genérico, 503, `httpx.ReadTimeout`, `TimeoutError`, `ConnectError`, excepción genérica. La clave nunca aparece en los mensajes, en `/api/health` ni en `/openapi.json`.
  - Endpoint: 503 sin clave, 200 con agente simulado, 7 casos de validación 422.
- Llamada **real** a Gemini con clave inválida: la API devolvió `ClientError 400 (API_KEY_INVALID)` → HTTP 503 "no pudo autenticarse…", sin la clave en el mensaje.
- De punta a punta (backend temporal + base aparte + Gemini simulado, vía proxy de Vite): `/api/health` → `agent_configured: true`; chat → 200, `fundamentada: true`, herramienta `consultar_ventas_por_categoria`, respuesta con Computación $18.209.690 (51,6%); mensaje vacío → 422. Captura con Edge (DevTools): conversación renderizada con negrita, lista y fuentes.
- `npm run build`: OK.
- Sin dependencias nuevas: `httpx` (para detectar timeouts) y `websockets` (solo verificación manual) vienen con `google-genai`.
- **Con clave real (2026-10-28):** `gemini-3.8-flash` y `gemini-3.7-flash` respondían `504 DEADLINE_EXCEEDED` (saturados); `gemini-2.5-flash` ya no existe (404). El agente funciona con `gemini-3.6-flash` (9 s), `gemini-3.5-flash` (9 s) y `gemini-3-flash-preview` (4 s): llama a la herramienta y responde con cifras de SQLite. Se fijó `GEMINI_MODEL=gemini-3.6-flash` en `backend/.env`.
  - Corrección: el 504 `DEADLINE_EXCEEDED` del servidor se mostraba como "servicio no disponible"; ahora devuelve HTTP 504 "tardó demasiado (modelo saturado)". 73/73 pruebas OK.
  - `backend/.env` se carga automáticamente desde `config.py` (sin python-dotenv); las variables del entorno tienen prioridad.

## Fase 5 — Calidad ✅ (2026-11-11)
- [x] Ejecutar pytest. — **74/74 OK** (4,7 s).
- [x] Compilar frontend. — `npm run build` OK, sin advertencias; mayor chunk recharts 231 kB.
- [x] Validar manejo de errores. — Servidor real con base temporal y sin clave: venta válida 201 (precio desde el producto); cantidad 0, `precio_unitario` enviado, fecha futura y JSON roto → 422; producto 999 → 404; nombre duplicado → 409; chat sin clave → 503; ruta inexistente → 404. Log del servidor sin errores.
  - Corrección: con el agente sin clave, un mensaje vacío devolvía 503 en lugar de 422 (la dependencia `get_agente` se resolvía antes que la validación del cuerpo). Ahora `get_agente` entrega un constructor perezoso que se invoca dentro del endpoint. Nueva prueba `test_chat_sin_clave_valida_entrada_primero`.
- [x] Revisar seguridad de secretos. — `.env` y `.env.*` en `.gitignore`; ningún `.env` real en el índice ni en el historial; búsqueda de patrones `AIza…` en código e historial: solo la clave falsa de las pruebas. La clave tiene `repr=False` y no aparece en `/api/health`, `/openapi.json` ni en los mensajes de error (ya probado); el log solo registra tipo y código.
  - Corrección: el modelo por defecto `gemini-2.5-flash` (inexistente, 404) pasa a `gemini-3.6-flash` en `config.py` y `.env.example`. `.env.example` tenía un comentario desactualizado ("no se carga automáticamente") y una `DATABASE_URL` relativa que cambiaba la ubicación de la base según la carpeta de arranque; ahora es opcional y está comentada.
- [x] Documentar ejecución en README. — `README.md`: requisitos, instalación, configuración, ejecución, pruebas, API, códigos de error y agente.

**Pendientes no bloqueantes:** decisión 4 (Recharts 3, sin aprobar) y decisión 5 (texto ajeno al final de spec.md).

## Regla de trabajo
Codex debe implementar una fase a la vez, ejecutar las verificaciones correspondientes y actualizar este plan. No avanzar automáticamente si existen errores sin resolver.
