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

## Fase 3 — Frontend
- [ ] Construir dashboard.
- [ ] Mostrar indicadores y gráficos.
- [ ] Crear formulario de ventas.
- [ ] Conectar frontend con backend.

## Fase 4 — Agente
- [ ] Configurar Gemini.
- [ ] Implementar herramientas de consulta.
- [ ] Integrar function calling.
- [ ] Crear endpoint de chat.
- [ ] Construir interfaz conversacional.

## Fase 5 — Calidad
- [ ] Ejecutar pytest.
- [ ] Compilar frontend.
- [ ] Validar manejo de errores.
- [ ] Revisar seguridad de secretos.
- [ ] Documentar ejecución en README.

## Regla de trabajo
Codex debe implementar una fase a la vez, ejecutar las verificaciones correspondientes y actualizar este plan. No avanzar automáticamente si existen errores sin resolver.
