import { EstadoCarga, EstadoError, EstadoVacio } from "./Estados.jsx";

/**
 * Contenedor reutilizable con título y manejo uniforme de carga, error y vacío.
 * Mientras recarga con datos previos, los mantiene visibles (sin parpadeo).
 */
export default function Panel({ titulo, subtitulo, acciones, estado, vacio, mensajeVacio, children, className = "" }) {
  let cuerpo = children;
  if (estado) {
    const { data, error, loading, reload } = estado;
    if (error && !data) cuerpo = <EstadoError mensaje={error.message} onReintentar={reload} />;
    else if (loading && !data) cuerpo = <EstadoCarga />;
    else if (vacio) cuerpo = <EstadoVacio mensaje={mensajeVacio} />;
  }

  return (
    <section className={`panel ${className}`} aria-busy={estado?.loading || undefined}>
      {(titulo || acciones) && (
        <header className="panel-header">
          <div>
            {titulo && <h2>{titulo}</h2>}
            {subtitulo && <p className="muted">{subtitulo}</p>}
          </div>
          {acciones}
        </header>
      )}
      {cuerpo}
    </section>
  );
}
