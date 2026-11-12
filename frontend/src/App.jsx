import { useDashboardData, LIMITE_VENTAS } from "./hooks/useDashboardData.js";
import KpiRow from "./components/KpiRow.jsx";
import CategoryChart from "./components/CategoryChart.jsx";
import SalesTable from "./components/SalesTable.jsx";
import SaleForm from "./components/SaleForm.jsx";
import AgentPanel from "./components/AgentPanel.jsx";

export default function App() {
  const { indicadores, ventas, productos, health, actualizarVentas } = useDashboardData();

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
          <SaleForm productos={productos} onRegistrada={actualizarVentas} />
        </div>
        <SalesTable estado={ventas} limite={LIMITE_VENTAS} />
      </main>

      <AgentPanel health={health} />
    </div>
  );
}
