import KpiCard from "./KpiCard.jsx";
import { EstadoError } from "./Estados.jsx";
import { cantidad, dinero } from "../format.js";

export default function KpiRow({ estado }) {
  const { data, error, loading, reload } = estado;
  const cargando = loading && !data;
  const fallo = error && !data ? error : null;
  const sinVentas = data && !data.hay_datos;

  return (
    <div className="kpi-block">
      <div className="kpi-row">
        <KpiCard
          etiqueta="Ingresos totales"
          valor={dinero(data?.ingresos)}
          detalle={data && `${cantidad(data.num_ventas)} ventas registradas`}
          loading={cargando}
          error={fallo}
        />
        <KpiCard
          etiqueta="Unidades vendidas"
          valor={cantidad(data?.cantidad_vendida)}
          detalle={data && `en ${data.ventas_por_categoria.length} categorías`}
          loading={cargando}
          error={fallo}
        />
        <KpiCard
          etiqueta="Ticket promedio"
          valor={dinero(data?.ticket_promedio)}
          detalle={sinVentas ? "Sin ventas para calcular" : "Ingresos / n.º de ventas"}
          loading={cargando}
          error={fallo}
        />
      </div>
      {fallo && <EstadoError mensaje={`No se pudieron cargar los indicadores: ${fallo.message}`} onReintentar={reload} />}
    </div>
  );
}
