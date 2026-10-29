import { Bar, BarChart, CartesianGrid, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Panel from "./Panel.jsx";
import { cantidad, dinero, dineroCompacto } from "../format.js";

function TooltipCategoria({ active, payload }) {
  if (!active || !payload?.length) return null;
  const c = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{c.categoria}</strong>
      <span>Ingresos: {dinero(c.ingresos)}</span>
      <span>Unidades: {cantidad(c.cantidad_vendida)}</span>
      <span>Ventas: {cantidad(c.num_ventas)}</span>
    </div>
  );
}

export default function CategoryChart({ estado }) {
  const items = estado.data?.ventas_por_categoria ?? [];
  const alto = Math.max(160, items.length * 52);

  return (
    <Panel
      titulo="Ingresos por categoría"
      subtitulo="Suma de cantidad × precio unitario de todas las ventas"
      estado={estado}
      vacio={items.length === 0}
      mensajeVacio="Aún no hay ventas registradas para graficar."
    >
      <div className="chart" style={{ height: alto }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={items} layout="vertical" margin={{ top: 4, right: 88, bottom: 4, left: 8 }} barCategoryGap={14}>
            <CartesianGrid horizontal={false} stroke="var(--grid)" />
            <XAxis type="number" tickFormatter={dineroCompacto} tick={{ fill: "var(--text-muted)", fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="categoria" width={104} tick={{ fill: "var(--text-secondary)", fontSize: 13 }} axisLine={false} tickLine={false} />
            <Tooltip content={<TooltipCategoria />} cursor={{ fill: "var(--hover)" }} />
            <Bar dataKey="ingresos" className="bar-serie" radius={[0, 4, 4, 0]} maxBarSize={28} isAnimationActive={false}>
              <LabelList dataKey="ingresos" position="right" formatter={dineroCompacto} className="bar-label" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <details className="tabla-alternativa">
        <summary>Ver como tabla</summary>
        <table className="tabla">
          <thead>
            <tr><th>Categoría</th><th className="num">Ventas</th><th className="num">Unidades</th><th className="num">Ingresos</th></tr>
          </thead>
          <tbody>
            {items.map((c) => (
              <tr key={c.categoria}>
                <td>{c.categoria}</td>
                <td className="num">{cantidad(c.num_ventas)}</td>
                <td className="num">{cantidad(c.cantidad_vendida)}</td>
                <td className="num">{dinero(c.ingresos)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </Panel>
  );
}
