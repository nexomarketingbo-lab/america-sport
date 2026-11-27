# America Sport – Chatbot de WhatsApp (Kapso)

Contenido del asistente virtual de **America Sport** (tienda de ropa deportiva) para cargar en [Kapso](https://app.kapso.ai).

- **Cuenta Kapso:** `nexo.marketing.bo+americasport@gmail.com`
- **Estado:** listo para cargar. Pendiente: tarifas y plazos de envío (por ahora los confirma un asesor).

## Archivos

| Archivo | Para qué sirve | Dónde va en Kapso |
|---|---|---|
| `chatbot/prompt-sistema.md` | Personalidad y reglas del asistente | Instrucciones / system prompt del agente |
| `chatbot/datos-tienda.md` | Datos de la tienda (horarios, pagos, cambios) | Base de conocimiento |
| `chatbot/enlaces-catalogo.md` | Cómo armar enlaces a modelos y secciones de la web | Base de conocimiento |
| `chatbot/preguntas-frecuentes.md` | Respuestas a preguntas comunes | Base de conocimiento |
| `chatbot/flujo-conversacion.md` | Menú y flujo de la conversación | Flujo (flow builder) |

## Pasos

1. (Opcional) Cuando estén definidos, agregar costos y plazos de envío en `datos-tienda.md`.
2. Crear el proyecto **America Sport** en Kapso y conectar el número de WhatsApp Business.
3. Pegar `prompt-sistema.md` en las instrucciones del agente.
4. Subir `datos-tienda.md`, `enlaces-catalogo.md` y `preguntas-frecuentes.md` a la base de conocimiento.
5. Armar el menú según `flujo-conversacion.md`.
6. Probar con el checklist de abajo antes de publicar.

## Checklist de pruebas

- [ ] Saluda y muestra el menú al primer mensaje
- [ ] Responde horarios, ubicación y pago por QR correctamente
- [ ] Manda el enlace correcto al preguntar por un modelo o sección (probar marca + producto + género)
- [ ] Explica bien la política de cambios (tardes, sin devoluciones)
- [ ] No inventa precios ni stock que no estén en los datos
- [ ] Deriva a un asesor humano cuando se le pide
- [ ] Responde bien fuera de horario

## Bot activo ahora: menú sin IA

Para no gastar créditos de IA, el número +591 57358527 está atendido por **"America Sport - Menú sin IA"** (`kapso/build_menu_sin_ia.py` → `kapso/workflow-menu-sin-ia.json`, función `kapso/functions/menu-sin-ia`):
- Menú en lista (calzado hombre / mujer / niños, ropa, accesorios, ofertas, ubicación, asesor) → enlace a esa sección de la web.
- Cualquier mensaje que no sea una opción (texto, foto, enlace) → "Enseguida un asesor se comunicará contigo" + aviso al encargado (+591 75389125) + pasa a humano.
- "menú" / "hola" → vuelve a mostrar el menú. Sin respuesta en 2 h → un seguimiento; luego se cierra.
- Prueba: `node tests/probar_menu_sin_ia.mjs`.

El agente con IA (abajo) sigue guardado en Kapso con su disparador **apagado**. Para volver a usarlo: activar su disparador y apagar el del menú sin IA (solo uno puede estar activo por número).

## Agente en Kapso

El agente **"America Sport - Asistente WhatsApp"** (slug `america-sport-asistente`) está **activo** en Kapso, en el número **+591 57358527**.

- Workflow: Inicio → agente IA "Asistente de America Sport" (Claude Haiku 5.5, el modelo más económico) → *(cliente elige un modelo)* → **aviso al encargado** (+591 75389125) → **pasa a humano** para confirmar stock.
- **Seguimiento:** después de cada respuesta del asistente, el flujo espera. Si el cliente no contesta en **2 h**, se le manda un mensaje de seguimiento (uno solo); si sigue sin contestar 20 h más, la conversación se cierra. Tiempos y texto en `kapso/build_workflow.py` (`ESPERA_SEGUIMIENTO_SEG`, `SEGUIMIENTO`). La función `kapso/functions/ruta-conversacion` decide cada camino.
- **Aviso al encargado:** plantilla de Meta `aviso_encargado_pedido` (cliente, teléfono, modelo, talla/color, enlace). Aprobada por Meta y activa. El nodo usa el id interno de Kapso de la plantilla (`PLANTILLA_AVISO_ENCARGADO`), que se obtiene agregando un nodo "Send template" en el lienzo y leyendo la definición.
- **Atiende a todos los clientes** en +591 57358527. El filtro de números de prueba (`kapso/functions/filtro-numeros/index.js`) está desactivado; se vuelve a poner con `USAR_FILTRO=1 python3 kapso/build_workflow.py`.
- Herramientas: `buscar_productos` (función propia), hora actual, pasar con un humano, esperar al cliente y contexto de WhatsApp.
- El prompt, los datos, los enlaces y las preguntas frecuentes van en las instrucciones del agente.

### Función `buscar_productos`
Código en `kapso/functions/buscar-productos/index.js` (Kapso Function, Cloudflare Worker). Recibe filtros (marca, familia, deporte, género, tipo, oferta y texto del modelo) y:
1. arma el enlace con la codificación correcta (espacios, Ñ),
2. revisa que la sección tenga productos (reintenta si la web responde vacía),
3. devuelve hasta 8 modelos con nombre, enlace y precio normal y de oferta,
4. si no hay productos, quita los mínimos filtros posibles y avisa (`exacto: false`).

### Actualizar el agente
1. Editar los archivos de `chatbot/`.
2. `python3 kapso/build_workflow.py` → regenera `kapso/workflow-america-sport.json`.
3. Subir la definición a Kapso (PATCH `/platform/v1/workflows/{id}` con `lock_version`).

### Pruebas
- `python3 tests/verificar_enlaces.py` → datos clave del prompt y enlaces del catálogo.
- `node tests/probar_buscar_productos.mjs` → función de búsqueda contra la web real.
- `node tests/probar_filtro_numeros.mjs` → filtro de números.
- `node tests/probar_ruta_conversacion.mjs` → ruta de conversación (pedido / esperar / seguimiento).

### Activarlo
En Kapso: abrir el workflow → agregar el disparador *Inbound message* con el número de WhatsApp → activar. Probar primero con el número sandbox.
