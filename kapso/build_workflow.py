"""Genera kapso/workflow-america-sport.json a partir de los archivos de chatbot/.

Uso: python3 kapso/build_workflow.py
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELO_CLAUDE_SONNET_5_5 = "1caa3ea4-b319-462b-abae-025bcfdd8cf1"
FUNCION_BUSCAR_PRODUCTOS = "6e5893e1-577b-4bd7-b198-76271747851f"
FUNCION_FILTRO_NUMEROS = "8305cf42-2f0f-4a87-816e-9599d4303de2"  # kapso/functions/filtro-numeros

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
- `enter_waiting`: después de responder o preguntar algo al cliente (sin botones), para esperar su siguiente mensaje.
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


UI_SKILLS = [
    {"key": "menu_principal", "title": "Menú principal", "component_type": "interactive_list",
     "enabled": True, "wait_for_reply": True,
     "instruction": ("En el primer mensaje de la conversación, cuando el cliente salude o pida ver opciones. "
                     "body: el saludo de 'Primer mensaje'. button: 'Ver opciones'. Filas (id → title / description): "
                     "calzado → 'Calzado 👟' / 'Zapatillas, chuteras, sandalias y más'; "
                     "ropa → 'Ropa 👕' / 'Poleras, shorts, buzos, calzas'; "
                     "accesorios → 'Accesorios ⚽' / 'Pelotas, mochilas, gorras, guantes'; "
                     "ofertas → 'Ofertas 🔥' / 'Productos con descuento'; "
                     "ubicacion → 'Ubicación y horarios 📍' / 'Calle Colón #130, Santa Cruz'; "
                     "asesor → 'Hablar con un asesor' / 'Te atiende una persona de la tienda'. "
                     "Al recibir la elección: calzado/ropa/accesorios → send_ui_elegir_genero; ofertas → buscar_productos con oferta=true; "
                     "ubicacion → send_ui_ubicacion_tienda y luego los horarios; asesor → handoff_to_human.")},
    {"key": "elegir_genero", "title": "Elegir para quién", "component_type": "interactive_reply_buttons",
     "enabled": True, "wait_for_reply": True,
     "instruction": ("Cuando el cliente elija Calzado, Ropa o Accesorios, o busque un producto sin decir para quién. "
                     "body: '¿Para quién es?' (puedes mencionar lo que busca). Botones (id → title): "
                     "hombre → 'Hombre', mujer → 'Mujer', ninos → 'Niños'. "
                     "Con la respuesta, llama a buscar_productos con ese genero (ninos = NIÑOS) y el tipo o producto elegido.")},
    {"key": "carrusel_productos", "title": "Carrusel de productos", "component_type": "carousel_url",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Para mostrar modelos después de llamar a buscar_productos, cuando devuelva 2 o más productos. "
                     "Usa entre 2 y 5 productos de la respuesta, SOLO con sus datos reales: image_url = 'imagen', url = 'enlace', "
                     "body de cada tarjeta = nombre + precio, ej. 'AIR MAX LONA C/PLATAFORMA\nBs 430 → oferta Bs 387' (máx. 160 caracteres), "
                     "button = 'Ver modelo'. body del mensaje: una línea corta; si exacto=false, avisa que no hay el modelo exacto y "
                     "que estas son opciones parecidas. Después envía el enlace_seccion como texto ('Ver todos: ...') y usa send_ui_seguir. "
                     "Si hay solo 1 producto, envíalo como texto con su enlace.")},
    {"key": "ubicacion_tienda", "title": "Ubicación de la tienda", "component_type": "location",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Cuando pregunten dónde está la tienda o elijan 'ubicacion'. Valores fijos: latitude -17.7854042, "
                     "longitude -63.1845161, name 'America Sport', address 'Calle Colón #130, Santa Cruz de la Sierra, Bolivia'. "
                     "Después escribe los horarios: lunes a sábado 9:00–20:00, domingo 10:00–14:00.")},
    {"key": "seguir", "title": "Siguiente paso", "component_type": "interactive_reply_buttons",
     "enabled": True, "wait_for_reply": True,
     "instruction": ("Al terminar de mostrar productos o responder una consulta, para ofrecer el siguiente paso. "
                     "body: pregunta corta, ej. '¿Te gustó alguno? Dime talla y color, o elige:'. Botones (id → title), elige 2 o 3: "
                     "quiero_comprar → 'Quiero comprar', ver_mas → 'Ver más modelos', menu → 'Ver menú', asesor → 'Hablar con asesor'. "
                     "quiero_comprar → pide modelo, talla y color y luego handoff_to_human con el resumen; ver_mas → pregunta qué cambiar "
                     "(marca, deporte, precio) y vuelve a buscar; menu → send_ui_menu_principal; asesor → handoff_to_human.")},
]

workflow = {"workflow": {
    "name": "America Sport - Asistente WhatsApp",
    "slug": "america-sport-asistente",
    "description": "Asistente de America Sport: atiende consultas y envía enlaces del catálogo de americasportbolivia.com.",
    "definition": {
        "nodes": [
            {"id": "start", "type": "flow-node", "position": {"x": 100, "y": 100},
             "data": {"node_type": "start", "config": {}, "display_name": "Inicio"}},
            # Solo los números de kapso/functions/filtro-numeros pasan al agente.
            {"id": "filtro_numeros", "type": "flow-node", "position": {"x": 350, "y": 100},
             "data": {"node_type": "decide", "display_name": "Filtro de números", "config": {
                 "decision_type": "function",
                 "function_id": FUNCION_FILTRO_NUMEROS,
                 "conditions": [
                     {"label": "autorizado", "description": "El número está en la lista permitida"},
                     {"label": "no_autorizado", "description": "Cualquier otro número: no se responde"},
                 ],
                 "llm_configuration": {},
             }}},
            {"id": "sporty", "type": "flow-node", "position": {"x": 650, "y": 50},
             "data": {"node_type": "agent", "display_name": "Asistente de America Sport (IA)", "config": {
                 "system_prompt": system,
                 "provider_model_id": MODELO_CLAUDE_SONNET_5_5,
                 "temperature": 0.3,
                 "message_delivery_mode": "auto_send_assistant_text",
                 "enabled_default_tools": ["get_current_datetime", "handoff_to_human", "enter_waiting",
                                           "get_whatsapp_context", "complete_task"],
                 "flow_agent_function_tools": [herramienta_buscar],
                 "ui_skills": UI_SKILLS,
             }}},
        ],
        "edges": [{"source": "start", "target": "filtro_numeros", "label": "next"},
                  {"source": "filtro_numeros", "target": "sporty", "label": "autorizado"}],
    },
}}

salida = ROOT / "kapso" / "workflow-america-sport.json"
salida.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK {salida.relative_to(ROOT)} — prompt de {len(system)} caracteres")
