"""Genera kapso/workflow-america-sport.json a partir de los archivos de chatbot/.

Uso: python3 kapso/build_workflow.py
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELO_CLAUDE_SONNET_5_5 = "1caa3ea4-b319-462b-abae-025bcfdd8cf1"
FUNCION_BUSCAR_PRODUCTOS = "6e5893e1-577b-4bd7-b198-76271747851f"

def leer(nombre):
    return (ROOT / "chatbot" / nombre).read_text(encoding="utf-8")

def sin_titulo(t):
    return re.sub(r"^# .*\n", "", t, count=1).strip()

def limpiar(t):
    return (sin_titulo(t).replace("`datos-tienda.md`", "DATOS DE LA TIENDA")
            .replace("`enlaces-catalogo.md`", "ENLACES DEL CATÁLOGO"))

HERRAMIENTAS = """
## Herramientas
- `buscar_productos`: úsala SIEMPRE antes de mandar un enlace de productos (ver regla principal).
- `get_current_datetime`: para saber si la tienda está abierta. La tienda está en Bolivia (hora UTC-4).
- `handoff_to_human`: para pasar con un asesor (incluye un resumen breve en el motivo).
- `enter_waiting`: después de responder o preguntar algo al cliente, para esperar su siguiente mensaje.
- Formato WhatsApp: negritas con *un asterisco*, nada de tablas ni encabezados markdown. Envía los enlaces completos tal cual.
"""

prompt = limpiar(leer("prompt-sistema.md")).replace(
    "la sección ENLACES DEL CATÁLOGO", "la sección ENLACES DEL CATÁLOGO")
system = (prompt + "\n" + HERRAMIENTAS
          + "\n\n=== DATOS DE LA TIENDA ===\n" + limpiar(leer("datos-tienda.md"))
          + "\n\n=== ENLACES DEL CATÁLOGO ===\n" + limpiar(leer("enlaces-catalogo.md"))
          + "\n\n=== PREGUNTAS FRECUENTES ===\n" + limpiar(leer("preguntas-frecuentes.md")))

texto = {"type": "string"}
herramienta_buscar = {
    "name": "buscar_productos",
    "description": ("Busca productos en americasportbolivia.com. Devuelve un enlace de sección verificado "
                    "(con productos) y hasta 8 modelos con nombre, enlace y precios en Bs. Si no hay productos "
                    "con todos los filtros, quita los mínimos necesarios e indica cuáles (exacto=false)."),
    "function_id": FUNCION_BUSCAR_PRODUCTOS,
    "input_schema": {
        "type": "object",
        "properties": {
            "marca": {**texto, "description": "Marca, ej. NIKE, ADIDAS, PUMA, NEW BALANCE, UNDER ARMOUR"},
            "familia": {**texto, "description": "Tipo de producto, ej. ZAPATILLAS, CHUTERAS, POLERAS, SHORT, PELOTAS, MOCHILAS, SANDALIAS, CROCS"},
            "grupo": {**texto, "description": "Deporte, ej. FUTBOL, FUTSAL, RUNNING, BASQUET, VOLEIBOL, TENIS, GIMNASIO, NATACION, CASUAL"},
            "genero": {**texto, "description": "HOMBRE, MUJER, NIÑOS o UNISEX"},
            "tipo": {**texto, "description": "CALZADO, ROPA o ACCESORIOS"},
            "oferta": {"type": "boolean", "description": "true para ver solo ofertas"},
            "buscar": {**texto, "description": "Palabras del nombre del modelo, ej. 'air max', 'superstar'"},
        },
    },
}

workflow = {"workflow": {
    "name": "America Sport - Asistente WhatsApp",
    "slug": "america-sport-asistente",
    "description": "Asistente Sporty de America Sport: atiende consultas y envía enlaces del catálogo de americasportbolivia.com.",
    "definition": {
        "nodes": [
            {"id": "start", "type": "flow-node", "position": {"x": 100, "y": 100},
             "data": {"node_type": "start", "config": {}, "display_name": "Inicio"}},
            {"id": "sporty", "type": "flow-node", "position": {"x": 400, "y": 100},
             "data": {"node_type": "agent", "display_name": "Sporty (agente IA)", "config": {
                 "system_prompt": system,
                 "provider_model_id": MODELO_CLAUDE_SONNET_5_5,
                 "temperature": 0.3,
                 "message_delivery_mode": "auto_send_assistant_text",
                 "enabled_default_tools": ["get_current_datetime", "handoff_to_human", "enter_waiting",
                                           "get_whatsapp_context", "complete_task"],
                 "flow_agent_function_tools": [herramienta_buscar],
             }}},
        ],
        "edges": [{"source": "start", "target": "sporty", "label": "next"}],
    },
}}

salida = ROOT / "kapso" / "workflow-america-sport.json"
salida.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK {salida.relative_to(ROOT)} — prompt de {len(system)} caracteres")
