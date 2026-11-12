import { useCallback, useState } from "react";
import { api } from "../api.js";
import { useApi } from "./useApi.js";

export const LIMITE_VENTAS = 10;

/**
 * Reúne las consultas del dashboard en un solo lugar.
 * `actualizarVentas` incrementa `version`, lo que vuelve a pedir indicadores y ventas recientes.
 * Productos y estado del backend se cargan una sola vez.
 */
export function useDashboardData() {
  const [version, setVersion] = useState(0);

  const indicadores = useApi(api.indicadores, [version]);
  const ventas = useApi(() => api.ventas(LIMITE_VENTAS), [version]);
  const productos = useApi(api.productos);
  const health = useApi(api.health);

  const actualizarVentas = useCallback(() => setVersion((v) => v + 1), []);

  return { indicadores, ventas, productos, health, actualizarVentas };
}
