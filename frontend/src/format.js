const numero = new Intl.NumberFormat("es-CL", { maximumFractionDigits: 2 });
const conDecimales = new Intl.NumberFormat("es-CL", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fechaCorta = new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" });

const vacio = (v) => v === null || v === undefined;

// Montos enteros sin decimales ($35.313.570); los demás siempre con dos ($706.271,40).
export const dinero = (v) => (vacio(v) ? "—" : `$${(Number.isInteger(v) ? numero : conDecimales).format(v)}`);
export const cantidad = (v) => (vacio(v) ? "—" : numero.format(v));
// Las fechas llegan como "YYYY-MM-DD"; se formatean en UTC para no correrse un día.
export const fecha = (iso) => (iso ? fechaCorta.format(new Date(`${iso}T00:00:00Z`)) : "—");

export function hoyISO() {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

// Etiqueta compacta para ejes: $18,2 M, $950 mil. Espacio no separable para que Recharts no la parta.
export function dineroCompacto(v) {
  if (Math.abs(v) >= 1e6) return `$${numero.format(Math.round(v / 1e5) / 10)} M`;
  if (Math.abs(v) >= 1e3) return `$${numero.format(Math.round(v / 1e3))} mil`;
  return dinero(v);
}
