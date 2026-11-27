// Router del flujo America Sport (nodos "decide" en modo función).
// - Después del agente (edges: pedido / esperar / consulta / asesor): usa la variable `siguiente` que guarda el agente.
// - Después de una espera (edges: respondio / sin_respuesta): usa system.last_resume.reason.

function motivoReanudacion(body) {
  const ec = body.execution_context || {};
  const candidatos = [
    ec.system && ec.system.last_resume && ec.system.last_resume.reason,
    ec.system && ec.system.last_resume_reason,
    body.system && body.system.last_resume && body.system.last_resume.reason,
    ec.vars && ec.vars.system && ec.vars.system.last_resume && ec.vars.system.last_resume.reason,
  ];
  return candidatos.find((v) => typeof v === "string") || null;
}

async function handler(request, env) {
  const body = await request.json().catch(() => ({}));
  const edges = body.available_edges || [];
  const vars = (body.execution_context && body.execution_context.vars) || {};
  let next_edge;

  if (edges.includes("pedido")) {
    const sig = String(vars.siguiente || "").toLowerCase();
    // "consulta" = el cliente pidió un modelo que no existe → avisar al personal (si el flujo tiene ese camino).
    next_edge = sig === "pedido" ? "pedido"
      : sig === "asesor" && edges.includes("asesor") ? "asesor"
      : sig === "consulta" && edges.includes("consulta") ? "consulta"
      : "esperar";
    return new Response(JSON.stringify({ next_edge, vars: { siguiente: "" } }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  if (edges.includes("sin_respuesta")) {
    const motivo = motivoReanudacion(body);
    next_edge = motivo === "timeout" ? "sin_respuesta" : "respondio";
    console.log(JSON.stringify({ motivo, system: (body.execution_context || {}).system }));
    return new Response(JSON.stringify({ next_edge }), { headers: { "Content-Type": "application/json" } });
  }

  return new Response(JSON.stringify({ next_edge: edges[0] }), { headers: { "Content-Type": "application/json" } });
}
