"""Genera kapso/workflow-menu-sin-ia.json: bot de America Sport SIN IA (no gasta créditos de IA).

Menú con lista → enlace a la sección de la web. Cualquier mensaje que no sea una opción
→ "Enseguida un asesor se comunicará contigo" + aviso al encargado + pasa a humano.

Uso: python3 kapso/build_menu_sin_ia.py
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FUNCION_MENU = "d2535f06-f55f-40d3-8f70-4c737b13e65a"  # kapso/functions/menu-sin-ia
NUMERO_TIENDA = "1362454746955581"          # +591 57358527
ENCARGADO = "59175389125"
PLANTILLA_AVISO_ENCARGADO = "8223f293-6de1-4305-bb7a-e1caf35d5f0e"  # aviso_encargado_pedido
WEB = "https://americasportbolivia.com"
B = f"{WEB}/index.php"
CIERRE = ("\n\nSi te gusta algún modelo, mándanos la *captura o el enlace* con tu talla y un asesor te confirma "
          "si está disponible 🙌\nEscribe *menú* para ver otras opciones.")
HORARIO = "Atendemos de lunes a sábado de 9:00 a 20:00 y domingos de 10:00 a 14:00."

SECCIONES = [  # id, título en la lista (≤24), descripción (≤72), texto que se envía
    ("calzado_hombre", "Calzado hombre 👟", "Zapatillas, chuteras y más",
     f"👟 *Calzado para hombre*\nMira todos los modelos con precios y tallas aquí:\n{B}?tipo=CALZADO&genero=HOMBRE"),
    ("calzado_mujer", "Calzado mujer 👟", "Zapatillas, sandalias y más",
     f"👟 *Calzado para mujer*\nMira todos los modelos con precios y tallas aquí:\n{B}?tipo=CALZADO&genero=MUJER"),
    ("calzado_ninos", "Calzado niños 👟", "Zapatillas, chuteras y más",
     f"👟 *Calzado para niños*\nMira todos los modelos con precios y tallas aquí:\n{B}?tipo=CALZADO&genero=NI%C2%A5OS"),
    ("ropa", "Ropa 👕", "Poleras, shorts, buzos, calzas",
     f"👕 *Ropa deportiva*\nMira todos los modelos con precios y tallas aquí:\n{B}?tipo=ROPA"),
    ("accesorios", "Accesorios ⚽", "Pelotas, mochilas, gorras, guantes",
     f"⚽ *Accesorios*\nMira todo aquí:\n{B}?tipo=ACCESORIOS"),
    ("ofertas", "Ofertas 🔥", "Productos con descuento",
     f"🔥 *Ofertas*\nMira todos los productos con descuento aquí:\n{B}?oferta=1"),
]
UBICACION = ("📍 *America Sport*\nCalle Colón #130, Santa Cruz de la Sierra\nhttps://maps.app.goo.gl/MiKgaevYmwHoAXeU9\n\n"
             f"🕘 {HORARIO}\n\nEscribe *menú* para ver otras opciones.")
ASESOR = f"¡Gracias por escribirnos! 🙌 Enseguida un asesor de America Sport se comunicará contigo.\n{HORARIO}"
SEGUIMIENTO = ("¡Hola de nuevo! 👋 ¿Encontraste lo que buscabas? Si te gustó algún modelo, mándanos la captura o el enlace "
               "con tu talla y un asesor te confirma. Escribe *menú* para ver las opciones.")
MENU = ("¡Hola! 👋 Bienvenido a *America Sport*. ¿Qué estás buscando hoy?\n\n"
        f"🛒 Catálogo completo: {WEB}\n\nElige una opción o escríbenos tu consulta y un asesor te atiende.")

def nodo(id_, tipo, x, y, nombre, config):
    return {"id": id_, "type": "flow-node", "position": {"x": x, "y": y},
            "data": {"node_type": tipo, "display_name": nombre, "config": config}}

def texto(id_, x, y, nombre, mensaje):
    return nodo(id_, "send_text", x, y, nombre, {"message": mensaje})

filas = [{"id": s[0], "title": s[1], "description": s[2]} for s in SECCIONES] + [
    {"id": "ubicacion", "title": "Ubicación y horarios 📍", "description": "Calle Colón #130, Santa Cruz"},
    {"id": "asesor", "title": "Hablar con un asesor", "description": "Te atiende una persona de la tienda"},
]
etiquetas = [s[0] for s in SECCIONES] + ["ubicacion", "asesor", "menu", "sin_respuesta", "cerrar"]

nodes = [
    nodo("start", "start", 0, 300, "Inicio", {}),
    nodo("menu", "send_interactive", 250, 300, "Menú", {
        "interactive_type": "list", "body_text": MENU, "list_button_text": "Ver opciones",
        "list_sections": [{"title": "America Sport", "rows": filas}]}),
    nodo("espera", "wait_for_response", 500, 300, "Esperar respuesta (2 h)", {"has_timeout": True, "timeout_seconds": 2 * 3600}),
    nodo("ruta", "decide", 750, 300, "¿Qué eligió?", {
        "decision_type": "function", "function_id": FUNCION_MENU, "llm_configuration": {},
        "conditions": [{"label": e, "description": e.replace("_", " ")} for e in etiquetas]}),
    *[texto(f"t_{s[0]}", 1050, 40 + i * 90, s[1], s[3] + CIERRE) for i, s in enumerate(SECCIONES)],
    texto("t_ubicacion", 1050, 600, "Ubicación", UBICACION),
    texto("t_seguimiento", 1050, 700, "Seguimiento", SEGUIMIENTO),
    texto("t_asesor", 1050, 820, "Un asesor te contacta", ASESOR),
    nodo("aviso_encargado", "send_template", 1350, 820, "Aviso al encargado", {
        "template_id": PLANTILLA_AVISO_ENCARGADO, "phone_number_id": NUMERO_TIENDA, "to_phone_number": ENCARGADO,
        "parameters": [{"type": "BODY", "parameters": [
            {"type": "text", "parameter_name": "cliente", "text": "Cliente"},
            {"type": "text", "parameter_name": "telefono", "text": "+{{context.phone_number}}"},
            {"type": "text", "parameter_name": "modelo", "text": "Consulta: {{vars.aviso_mensaje}}"},
            {"type": "text", "parameter_name": "detalle", "text": "Ver el chat"},
            {"type": "text", "parameter_name": "enlace", "text": WEB},
        ]}]}),
    nodo("pasar_a_humano", "handoff", 1650, 820, "Pasa a un asesor", {"reason": "Consulta para un asesor"}),
]
edges = [
    {"source": "start", "target": "menu", "label": "next"},
    {"source": "menu", "target": "espera", "label": "next"},
    {"source": "espera", "target": "ruta", "label": "next"},
    *[{"source": "ruta", "target": f"t_{s[0]}", "label": s[0]} for s in SECCIONES],
    *[{"source": f"t_{s[0]}", "target": "espera", "label": "next"} for s in SECCIONES],
    {"source": "ruta", "target": "t_ubicacion", "label": "ubicacion"},
    {"source": "t_ubicacion", "target": "espera", "label": "next"},
    {"source": "ruta", "target": "menu", "label": "menu"},
    {"source": "ruta", "target": "t_seguimiento", "label": "sin_respuesta"},
    {"source": "t_seguimiento", "target": "espera", "label": "next"},
    {"source": "ruta", "target": "t_asesor", "label": "asesor"},
    {"source": "t_asesor", "target": "aviso_encargado", "label": "next"},
    {"source": "aviso_encargado", "target": "pasar_a_humano", "label": "next"},
]
wf = {"workflow": {"name": "America Sport - Menú sin IA", "slug": "america-sport-menu-sin-ia",
                   "description": "Bot sin IA: menú con enlaces a la web; consultas libres pasan a un asesor con aviso al encargado.",
                   "definition": {"nodes": nodes, "edges": edges}}}
for n in filas: assert len(n["title"]) <= 24 and len(n["description"]) <= 72, n
assert len(MENU) <= 1024
salida = ROOT / "kapso" / "workflow-menu-sin-ia.json"
salida.write_text(json.dumps(wf, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK {salida.relative_to(ROOT)} — {len(nodes)} nodos, {len(edges)} flechas")
