// Filtro de números para el agente America Sport (nodo "decide" en modo función).
// Solo los números de esta lista pasan al agente; el resto no recibe respuesta automática
// (sus mensajes quedan en la bandeja de Kapso para atenderlos a mano).
// Para agregar o quitar números, editar NUMEROS_PERMITIDOS y volver a publicar la función.

const NUMEROS_PERMITIDOS = [
  "59177213515",
  "59172181658",
];

function soloDigitos(valor) {
  return String(valor || "").replace(/\D/g, "");
}

function permitido(numero) {
  const d = soloDigitos(numero);
  if (!d) return false;
  return NUMEROS_PERMITIDOS.some((p) => d === p || (d.length === 8 && `591${d}` === p));
}

async function handler(request, env) {
  const body = await request.json().catch(() => ({}));
  const ctx = (body.execution_context && body.execution_context.context) || {};
  const conv = (body.whatsapp_context && body.whatsapp_context.conversation) || {};
  const numero = conv.phone_number || ctx.phone_number || "";
  const ok = permitido(numero);
  return new Response(JSON.stringify({
    next_edge: ok ? "autorizado" : "no_autorizado",
    vars: { numero_autorizado: ok },
  }), { headers: { "Content-Type": "application/json" } });
}
