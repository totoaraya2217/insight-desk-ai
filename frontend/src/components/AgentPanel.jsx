// Espacio reservado para el asistente de IA. La integración con Gemini llega en la Fase 4.
export default function AgentPanel({ health }) {
  const configurado = health.data?.agent_configured;

  return (
    <aside className="agent-panel" aria-label="Asistente de IA">
      <header className="panel-header">
        <div>
          <h2>Asistente IA</h2>
          <p className="muted">Consultas en lenguaje natural sobre tus ventas</p>
        </div>
        <span className="badge">Próximamente</span>
      </header>

      <div className="agent-body">
        <p>Aquí podrás preguntar, por ejemplo:</p>
        <ul className="sugerencias">
          <li>¿Cuál fue la categoría con más ingresos?</li>
          <li>¿Cuál es el ticket promedio?</li>
          <li>¿Qué productos venden menos?</li>
        </ul>
        <p className="muted pequeno">
          Estado del backend:{" "}
          {health.loading && !health.data
            ? "verificando…"
            : health.error
              ? "sin conexión"
              : configurado
                ? "clave de Gemini configurada"
                : "clave de Gemini no configurada"}
        </p>
      </div>

      <form className="agent-input" onSubmit={(e) => e.preventDefault()}>
        <textarea rows={2} placeholder="El asistente se habilitará en la Fase 4" disabled aria-label="Pregunta al asistente" />
        <button type="submit" className="btn btn-primary" disabled>
          Enviar
        </button>
      </form>
    </aside>
  );
}
