# America Sport – Chatbot de WhatsApp (Kapso)

Contenido del asistente virtual de **America Sport** (tienda de ropa deportiva) para cargar en [Kapso](https://app.kapso.ai).

- **Cuenta Kapso:** `nexo.marketing.bo+americasport@gmail.com`
- **Estado:** casi listo — falta definir envíos (`[COMPLETAR]` en datos y preguntas frecuentes).

## Archivos

| Archivo | Para qué sirve | Dónde va en Kapso |
|---|---|---|
| `chatbot/prompt-sistema.md` | Personalidad y reglas del asistente | Instrucciones / system prompt del agente |
| `chatbot/datos-tienda.md` | Datos de la tienda (horarios, pagos, cambios) | Base de conocimiento |
| `chatbot/enlaces-catalogo.md` | Cómo armar enlaces a modelos y secciones de la web | Base de conocimiento |
| `chatbot/preguntas-frecuentes.md` | Respuestas a preguntas comunes | Base de conocimiento |
| `chatbot/flujo-conversacion.md` | Menú y flujo de la conversación | Flujo (flow builder) |

## Pasos

1. Completar la información de envíos (`[COMPLETAR]`).
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
