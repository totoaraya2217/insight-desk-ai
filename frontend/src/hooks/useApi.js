import { useCallback, useEffect, useState } from "react";

/**
 * Ejecuta una función del cliente API y expone { data, error, loading, reload }.
 * `deps` controla cuándo se vuelve a pedir (p. ej. un contador de versión tras registrar una venta).
 */
export function useApi(fn, deps = []) {
  const [state, setState] = useState({ data: null, error: null, loading: true });

  const load = useCallback(fn, deps);

  const reload = useCallback(() => {
    let vigente = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    load()
      .then((data) => vigente && setState({ data, error: null, loading: false }))
      .catch((error) => vigente && setState((s) => ({ data: s.data, error, loading: false })));
    return () => {
      vigente = false;
    };
  }, [load]);

  useEffect(reload, [reload]);

  return { ...state, reload };
}
