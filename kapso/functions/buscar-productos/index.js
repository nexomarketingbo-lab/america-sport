// Herramienta del agente America Sport: busca productos en americasportbolivia.com.
// Recibe filtros (marca, familia, grupo, genero, tipo, oferta, buscar), arma el enlace
// con la codificación correcta, cuenta los productos y devuelve los primeros modelos.
// Si no hay productos, quita filtros de a uno para sugerir una sección parecida.

const BASE = "https://americasportbolivia.com/index.php";
const MAX_PRODUCTOS = 8;
const ORDEN_RELAJAR = ["grupo", "genero", "marca", "tipo", "oferta", "pmin", "pmax"]; // "familia" se conserva; el precio se quita al final

function normalizar(campo, valor) {
  if (valor === undefined || valor === null || valor === "" || valor === false) return null;
  if (campo === "oferta") return "1";
  if (campo === "pmin" || campo === "pmax") {
    const n = parseFloat(String(valor).replace(",", ".").replace(/[^\d.]/g, ""));
    return Number.isFinite(n) && n > 0 ? String(Math.round(n)) : null;
  }
  let v = String(valor).trim().toUpperCase()
    .normalize("NFD").replace(/[̀-̂̄-ͯ]/g, "").normalize("NFC");
  if (campo === "genero") {
    if (/^NI(Ñ|N|¥)?(O|A)S?$/.test(v) || v.startsWith("NI")) return "NI¥OS";
    if (v.includes("UNISEX") || v.includes("/")) return "HOMBRE/MUJER";
    if (v.startsWith("MUJER") || v.startsWith("DAMA")) return "MUJER";
    if (v.startsWith("HOMBRE") || v.startsWith("VARON")) return "HOMBRE";
  }
  return v.replace(/Ñ/g, "¥");
}

function armarEnlace(filtros) {
  const partes = Object.entries(filtros).map(([k, v]) => `${k}=${encodeURIComponent(v).replace(/%2F/g, "/")}`);
  return partes.length ? `${BASE}?${partes.join("&")}` : BASE;
}

function limpiar(html) {
  return html.replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/\s+/g, " ").trim();
}

function extraerProductos(html) {
  const productos = new Map();
  const re = /<a href="index\.php\?codigo=(\d+)"[^>]*>\s*<div class="w3-display-container">\s*<img src="([^"]+)" alt="([^"]*)"[\s\S]*?<strong>([\s\S]*?)<\/strong>/g;
  let m;
  while ((m = re.exec(html))) {
    const [, codigo, img, nombre, preciosHtml] = m;
    if (productos.has(codigo)) continue;
    const precios = limpiar(preciosHtml);
    const normal = (precios.match(/PRECIO NORMAL:\s*([\d.,]+)/) || [])[1] || null;
    const oferta = (precios.match(/PRECIO OFERTA:\s*([\d.,]+)/) || [])[1] || null;
    productos.set(codigo, {
      codigo,
      nombre: nombre.trim(),
      enlace: `${BASE}?codigo=${codigo}`,
      precio_normal_bs: normal,
      precio_oferta_bs: oferta,
      imagen: `https://americasportbolivia.com/${img.replace(/^\//, "")}`,
    });
  }
  return [...productos.values()];
}

async function consultar(filtros) {
  const enlace = armarEnlace(filtros);
  for (let intento = 0; intento < 3; intento++) {
    try {
      const r = await fetch(enlace, { headers: { "User-Agent": "Mozilla/5.0 (AmericaSportBot)" } });
      const html = await r.text();
      const productos = extraerProductos(html);
      // La web a veces responde vacía bajo carga: reintentar antes de concluir que no hay productos.
      if (productos.length || intento === 2) return { enlace, productos };
    } catch (e) {
      if (intento === 2) return { enlace, productos: [], error: String(e) };
    }
    await new Promise((res) => setTimeout(res, 800));
  }
}


// Detalle de un modelo por código: nombre, precios, colores y tallas disponibles por color.
async function obtenerHtml(url) {
  for (let intento = 0; intento < 3; intento++) {
    try {
      const r = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0 (AmericaSportBot)" } });
      const html = await r.text();
      if (html.includes("Talla") || intento === 2) return html;
    } catch (e) {
      if (intento === 2) throw e;
    }
    await new Promise((res) => setTimeout(res, 800));
  }
}

function tallasDe(html) {
  const tallas = [];
  const re = /index\.php\?codigo=\d+&color=[^&"]*&talla=([^"&]+)"/g;
  let m;
  while ((m = re.exec(html))) if (!tallas.includes(m[1])) tallas.push(decodeURIComponent(m[1]));
  return tallas;
}

async function detalleProducto(codigo) {
  const enlace = `${BASE}?codigo=${codigo}`;
  const html = await obtenerHtml(enlace);
  const nombre = ((html.match(/<h4>([^<]+)<\/h4>/) || [])[1] || "").trim();
  if (!nombre) return { encontrado: false, enlace };
  const dato = (etq) => ((html.match(new RegExp(`<strong>${etq}:</strong>\\s*([^<]+)<`)) || [])[1] || "").trim() || null;
  const normal = (html.match(/Precio Normal:<\/strong>\s*(?:<span[^>]*>)?\s*([\d.,]+)/) || [])[1] || null;
  const oferta = (html.match(/Precio Oferta:<\/strong>\s*([\d.,]+)/) || [])[1] || null;
  const colores = [];
  const reColor = /index\.php\?codigo=\d+&color=([^"&]+)" title="([^"]*)"/g;
  let m;
  while ((m = reColor.exec(html))) if (!colores.find((c) => c.color === m[1])) colores.push({ color: m[1] });
  // Las tallas dependen del color: se consulta la página de cada color (máx. 5).
  for (const c of colores.slice(0, 5)) {
    try {
      const h = colores.length === 1 ? html : await obtenerHtml(`${enlace}&color=${encodeURIComponent(c.color)}`);
      c.tallas = tallasDe(h);
      c.enlace = `${enlace}&color=${encodeURIComponent(c.color)}`;
      c.imagen = `https://americasportbolivia.com/imagenes/${codigo}-${c.color}.jpg`;
    } catch (_) { c.tallas = []; }
  }
  return {
    encontrado: true, codigo, nombre, enlace,
    marca: dato("Marca"), familia: dato("Familia"), deporte: dato("Deporte"), genero: dato("Genero"),
    precio_normal_bs: normal, precio_oferta_bs: oferta,
    imagen: `https://americasportbolivia.com/imagenes/${codigo}.jpg`,
    colores,
    nota: "Tallas y colores según la página web; el stock real lo confirma el encargado.",
  };
}

async function handler(request, env) {
  let body = {};
  try { body = await request.json(); } catch (_) {}
  const input = body.input || body || {};

  if (input.codigo) {
    const codigo = String(input.codigo).replace(/\D/g, "");
    const det = await detalleProducto(codigo).catch((e) => ({ encontrado: false, error: String(e) }));
    return new Response(JSON.stringify({ modelo: det }), { headers: { "Content-Type": "application/json" } });
  }

  const filtros = {};
  const entrada = { ...input, pmin: input.precio_min, pmax: input.precio_max };
  for (const campo of ["tipo", "familia", "grupo", "marca", "genero", "oferta", "pmin", "pmax"]) {
    const v = normalizar(campo, entrada[campo]);
    if (v) filtros[campo] = v;
  }
  const buscar = input.buscar ? String(input.buscar).trim().toUpperCase() : null;

  // Si no hay productos, probar quitando la menor cantidad de filtros posible
  // (primero 1, luego 2...), en orden de preferencia. "familia" se conserva.
  let actual = { ...filtros };
  let quitados = [];
  let res = await consultar(actual);
  const relajables = ORDEN_RELAJAR.filter((c) => c in filtros);
  const combinaciones = (arr, k) => k === 0 ? [[]] : arr.flatMap((x, i) => combinaciones(arr.slice(i + 1), k - 1).map((r) => [x, ...r]));
  let consultas = 1;
  for (let k = 1; res.productos.length === 0 && k <= relajables.length && consultas < 8; k++) {
    for (const quitar of combinaciones(relajables, k)) {
      const prueba = { ...filtros };
      quitar.forEach((c) => delete prueba[c]);
      if (!Object.keys(prueba).length) continue;
      const r = await consultar(prueba);
      consultas++;
      if (r.productos.length) { res = r; actual = prueba; quitados = quitar.map((c) => `${c}=${filtros[c]}`); break; }
      if (consultas >= 8) break;
    }
  }

  let productos = res.productos;
  let coincidencias_texto = null;
  if (buscar && productos.length) {
    const palabras = buscar.split(/\s+/).filter((p) => p.length > 1);
    const filtrados = productos.filter((p) => palabras.every((w) => p.nombre.toUpperCase().includes(w)));
    coincidencias_texto = filtrados.length;
    if (filtrados.length) productos = filtrados;
  }

  const salida = {
    enlace_seccion: res.enlace,
    hay_productos: productos.length > 0,
    exacto: quitados.length === 0,
    filtros_pedidos: filtros,
    filtros_usados: actual,
    filtros_quitados: quitados,
    total_en_pagina: res.productos.length,
    coincidencias_texto,
    productos: productos.slice(0, MAX_PRODUCTOS),
    nota: quitados.length
      ? "No hubo productos con todos los filtros; se quitaron algunos. Avisa al cliente que no hay ese modelo exacto y ofrece estas opciones."
      : "Resultados de la primera página de la sección.",
  };
  if (res.error) salida.error = res.error;
  return new Response(JSON.stringify(salida), { headers: { "Content-Type": "application/json" } });
}

