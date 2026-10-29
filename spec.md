# spec.md — Especificación técnica

## Stack
- Frontend: React con Vite.
- Backend: Python con FastAPI.
- Base de datos: SQLite y SQLAlchemy.
- Agente: Gemini mediante google-genai.
- Visualización: Recharts.
- Pruebas: pytest y pruebas de compilación del frontend.

## Entidades
Producto: id, nombre, categoría, precio.

Venta: id, producto_id, cantidad, precio_unitario, fecha.

## Endpoints
- GET /api/productos
- POST /api/productos
- GET /api/ventas
- POST /api/ventas
- GET /api/indicadores
- POST /api/agente/chat

## Funcionalidades del agente
El agente debe disponer de herramientas de solo lectura:
- consultar_resumen_ventas()
- consultar_ventas_por_producto()
- consultar_ventas_por_categoria()

El agente podrá decidir qué herramienta utilizar según la pregunta del usuario.

## Reglas
- El navegador nunca accede directamente a Gemini.
- El backend valida los datos recibidos.
- Las consultas utilizan SQLAlchemy.
- El agente no ejecuta SQL arbitrario.
- Las herramientas no modifican registros.
- Las respuestas numéricas deben basarse en resultados de las herramientas.
- Las claves se almacenan en variables de entorno.

## Criterios de aceptación
- Los endpoints responden con JSON válido.
- Las ventas registradas persisten al reiniciar.
- El dashboard presenta los indicadores correctos.
- El agente puede responder preguntas utilizando herramientas.
- Los errores de Gemini se manejan sin exponer secretos.
- Existen pruebas automatizadas para las operaciones principales.

Jorge Ariel Bermúdez Tellería
20:00
# plan.md — Plan de implementación

## Fase 1 — Inicialización
- [ ] Crear frontend React + Vite.
- [ ] Crear backend FastAPI.
- [ ] Configurar Git y .gitignore.
- [ ] Instalar dependencias autorizadas.

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