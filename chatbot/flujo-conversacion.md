# Flujo de conversación – America Sport

```
Mensaje del cliente
        │
        ▼
 ¿Primer mensaje? ──sí──► Saludo + menú principal
        │no
        ▼
 Detectar intención
   ├─ 1 Ver productos ─────► Preguntar categoría → enviar catálogo/fotos [COMPLETAR: enlace catálogo]
   ├─ 2 Precios y stock ───► Pedir producto + talla + color → derivar a asesor
   ├─ 3 Guía de tallas ────► Enviar tabla → ofrecer ayuda para elegir
   ├─ 4 Envíos y pagos ────► Responder con datos de la tienda
   ├─ 5 Ubicación/horario ─► Dirección + Maps + horarios
   ├─ 6 Asesor ────────────► Derivar a humano
   └─ Otra pregunta ───────► Responder con la base de conocimiento; si no sabe → derivar
        │
        ▼
 ¿Quiere comprar? ──sí──► Tomar pedido (nombre, producto, talla, color,
        │                   cantidad, recojo/envío, dirección) → resumen
        │                   → derivar a asesor para confirmar y cobrar
        ▼
 Cierre: "¿Te ayudo con algo más? 💪"
```

## Fuera de horario
"Gracias por escribir a America Sport 🙌 Ahora estamos fuera de horario. Un asesor te responde [COMPLETAR: mañana desde las 9:00]. Mientras tanto, cuéntame qué buscas y lo dejo anotado."

## Plantilla de resumen para el asesor
```
🛒 NUEVO PEDIDO
Cliente: {nombre}
Producto: {producto} | Talla: {talla} | Color: {color} | Cant.: {cantidad}
Entrega: {recojo / envío a {dirección}}
Notas: {notas}
```
