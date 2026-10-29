import { useState } from "react";
import { api } from "./api.js";
import { useApi } from "./hooks/useApi.js";
import KpiRow from "./components/KpiRow.jsx";
import CategoryChart from "./components/CategoryChart.jsx";
import SalesTable from "./components/SalesTable.jsx";
import SaleForm from "./components/SaleForm.jsx";
import AgentPanel from "./components/AgentPanel.jsx";

const LIMITE_VENTAS = 10;

export default function App() {
  // Se incrementa tras registrar una venta para recargar indicadores y tabla.
  const [version, setVersion] = useState(0);

  const indicadores = useApi(api.indicadores, [version]);
  const ventas = useApi(() => api.ventas(LIMITE_VENTAS), [version]);
  const productos = useApi(api.productos);
  const health = useApi(api.health);

  return (
    <div className="layout">
      <header className="topbar">
        <div className="brand">
          <span className="logo" aria-hidden>◆</span>
          <span>InsightDesk <strong>AI</strong></span>
        </div>
        <span className="muted pequeno">Panel comercial</span>
      </header>

      <main className="dashboard">
        <KpiRow estado={indicadores} />
        <div className="grid-2">
          <CategoryChart estado={indicadores} />
          <SaleForm productos={productos} onRegistrada={() => setVersion((v) => v + 1)} />
        </div>
        <SalesTable estado={ventas} limite={LIMITE_VENTAS} />
      </main>

      <AgentPanel health={health} />
    </div>
  );
}
