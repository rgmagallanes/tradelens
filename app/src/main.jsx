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

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {hosted?<HostedGate><App initialTab="Journal"/></HostedGate>:<QueryScope><App/></QueryScope>}
  </React.StrictMode>,
);
