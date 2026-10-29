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

**Decisiones abiertas antes de la Fase 2:**
1. Precio en ventas: propuesta, el backend toma `precio_unitario` del producto en vez de aceptarlo del cliente.
2. Stock: no está en la entidad Producto; propuesta, no agregarlo.
3. `consultar_ventas_por_producto` debe incluir productos sin ventas (para detectar bajo rendimiento).
4. Recharts 2.x está deprecado; propuesta, fijar Recharts 3.
5. spec.md contiene texto ajeno al final (firma y una copia de plan.md); conviene limpiarlo.

## Fase 2 — Datos
- [ ] Crear modelos Producto y Venta.
- [ ] Configurar SQLite.
- [ ] Generar datos de demostración.
- [ ] Implementar endpoints REST.
- [ ] Verificar indicadores con pruebas.

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
