export default function KpiCard({ etiqueta, valor, detalle, loading, error }) {
  return (
    <article className="kpi" aria-busy={loading || undefined}>
      <span className="kpi-label">{etiqueta}</span>
      {loading ? (
        <span className="kpi-value skeleton" aria-label="Cargando" />
      ) : error ? (
        <span className="kpi-value kpi-error" title={error.message}>—</span>
      ) : (
        <span className="kpi-value">{valor}</span>
      )}
      {detalle && !loading && !error && <span className="kpi-detail muted">{detalle}</span>}
    </article>
  );
}
