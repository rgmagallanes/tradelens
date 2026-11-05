import './journalGalaxy.css';
import './tradingDashboard.css';
import './journalGraph.css';
import './journal.css';
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import QueryScope from './QueryScope.jsx';
import HostedGate from "./HostedGate.jsx";
const hosted=import.meta.env.VITE_HOSTED==='true';
import "./styles.css";
import "./ambient.css";
import "./panelMotion.css";
import "./navigation.css";
import "./lightTheme.css";
import "./marketNews.css";
try{document.documentElement.dataset.theme=localStorage.getItem("tradelens.theme")==="light"?"light":"dark"}catch{document.documentElement.dataset.theme="dark"}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {hosted?<HostedGate><App/></HostedGate>:<QueryScope><App/></QueryScope>}
  </React.StrictMode>,
);
