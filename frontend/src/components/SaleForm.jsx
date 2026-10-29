import { useState } from "react";
import Panel from "./Panel.jsx";
import { api } from "../api.js";
import { dinero, hoyISO } from "../format.js";

const INICIAL = { producto_id: "", cantidad: 1, fecha: hoyISO() };

export default function SaleForm({ productos, onRegistrada }) {
  const [form, setForm] = useState(INICIAL);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(null);

  const lista = productos.data ?? [];
  const seleccionado = lista.find((p) => String(p.id) === form.producto_id);
  const cambiar = (campo) => (e) => {
    setForm((f) => ({ ...f, [campo]: e.target.value }));
    setExito(null);
  };

  async function enviar(e) {
    e.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      // Solo se envían producto, cantidad y fecha: el precio lo fija el backend.
      const venta = await api.crearVenta({
        producto_id: Number(form.producto_id),
        cantidad: Number(form.cantidad),
        fecha: form.fecha,
      });
      setExito(`Venta #${venta.id} registrada: ${venta.cantidad} × ${venta.producto_nombre} = ${dinero(venta.total)}`);
      setForm({ ...INICIAL, fecha: form.fecha });
      onRegistrada();
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Panel
      titulo="Registrar venta"
      estado={productos}
      vacio={lista.length === 0}
      mensajeVacio="No hay productos registrados. Ejecuta el seed o crea productos vía API."
    >
      <form className="form" onSubmit={enviar}>
        <label className="campo">
          <span>Producto</span>
          <select value={form.producto_id} onChange={cambiar("producto_id")} required>
            <option value="" disabled>Selecciona un producto…</option>
            {lista.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nombre} · {dinero(p.precio)}
              </option>
            ))}
          </select>
        </label>
        <div className="campo-fila">
          <label className="campo">
            <span>Cantidad</span>
            <input type="number" min="1" max="10000" step="1" value={form.cantidad} onChange={cambiar("cantidad")} required />
          </label>
          <label className="campo">
            <span>Fecha</span>
            <input type="date" max={hoyISO()} value={form.fecha} onChange={cambiar("fecha")} required />
          </label>
        </div>
        <p className="muted pequeno">
          {seleccionado
            ? `Total referencial: ${dinero(seleccionado.precio * Number(form.cantidad || 0))} (el backend confirma el monto final)`
            : "El precio unitario se toma del producto en el backend."}
        </p>
        {error && <p className="aviso aviso-error" role="alert">{error}</p>}
        {exito && <p className="aviso aviso-ok" role="status">{exito}</p>}
        <button type="submit" className="btn btn-primary" disabled={enviando || !form.producto_id}>
          {enviando ? "Registrando…" : "Registrar venta"}
        </button>
      </form>
    </Panel>
  );
}
