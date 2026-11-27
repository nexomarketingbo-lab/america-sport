"""Genera kapso/workflow-america-sport.json a partir de los archivos de chatbot/.

Uso: python3 kapso/build_workflow.py
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELO_CLAUDE_SONNET_5_5 = "1caa3ea4-b319-462b-abae-025bcfdd8cf1"
MODELO_CLAUDE_HAIKU_5_5 = "7c2cc054-60af-4ca8-aa15-030db79ce9db"  # el más económico (~17x más barato que Sonnet 5.5)
MODELO = MODELO_CLAUDE_HAIKU_5_5
FUNCION_BUSCAR_PRODUCTOS = "6e5893e1-577b-4bd7-b198-76271747851f"
FUNCION_FILTRO_NUMEROS = "8305cf42-2f0f-4a87-816e-9599d4303de2"  # kapso/functions/filtro-numeros
FUNCION_RUTA = "a6626bfa-4bfc-444d-ab76-8c91c5fcd10b"   # kapso/functions/ruta-conversacion
ESPERA_SEGUIMIENTO_SEG = int(__import__("os").environ.get("ESPERA_SEGUIMIENTO_SEG", 2 * 3600))  # sin respuesta en 2 h → seguimiento
ESPERA_FINAL_SEG = 20 * 3600         # luego 20 h más (dentro de la ventana de 24 h de WhatsApp) y se cierra
SEGUIMIENTO = ("¡Hola de nuevo! 👋 ¿Pudiste ver los modelos? Si te gustó alguno, dime la talla y el color "
               "y un encargado confirma si lo tenemos. Si buscas otra cosa, escríbeme y te ayudo 💪")
NUMERO_TIENDA = "1362454746955581"        # +591 57358527 (America Sport)
ENCARGADO = "59175389125"                 # recibe el aviso de cada modelo elegido
# Plantilla "aviso_modelo_no_encontrado" (Meta 29440643932243165): poner aquí su id interno de Kapso cuando esté aprobada.
PLANTILLA_AVISO_CONSULTA = None  # mientras no esté aprobada se usa PLANTILLA_AVISO_ENCARGADO
PLANTILLA_AVISO_ENCARGADO = "8223f293-6de1-4305-bb7a-e1caf35d5f0e"  # id Kapso de la plantilla "aviso_encargado_pedido" (Meta 1140906348851594)
# La plantilla debe estar aprobada por Meta y sincronizada en Kapso antes de activar el aviso.
USAR_AVISO = __import__("os").environ.get("USAR_AVISO", "1") == "1"
# Filtro de números (solo responder a números de prueba). Desactivado: el bot atiende a todos los clientes.
USAR_FILTRO = __import__("os").environ.get("USAR_FILTRO", "0") == "1"

def leer(nombre):
    return (ROOT / "chatbot" / nombre).read_text(encoding="utf-8")

def sin_titulo(t):
    return re.sub(r"^# .*\n", "", t, count=1).strip()

def limpiar(t):
    return (sin_titulo(t).replace("`datos-tienda.md`", "DATOS DE LA TIENDA")
            .replace("`enlaces-catalogo.md`", "ENLACES DEL CATÁLOGO"))

HERRAMIENTAS = """
## Herramientas
- `buscar_productos`: úsala SIEMPRE antes de mandar un enlace de productos (ver regla principal), y con `codigo` cuando el cliente elige un modelo.
- `ask_about_file`: para ver fotos, capturas o archivos que mande el cliente (usa la URL que viene en su mensaje).
- `get_current_datetime`: para saber si la tienda está abierta. La tienda está en Bolivia (hora UTC-4).
- Para pasar con un asesor usa SIEMPRE la "Regla fija" (`siguiente` = `asesor`), así se avisa al personal.
- `save_variable` + `complete_task`: cuando el cliente elige un modelo, o pide uno que no existe (ver esas secciones).
- `save_variable` (`siguiente` = `esperar`) + `complete_task`: después de CADA respuesta o pregunta al cliente, incluidas las de botones. No uses `enter_waiting`.
- Formato WhatsApp: negritas con *un asterisco*, nada de tablas ni encabezados markdown. Envía los enlaces completos tal cual.
"""

prompt = limpiar(leer("prompt-sistema.md"))
# El aviso al personal siempre está activo (plantilla de consulta o, si no, la de pedido).
system = (prompt + "\n" + HERRAMIENTAS
          + "\n\n=== DATOS DE LA TIENDA ===\n" + limpiar(leer("datos-tienda.md"))
          + "\n\n=== ENLACES DEL CATÁLOGO ===\n" + limpiar(leer("enlaces-catalogo.md"))
          + "\n\n=== PREGUNTAS FRECUENTES ===\n" + limpiar(leer("preguntas-frecuentes.md")))

texto = {"type": "string"}
herramienta_buscar = {
    "name": "buscar_productos",
    "description": ("Busca productos en americasportbolivia.com, o con `codigo` da el detalle de un modelo (colores y tallas). Devuelve un enlace de sección verificado "
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
            "precio_max": {"type": "number", "description": "Precio máximo en Bs (filtra por el precio de oferta), ej. 150 si el cliente dice 'hasta 150' o 'algo barato de 150'"},
            "precio_min": {"type": "number", "description": "Precio mínimo en Bs"},
            "codigo": {**texto, "description": "Código de un modelo (ej. 14771). Si se envía, devuelve el detalle de ese modelo: nombre, precios, colores y tallas disponibles por color; los demás filtros se ignoran."},
        },
    },
}


UI_SKILLS = [
    {"key": "menu_principal", "title": "Menú principal", "component_type": "interactive_list",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("En el primer mensaje de la conversación, cuando el cliente salude o pida ver opciones. "
                     "body: el saludo de 'Primer mensaje' y al final, siempre, la línea '🛒 Catálogo completo: https://americasportbolivia.com'. button: 'Ver opciones'. Filas (id → title / description): "
                     "calzado → 'Calzado 👟' / 'Zapatillas, chuteras, sandalias y más'; "
                     "ropa → 'Ropa 👕' / 'Poleras, shorts, buzos, calzas'; "
                     "accesorios → 'Accesorios ⚽' / 'Pelotas, mochilas, gorras, guantes'; "
                     "ofertas → 'Ofertas 🔥' / 'Productos con descuento'; "
                     "ubicacion → 'Ubicación y horarios 📍' / 'Calle Colón #130, Santa Cruz'; "
                     "asesor → 'Hablar con un asesor' / 'Te atiende una persona de la tienda'. "
                     "Al recibir la elección: calzado/ropa/accesorios → send_ui_elegir_genero; ofertas → buscar_productos con oferta=true; "
                     "ubicacion → send_ui_ubicacion_tienda y luego los horarios; asesor → sigue la \"Regla fija\" (siguiente = asesor).")},
    {"key": "elegir_genero", "title": "Elegir para quién", "component_type": "interactive_reply_buttons",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Cuando el cliente elija Calzado, Ropa o Accesorios, o busque un producto sin decir para quién. "
                     "body: '¿Para quién es?' (puedes mencionar lo que busca). Botones (id → title): "
                     "hombre → 'Hombre', mujer → 'Mujer', ninos → 'Niños'. "
                     "Con la respuesta, llama a buscar_productos con ese genero (ninos = NIÑOS) y el tipo o producto elegido.")},
    {"key": "carrusel_productos", "title": "Carrusel de productos", "component_type": "carousel_quick_reply",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Para mostrar modelos después de llamar a buscar_productos, cuando devuelva 2 o más productos. "
                     "Usa entre 2 y 5 productos de la respuesta, SOLO con sus datos reales: image_url = 'imagen', "
                     "body de cada tarjeta = nombre + precio, ej. 'AIR MAX LONA C/PLATAFORMA\\nBs 430 → oferta Bs 387' (máx. 160 caracteres), "
                     "button = 'Lo quiero', id = 'modelo_' + codigo (ej. 'modelo_14770'). body del mensaje: una línea corta "
                     "que invite a tocar 'Lo quiero' en el modelo que le guste; si exacto=false, avisa que no hay el modelo exacto y "
                     "que estas son opciones parecidas. Después envía como texto 'Ver todos: ' + enlace_seccion. "
                     "Si hay solo 1 producto, envíalo como texto con su enlace y pregunta si lo quiere.")},
    {"key": "elegir_color", "title": "Elegir color", "component_type": "interactive_list",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Cuando el modelo elegido tiene más de un color (según buscar_productos con codigo) y el cliente no dijo cuál. "
                     "body: '¿En qué color lo quieres?'. button: 'Ver colores'. Una fila por color: id = 'color_' + código de color, "
                     "title = nombre del color en español, description = tallas disponibles, ej. 'Tallas: 38, 39, 40'.")},
    {"key": "elegir_talla", "title": "Elegir talla", "component_type": "interactive_list",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Cuando ya sabes el modelo (y el color, si tiene varios) pero no la talla. Usa SOLO las tallas que devolvió "
                     "buscar_productos con codigo para ese color (máx. 10; si hay más, las 10 más cercanas a lo que pidió). "
                     "body: '¿Qué talla necesitas?' + nombre del modelo. button: 'Ver tallas'. Filas: id = 'talla_' + talla, title = 'Talla ' + talla.")},
    {"key": "ubicacion_tienda", "title": "Ubicación de la tienda", "component_type": "location",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Cuando pregunten dónde está la tienda o elijan 'ubicacion'. Valores fijos: latitude -17.7854042, "
                     "longitude -63.1845161, name 'America Sport', address 'Calle Colón #130, Santa Cruz de la Sierra, Bolivia'. "
                     "Después escribe los horarios: lunes a sábado 9:00–20:00, domingo 10:00–14:00.")},
    {"key": "seguir", "title": "Siguiente paso", "component_type": "interactive_reply_buttons",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Al terminar de mostrar productos o responder una consulta, para ofrecer el siguiente paso. "
                     "body: pregunta corta. Botones (id → title), elige 2 o 3 que tengan sentido: "
                     "ver_mas → 'Ver más modelos', menu → 'Ver menú', asesor → 'Hablar con asesor', quiero_comprar → 'Quiero comprar'. "
                     "Después de un carrusel NO uses 'Quiero comprar' (el cliente ya tiene 'Lo quiero' en cada foto): usa ver_mas, menu y asesor. "
                     "quiero_comprar sin modelo elegido → send_ui_elegir_modelo con los modelos que ya le mostraste; "
                     "ver_mas → responde SIEMPRE con texto invitando a ver todos los modelos en la página, con el enlace_seccion de la última búsqueda "
                     "(o https://americasportbolivia.com si no hay), ej. 'Tenemos muchos más modelos 👟 Míralos todos aquí: <enlace>. Si te gusta alguno, "
                     "mándame el enlace o una captura y te ayudo con la talla 🙌'; "
                     "menu → send_ui_menu_principal; asesor → sigue la \"Regla fija\" (siguiente = asesor).")},
    {"key": "elegir_modelo", "title": "Elegir modelo", "component_type": "interactive_list",
     "enabled": True, "wait_for_reply": False,
     "instruction": ("Cuando el cliente quiere comprar pero no dijo cuál modelo (ej. toca 'Quiero comprar' o escribe 'lo quiero' sin "
                     "tocar una tarjeta). Usa los modelos que ya le mostraste en esta conversación (sus códigos están en los id "
                     "'modelo_…' del carrusel). body: '¿Cuál de estos modelos quieres?'. button: 'Ver modelos'. Filas: id = 'modelo_' + codigo, "
                     "title = nombre del modelo recortado a 24 caracteres, description = precio, ej. 'Bs 350 → oferta Bs 315'. "
                     "Nunca le pidas que vuelva a buscar el carrusel de arriba.")},
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
            *([{"id": "filtro_numeros", "type": "flow-node", "position": {"x": 350, "y": 100},
             "data": {"node_type": "decide", "display_name": "Filtro de números", "config": {
                 "decision_type": "function",
                 "function_id": FUNCION_FILTRO_NUMEROS,
                 "conditions": [
                     {"label": "autorizado", "description": "El número está en la lista permitida"},
                     {"label": "no_autorizado", "description": "Cualquier otro número: no se responde"},
                 ],
                 "llm_configuration": {},
             }}}] if USAR_FILTRO else []),
            {"id": "sporty", "type": "flow-node", "position": {"x": 650, "y": 50},
             "data": {"node_type": "agent", "display_name": "Asistente de America Sport (IA)", "config": {
                 "system_prompt": system,
                 "provider_model_id": MODELO,
                 "temperature": 0.3,
                 "message_delivery_mode": "auto_send_assistant_text",
                 "enabled_default_tools": ["get_current_datetime", "enter_waiting",
                                           "get_whatsapp_context", "complete_task", "save_variable", "ask_about_file"],
                 "flow_agent_function_tools": [herramienta_buscar],
                 "ui_skills": UI_SKILLS,
             }}},
            # Después de cada respuesta del agente: ¿eligió un modelo o hay que esperar?
            {"id": "ruta_agente", "type": "flow-node", "position": {"x": 950, "y": 250},
             "data": {"node_type": "decide", "display_name": "¿Eligió modelo?", "config": {
                 "decision_type": "function", "function_id": FUNCION_RUTA, "llm_configuration": {},
                 "conditions": [{"label": "pedido", "description": "El cliente eligió un modelo"},
                                {"label": "esperar", "description": "Esperar la respuesta del cliente"},
                                {"label": "consulta", "description": "Pidió un modelo que no existe: avisar al personal"},
                                {"label": "asesor", "description": "No sabe responder: avisar al personal y pasar a un asesor"}]}}},
            {"id": "espera_1", "type": "flow-node", "position": {"x": 950, "y": 450},
             "data": {"node_type": "wait_for_response", "display_name": "Esperar respuesta (2 h)", "config": {
                 "has_timeout": True, "timeout_seconds": ESPERA_SEGUIMIENTO_SEG}}},
            {"id": "ruta_espera_1", "type": "flow-node", "position": {"x": 950, "y": 650},
             "data": {"node_type": "decide", "display_name": "¿Respondió?", "config": {
                 "decision_type": "function", "function_id": FUNCION_RUTA, "llm_configuration": {},
                 "conditions": [{"label": "respondio", "description": "El cliente respondió"},
                                {"label": "sin_respuesta", "description": "Pasó el tiempo sin respuesta"}]}}},
            {"id": "seguimiento", "type": "flow-node", "position": {"x": 1250, "y": 650},
             "data": {"node_type": "send_text", "display_name": "Mensaje de seguimiento", "config": {
                 "message": SEGUIMIENTO}}},
            {"id": "espera_2", "type": "flow-node", "position": {"x": 1550, "y": 650},
             "data": {"node_type": "wait_for_response", "display_name": "Esperar respuesta (20 h)", "config": {
                 "has_timeout": True, "timeout_seconds": ESPERA_FINAL_SEG}}},
            {"id": "ruta_espera_2", "type": "flow-node", "position": {"x": 1850, "y": 650},
             "data": {"node_type": "decide", "display_name": "¿Respondió al seguimiento?", "config": {
                 "decision_type": "function", "function_id": FUNCION_RUTA, "llm_configuration": {},
                 "conditions": [{"label": "respondio", "description": "El cliente respondió"},
                                {"label": "sin_respuesta", "description": "Sin respuesta: se cierra"}]}}},
            # Cliente eligió un modelo → avisar al encargado (si la plantilla está aprobada) → pasar a humano.
            *([{"id": "aviso_encargado", "type": "flow-node", "position": {"x": 950, "y": 50},
                "data": {"node_type": "send_template", "display_name": "Aviso al encargado", "config": {
                    "template_id": PLANTILLA_AVISO_ENCARGADO,
                    "phone_number_id": NUMERO_TIENDA,
                    "to_phone_number": ENCARGADO,
                    "parameters": [{"type": "BODY", "parameters": [
                        {"type": "text", "parameter_name": "cliente", "text": "{{vars.cliente_nombre}}"},
                        {"type": "text", "parameter_name": "telefono", "text": "+{{context.phone_number}} · Escríbele: https://wa.me/{{context.phone_number}}"},
                        {"type": "text", "parameter_name": "modelo", "text": "{{vars.pedido_modelo}}"},
                        {"type": "text", "parameter_name": "detalle", "text": "{{vars.pedido_detalle}}"},
                        {"type": "text", "parameter_name": "enlace", "text": "{{vars.pedido_enlace}}"},
                    ]}],
                }}}] if USAR_AVISO else []),
            # Cliente pidió un modelo que no existe → avisar al personal y seguir la conversación.
            # Cliente preguntó algo que el bot no sabe → avisar al personal y pasar a un asesor.
            *[{"id": nid, "type": "flow-node", "position": {"x": 1250, "y": y},
               "data": {"node_type": "send_template", "display_name": nombre, "config": {
                   "template_id": PLANTILLA_AVISO_CONSULTA or PLANTILLA_AVISO_ENCARGADO,
                   "phone_number_id": NUMERO_TIENDA,
                   "to_phone_number": ENCARGADO,
                   "parameters": [{"type": "BODY", "parameters": (
                       [{"type": "text", "parameter_name": "cliente", "text": "{{vars.cliente_nombre}}"},
                        {"type": "text", "parameter_name": "telefono", "text": "+{{context.phone_number}} · Escríbele: https://wa.me/{{context.phone_number}}"},
                        {"type": "text", "parameter_name": "busqueda", "text": "{{vars.consulta_busqueda}}"}]
                       if PLANTILLA_AVISO_CONSULTA and nid == "aviso_consulta" else
                       [{"type": "text", "parameter_name": "cliente", "text": "{{vars.cliente_nombre}}"},
                        {"type": "text", "parameter_name": "telefono", "text": "+{{context.phone_number}} · Escríbele: https://wa.me/{{context.phone_number}}"},
                        {"type": "text", "parameter_name": "modelo", "text": "Consulta: {{vars.consulta_busqueda}}"},
                        {"type": "text", "parameter_name": "detalle", "text": "Ver el chat"},
                        {"type": "text", "parameter_name": "enlace", "text": "https://americasportbolivia.com"}])}],
               }}} for nid, nombre, y in [("aviso_consulta", "Aviso: modelo no encontrado", 300),
                                           ("aviso_asesor", "Aviso: consulta para un asesor", 420)]],
            {"id": "pasar_a_asesor", "type": "flow-node", "position": {"x": 1550, "y": 420},
             "data": {"node_type": "handoff", "display_name": "Pasa a un asesor", "config": {
                 "reason": "Consulta que el bot no sabe responder"}}},
            {"id": "confirmar_stock", "type": "flow-node", "position": {"x": 1250, "y": 50},
             "data": {"node_type": "handoff", "display_name": "Encargado confirma stock", "config": {
                 "reason": "Cliente eligió un modelo: confirmar disponibilidad"}}},
        ],
        "edges": [*([{"source": "start", "target": "filtro_numeros", "label": "next"},
                     {"source": "filtro_numeros", "target": "sporty", "label": "autorizado"}] if USAR_FILTRO
                    else [{"source": "start", "target": "sporty", "label": "next"}]),
                  {"source": "sporty", "target": "ruta_agente", "label": "next"},
                  *([{"source": "ruta_agente", "target": "aviso_encargado", "label": "pedido"},
                     {"source": "aviso_encargado", "target": "confirmar_stock", "label": "next"}] if USAR_AVISO
                    else [{"source": "ruta_agente", "target": "confirmar_stock", "label": "pedido"}]),
                  {"source": "ruta_agente", "target": "espera_1", "label": "esperar"},
                  {"source": "ruta_agente", "target": "aviso_consulta", "label": "consulta"},
                  {"source": "aviso_consulta", "target": "espera_1", "label": "next"},
                  {"source": "ruta_agente", "target": "aviso_asesor", "label": "asesor"},
                  {"source": "aviso_asesor", "target": "pasar_a_asesor", "label": "next"},
                  {"source": "espera_1", "target": "ruta_espera_1", "label": "next"},
                  {"source": "ruta_espera_1", "target": "sporty", "label": "respondio"},
                  {"source": "ruta_espera_1", "target": "seguimiento", "label": "sin_respuesta"},
                  {"source": "seguimiento", "target": "espera_2", "label": "next"},
                  {"source": "espera_2", "target": "ruta_espera_2", "label": "next"},
                  {"source": "ruta_espera_2", "target": "sporty", "label": "respondio"}],
    },
}}

salida = ROOT / "kapso" / "workflow-america-sport.json"
salida.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK {salida.relative_to(ROOT)} — prompt de {len(system)} caracteres")
