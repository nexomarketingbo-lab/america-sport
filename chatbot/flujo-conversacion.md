# Flujo de conversación – America Sport

```
Mensaje del cliente
        │
        ▼
 ¿Primer mensaje? ──sí──► Saludo + menú
        │no
        ▼
 Detectar intención
   ├─ Pregunta por un producto/modelo ─► ¿Mandó enlace/ID? ─sí─► confirmar ese modelo
   │                                       └no─► armar enlace de sección (marca+familia+deporte+género)
   │                                              → enviar enlace → "¿Te gustó alguno? Dime talla y color"
   ├─ 1 Calzado ────► ¿Hombre, mujer o niño? → enlace ?tipo=CALZADO&genero=…
   ├─ 2 Ropa ───────► ¿Hombre, mujer o niño? → enlace ?tipo=ROPA&genero=…
   ├─ 3 Accesorios ─► ¿Qué deporte? → enlace ?tipo=ACCESORIOS&grupo=…
   ├─ 4 Ofertas ────► enlace ?oferta=1
   ├─ 5 Ubicación ──► Calle Colón #130 + Maps + horarios
   ├─ 6 Asesor ─────► pasar con humano
   ├─ Cambios ──────► todas las tardes, por otro modelo; sin devoluciones
   ├─ Envíos ───────► sí hay envíos → pedir ciudad/zona → asesor confirma costo y plazo
   └─ Otra cosa ────► base de conocimiento; si no sabe → asesor
        │
        ▼
 ¿Quiere comprar? ──sí──► Tomar: nombre, modelo (enlace), talla, color, cantidad,
        │                   recojo en tienda o envío → resumen → asesor confirma stock y manda QR
        ▼
 Cierre: "¿Te ayudo con algo más? 💪"
```

## Fuera de horario
"¡Gracias por escribir a America Sport! 🙌 Ahora estamos cerrados (atendemos de lunes a sábado de 9:00 a 20:00 y domingos de 10:00 a 14:00). Mientras tanto, mira nuestro catálogo: https://americasportbolivia.com y cuéntame qué buscas, un asesor te responde apenas abramos."

## Plantilla de resumen para el asesor
```
🛒 NUEVO PEDIDO
Cliente: {nombre}
Modelo: {enlace del producto}
Talla: {talla} | Color: {color} | Cant.: {cantidad}
Entrega: {recojo en tienda / envío a {dirección}}
Pago: QR
```
