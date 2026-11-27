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

## Agente en Kapso

El agente **"America Sport - Asistente WhatsApp"** (slug `america-sport-asistente`) está creado en Kapso como **borrador**.

- Workflow: Inicio → **filtro de números** → agente IA "Sporty" (Claude Sonnet 5.5).
- **Filtro de números** (`kapso/functions/filtro-numeros/index.js`): por ahora el bot solo responde a **+591 77213515** y **+591 72181658**. Otros números no reciben respuesta automática (sus mensajes quedan en la bandeja de Kapso). Para abrirlo a todos los clientes, quitar el nodo del filtro en `kapso/build_workflow.py` o editar la lista y volver a publicar la función.
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

### Activarlo
En Kapso: abrir el workflow → agregar el disparador *Inbound message* con el número de WhatsApp → activar. Probar primero con el número sandbox.
