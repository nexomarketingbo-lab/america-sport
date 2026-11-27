// Router del bot SIN IA de America Sport (nodo "decide" en modo función). No usa créditos de IA.
// - Opción del menú tocada (reply_option_id) → esa sección.
// - "menú", "hola", "inicio"… → volver a mostrar el menú.
// - Cualquier otra cosa (texto, foto, audio, enlace) → "asesor": avisa al encargado y pasa a humano.
// - Sin respuesta (timeout de la espera) → un seguimiento; si ya hubo uno → "cerrar".

const OPCIONES = ["calzado_hombre", "calzado_mujer", "calzado_ninos", "ropa", "accesorios", "ofertas", "ubicacion", "asesor"];
const VOLVER_AL_MENU = /^(men[uú]|hola|holi|buenas|buen[oa]s (d[ií]as|tardes|noches)|inicio|opciones|volver)(?=$|[\s!.,?¡¿])/iu;

function limpiar(texto) {
  // Meta no acepta saltos de línea, tabs ni más de 4 espacios seguidos en los parámetros de plantilla.
  return String(texto || "")
    .replace(/Image attached[^]*$/i, "[envió una foto]")
    .replace(/(Audio|Video|Document|Sticker) attached[^]*$/i, "[envió un archivo]")
    .replace(/[\r\n\t]+/g, " ").replace(/ {2,}/g, " ").trim().slice(0, 300) || "[mensaje sin texto]";
}

function ultimoMensajeDelCliente(body) {
  const msgs = (body.whatsapp_context && body.whatsapp_context.messages) || [];
  for (let i = msgs.length - 1; i >= 0; i--) if (msgs[i].direction === "inbound") return msgs[i];
  return null;
}

function motivoReanudacion(body) {
  const sys = (body.execution_context && body.execution_context.system) || {};
  return (sys.last_resume && sys.last_resume.reason) || sys.last_resume_reason || null;
}

function responder(next_edge, vars) {
  return new Response(JSON.stringify(vars ? { next_edge, vars } : { next_edge }), {
    headers: { "Content-Type": "application/json" },
  });
}

async function handler(request, env) {
  const body = await request.json().catch(() => ({}));
  const edges = body.available_edges || [];
  const vars = (body.execution_context && body.execution_context.vars) || {};

  if (motivoReanudacion(body) === "timeout") {
    const n = Number(vars.seguimientos || 0);
    return n >= 1 ? responder("cerrar") : responder("sin_respuesta", { seguimientos: n + 1 });
  }

  const msg = ultimoMensajeDelCliente(body);
  const opcion = msg && msg.reply_option_id;
  if (opcion && OPCIONES.includes(opcion) && edges.includes(opcion)) {
    return responder(opcion, { seguimientos: 0, ...(opcion === "asesor" ? { aviso_mensaje: "Pidió hablar con un asesor" } : {}) });
  }

  const texto = (msg && msg.content) || vars.last_user_input || "";
  if (VOLVER_AL_MENU.test(String(texto).trim())) return responder("menu", { seguimientos: 0 });

  return responder("asesor", { seguimientos: 0, aviso_mensaje: limpiar(texto) });
}
