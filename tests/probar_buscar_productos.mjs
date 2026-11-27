// Prueba local de kapso/functions/buscar-productos/index.js contra la web real.
// Uso: node tests/probar_buscar_productos.mjs
// (detrás de un proxy: NODE_USE_ENV_PROXY=1 node tests/probar_buscar_productos.mjs)
import fs from "node:fs";
const code = fs.readFileSync(new URL("../kapso/functions/buscar-productos/index.js", import.meta.url), "utf8");
const handler = new Function(`${code}; return handler;`)();
const casos = [
  [{ marca: "nike", familia: "zapatillas", genero: "mujer" }, true],
  [{ marca: "puma", familia: "chuteras", genero: "niños" }, false], // no existe exacto: debe sugerir chuteras de niño
  [{ familia: "muñequeras" }, true],
  [{ marca: "new balance", familia: "zapatillas" }, true],
  [{ marca: "nike", buscar: "air max" }, true],
  [{ grupo: "basquet", familia: "pelotas" }, true],
  [{ familia: "zapatillas", precio_max: 100 }, true],
  [{ familia: "zapatillas", precio_min: 100, precio_max: 150 }, true],
];
let fallas = 0;
for (const [input, exactoEsperado] of casos) {
  const r = await handler(new Request("http://local", { method: "POST", body: JSON.stringify({ input }) }));
  const j = await r.json();
  const precioOk = j.productos.every((p) => {
    const v = parseFloat(p.precio_oferta_bs || p.precio_normal_bs);
    return (!input.precio_max || v <= input.precio_max) && (!input.precio_min || v >= input.precio_min);
  });
  const ok = j.hay_productos && j.exacto === exactoEsperado && precioOk && j.productos.every((p) => p.enlace.includes("codigo="));
  if (!ok) fallas++;
  console.log(ok ? "OK   " : "FALLA", JSON.stringify(input), "→", j.total_en_pagina, "productos", j.filtros_quitados.length ? `(quitó ${j.filtros_quitados})` : "", "|", j.productos[0]?.nombre ?? "-");
}
// Detalle por código: nombre, precios, colores y tallas
for (const codigo of ["14771", "14810"]) {
  const j = await (await handler(new Request("http://local", { method: "POST", body: JSON.stringify({ input: { codigo } }) }))).json();
  const m = j.modelo;
  const ok = m.encontrado && m.nombre && m.colores.length && m.colores.every((c) => c.tallas.length);
  if (!ok) fallas++;
  console.log(ok ? "OK   " : "FALLA", "codigo", codigo, "→", m.nombre, JSON.stringify(m.colores.map((c) => [c.color, c.tallas])));
}
process.exit(fallas ? 1 : 0);
