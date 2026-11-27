// Prueba local de kapso/functions/menu-sin-ia/index.js
import fs from "node:fs";
const code = fs.readFileSync(new URL("../kapso/functions/menu-sin-ia/index.js", import.meta.url), "utf8");
const handler = new Function(`${code}; return handler;`)();
const edges = ["calzado_hombre", "calzado_mujer", "calzado_ninos", "ropa", "accesorios", "ofertas", "ubicacion", "asesor", "menu", "sin_respuesta", "cerrar"];
const msg = (m) => ({ available_edges: edges, whatsapp_context: { conversation: { contact_name: "Juan Pérez" }, messages: [{ direction: "outbound", content: "menu" }, { direction: "inbound", ...m }] } });
const casos = [
  [msg({ content: "Selected: Calzado hombre", reply_option_id: "calzado_hombre" }), "calzado_hombre"],
  [msg({ content: "Selected: Ofertas", reply_option_id: "ofertas" }), "ofertas"],
  [msg({ content: "Selected: Hablar con un asesor", reply_option_id: "asesor" }), "asesor"],
  [msg({ content: "Menú" }), "menu"],
  [msg({ content: "hola buenas tardes" }), "menu"],
  [msg({ content: "tienen las nike air max en 40?" }), "asesor"],
  [msg({ content: "Este en 40 Image attached (image.jpeg) URL: https://x" }), "asesor"],
  [{ available_edges: edges, execution_context: { system: { last_resume: { reason: "timeout" } }, vars: {} } }, "sin_respuesta"],
  [{ available_edges: edges, execution_context: { system: { last_resume: { reason: "timeout" } }, vars: { seguimientos: 1 } } }, "cerrar"],
];
const inicio = (c) => ({ available_edges: ["anuncio", "menu"], whatsapp_context: { messages: [{ direction: "inbound", content: c }] } });
casos.push([inicio("¿Cuáles son los modelos de poleras disponibles?"), "anuncio"], [inicio("¿Me pueden mandar más información de las ofertas disponibles?"), "anuncio"], [inicio("Me pueden mandar mas informacion de las ofretas disponibles?"), "menu"], [inicio("Hola"), "menu"], [inicio("precio de las chinelas"), "menu"]);
let fallas = 0;
for (const [body, esperado] of casos) {
  const j = await (await handler(new Request("http://l", { method: "POST", body: JSON.stringify(body) }))).json();
  const ok = j.next_edge === esperado; if (!ok) fallas++;
  console.log(ok ? "OK   " : "FALLA", esperado.padEnd(15), "→", j.next_edge, j.vars && j.vars.aviso_mensaje ? `| aviso: "${j.vars.aviso_mensaje}" de ${j.vars.cliente_nombre}` : "");
}
process.exit(fallas ? 1 : 0);
