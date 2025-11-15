import React from "react";
import ReactDOM from "react-dom/client";
import App from "./app";              // <-- THIS MUST BE RELATIVE



ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
