// Prueba local de kapso/functions/filtro-numeros/index.js
// Uso: node tests/probar_filtro_numeros.mjs
import fs from "node:fs";
const code = fs.readFileSync(new URL("../kapso/functions/filtro-numeros/index.js", import.meta.url), "utf8");
const handler = new Function(`${code}; return handler;`)();
const casos = [
  [{ whatsapp_context: { conversation: { phone_number: "+59177213515" } } }, "autorizado"],
  [{ whatsapp_context: { conversation: { phone_number: "59172181658" } } }, "autorizado"],
  [{ execution_context: { context: { phone_number: "+591 7218-1658" } } }, "autorizado"],
  [{ whatsapp_context: { conversation: { phone_number: "+59170000000" } } }, "no_autorizado"],
  [{ whatsapp_context: { conversation: { phone_number: "+5677213515" } } }, "no_autorizado"],
  [{ whatsapp_context: { conversation: { phone_number: "+5917721351599" } } }, "no_autorizado"],
  [{}, "no_autorizado"],
];
let fallas = 0;
for (const [body, esperado] of casos) {
  const r = await handler(new Request("http://local", { method: "POST", body: JSON.stringify(body) }));
  const j = await r.json();
  const ok = j.next_edge === esperado;
  if (!ok) fallas++;
  console.log(ok ? "OK   " : "FALLA", JSON.stringify(body).slice(0, 80), "→", j.next_edge);
}
process.exit(fallas ? 1 : 0);
