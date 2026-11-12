# InsightDesk AI

Dashboard de ventas con un agente de IA (Gemini) que responde preguntas en lenguaje natural usando solo datos reales de la base.

- **Frontend:** React 18 + Vite + Recharts (`frontend/`)
- **Backend:** FastAPI + SQLAlchemy + SQLite (`backend/`)
- **Agente:** Gemini vía `google-genai`, con function calling sobre 3 herramientas de solo lectura

El navegador nunca habla con Gemini: todo pasa por el backend, que guarda la clave.

## Requisitos

- Python 3.12 o superior (probado con 3.14)
- Node.js 20 o superior (probado con 26)
- Una clave de Gemini ([Google AI Studio](https://aistudio.google.com/apikey)). Es opcional: sin clave funciona todo excepto el chat.

## Instalación

Desde la raíz del repositorio:

```powershell
# Backend
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
pip install -r backend/requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

## Configuración

Copia `backend/.env.example` a `backend/.env` y completa la clave:

```ini
GEMINI_API_KEY=tu-clave
GEMINI_MODEL=gemini-3.6-flash
GEMINI_TIMEOUT_S=30
```

`backend/app/config.py` carga ese archivo automáticamente. Si una variable ya está definida en el entorno, tiene prioridad sobre el archivo. `backend/.env` está en `.gitignore`: **nunca lo subas al repositorio**.

| Variable | Por defecto | Uso |
|---|---|---|
| `GEMINI_API_KEY` | (vacía) | Sin clave, `POST /api/agente/chat` responde 503 y el panel lo indica. |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Modelo de Gemini. |
| `GEMINI_TIMEOUT_S` | `30` | Tiempo máximo por llamada a Gemini. |
| `DATABASE_URL` | `backend/insightdesk.db` | Ruta de SQLite. |

## Ejecución

Usa dos terminales, ambas desde la raíz:

```powershell
# 1) Backend → http://127.0.0.1:8000  (documentación en /docs)
cd backend
..\.venv\Scripts\python -m app.seed          # solo la primera vez: 8 productos y 50 ventas de demostración
..\.venv\Scripts\python -m uvicorn app.main:app --reload
```

```powershell
# 2) Frontend → http://localhost:5173
cd frontend
npm run dev
```

Vite reenvía `/api` al backend. Para apuntar a otro backend, usa `API_TARGET=http://host:puerto`.

`python -m app.seed --reset` borra la base y regenera los datos de demostración. Los datos son deterministas (semilla 42).

## Pruebas y compilación

```powershell
cd backend;  ..\.venv\Scripts\python -m pytest -q     # 74 pruebas; Gemini simulado, sin red ni costo
cd frontend; npm run build                            # genera frontend/dist
```

## API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/health` | Estado y si el agente tiene clave (nunca la expone) |
| GET / POST | `/api/productos` | Listar / crear producto (409 si el nombre ya existe) |
| GET / POST | `/api/ventas` | Listar (`?limit=`) / registrar venta. El precio lo pone el backend. |
| GET | `/api/indicadores` | Ingresos, unidades, ticket promedio y ventas por categoría |
| POST | `/api/agente/chat` | `{mensaje, historial}` → `{respuesta, herramientas_usadas, fundamentada}` |

Códigos de error: 422 entrada inválida · 404 producto inexistente · 409 duplicado · 503 agente sin clave o clave inválida · 429 cuota de Gemini agotada · 504 Gemini tardó demasiado · 502 fallo o respuesta vacía de Gemini. Los mensajes son fijos y nunca reenvían el texto del proveedor ni la clave.

## Agente

Herramientas (solo lectura, sin parámetros, en lista blanca): `consultar_resumen_ventas`, `consultar_ventas_por_producto` y `consultar_ventas_por_categoria`. Usan las mismas consultas que el dashboard. El modelo no puede ejecutar SQL ni modificar registros. Cada pregunta permite como máximo 5 rondas de herramientas. Si no hay datos, el agente lo dice en vez de inventar cifras.

Detalles de diseño y evidencia de cada fase: [`plan.md`](plan.md). Requisitos: [`intent.md`](intent.md) y [`spec.md`](spec.md).
