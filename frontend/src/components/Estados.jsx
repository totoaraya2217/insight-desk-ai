export function EstadoCarga({ texto = "Cargando…" }) {
  return (
    <div className="estado" role="status">
      <span className="spinner" aria-hidden /> {texto}
    </div>
  );
}

export function EstadoError({ mensaje, onReintentar }) {
  return (
    <div className="estado estado-error" role="alert">
      <span aria-hidden>⚠</span>
      <span>{mensaje}</span>
      {onReintentar && (
        <button type="button" className="btn btn-ghost" onClick={onReintentar}>
          Reintentar
        </button>
      )}
    </div>
  );
}

export function EstadoVacio({ mensaje = "Sin datos registrados." }) {
  return <div className="estado muted">{mensaje}</div>;
}
