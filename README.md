# America Sport – Chatbot de WhatsApp (Kapso)

Contenido del asistente virtual de **America Sport** (tienda de ropa deportiva) para cargar en [Kapso](https://app.kapso.ai).

- **Cuenta Kapso:** `nexo.marketing.bo+americasport@gmail.com`
- **Estado:** borrador — completar los campos marcados con `[COMPLETAR]`.

## Archivos

| Archivo | Para qué sirve | Dónde va en Kapso |
|---|---|---|
| `chatbot/prompt-sistema.md` | Personalidad y reglas del asistente | Instrucciones / system prompt del agente |
| `chatbot/datos-tienda.md` | Datos de la tienda (horarios, pagos, envíos) | Base de conocimiento |
| `chatbot/preguntas-frecuentes.md` | Respuestas a preguntas comunes | Base de conocimiento |
| `chatbot/flujo-conversacion.md` | Menú y flujo de la conversación | Flujo (flow builder) |

## Pasos

1. Completar todos los `[COMPLETAR]` con los datos reales de la tienda.
2. Crear el proyecto **America Sport** en Kapso y conectar el número de WhatsApp Business.
3. Pegar `prompt-sistema.md` en las instrucciones del agente.
4. Subir `datos-tienda.md` y `preguntas-frecuentes.md` a la base de conocimiento.
5. Armar el menú según `flujo-conversacion.md`.
6. Probar con el checklist de abajo antes de publicar.

## Checklist de pruebas

- [ ] Saluda y muestra el menú al primer mensaje
- [ ] Responde horarios, ubicación y métodos de pago correctamente
- [ ] Explica la guía de tallas
- [ ] No inventa precios ni stock que no estén en los datos
- [ ] Deriva a un asesor humano cuando se le pide
- [ ] Responde bien fuera de horario
