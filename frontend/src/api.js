// Único punto de acceso al backend. Todas las rutas pasan por el proxy /api de Vite.

export class ApiError extends Error {}

function mensajeDeError(status, data) {
  if (Array.isArray(data?.detail)) {
    // Errores de validación de Pydantic (422): "campo: mensaje".
    return data.detail.map((d) => `${d.loc?.at(-1) ?? "dato"}: ${d.msg}`).join(" · ");
  }
  if (typeof data?.detail === "string") return data.detail;
  if (status >= 500) return "El backend no responde. Verifica que uvicorn esté en ejecución.";
  return `Error inesperado (${status}).`;
}

async function request(path, { method = "GET", body, params } = {}) {
  const qs = params ? `?${new URLSearchParams(params)}` : "";
  let res;
  try {
    res = await fetch(`/api${path}${qs}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("No se pudo conectar con el backend.");
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(mensajeDeError(res.status, data));
  return data;
}

export const api = {
  health: () => request("/health"),
  productos: () => request("/productos"),
  ventas: (limit = 10) => request("/ventas", { params: { limit } }),
  crearVenta: (venta) => request("/ventas", { method: "POST", body: venta }),
  indicadores: () => request("/indicadores"),
};
