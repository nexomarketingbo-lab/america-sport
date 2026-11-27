// Prueba local de kapso/functions/ruta-conversacion/index.js
import fs from "node:fs";
const code = fs.readFileSync(new URL("../kapso/functions/ruta-conversacion/index.js", import.meta.url), "utf8");
const handler = new Function(`${code}; return handler;`)();
const casos = [
  [{ available_edges: ["pedido", "esperar"], execution_context: { vars: { siguiente: "pedido" } } }, "pedido"],
  [{ available_edges: ["pedido", "esperar"], execution_context: { vars: { siguiente: "esperar" } } }, "esperar"],
  [{ available_edges: ["pedido", "esperar"], execution_context: { vars: {} } }, "esperar"],
  [{ available_edges: ["pedido", "esperar", "consulta"], execution_context: { vars: { siguiente: "consulta" } } }, "consulta"],
  [{ available_edges: ["pedido", "esperar"], execution_context: { vars: { siguiente: "consulta" } } }, "esperar"],
  [{ available_edges: ["respondio", "sin_respuesta"], execution_context: { system: { last_resume: { reason: "timeout" } } } }, "sin_respuesta"],
  [{ available_edges: ["respondio", "sin_respuesta"], execution_context: { system: { last_resume: { reason: "user_input" } } } }, "respondio"],
];
let fallas = 0;
for (const [body, esperado] of casos) {
  const j = await (await handler(new Request("http://l", { method: "POST", body: JSON.stringify(body) }))).json();
  const ok = j.next_edge === esperado; if (!ok) fallas++;
  console.log(ok ? "OK   " : "FALLA", JSON.stringify(body).slice(0, 90), "→", j.next_edge);
}
process.exit(fallas ? 1 : 0);
