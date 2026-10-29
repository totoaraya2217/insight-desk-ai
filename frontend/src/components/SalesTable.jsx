import Panel from "./Panel.jsx";
import { cantidad, dinero, fecha } from "../format.js";

export default function SalesTable({ estado, limite }) {
  const ventas = estado.data ?? [];
  return (
    <Panel
      titulo="Ventas recientes"
      subtitulo={`Últimas ${limite} por fecha`}
      estado={estado}
      vacio={ventas.length === 0}
      mensajeVacio="No hay ventas registradas."
    >
      <div className="tabla-scroll">
        <table className="tabla">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Producto</th>
              <th className="num">Cant.</th>
              <th className="num">Precio unit.</th>
              <th className="num">Total</th>
            </tr>
          </thead>
          <tbody>
            {ventas.map((v) => (
              <tr key={v.id}>
                <td className="nowrap">{fecha(v.fecha)}</td>
                <td>{v.producto_nombre}</td>
                <td className="num">{cantidad(v.cantidad)}</td>
                <td className="num">{dinero(v.precio_unitario)}</td>
                <td className="num strong">{dinero(v.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
