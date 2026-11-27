# Enlaces del catálogo – americasportbolivia.com

El bot debe **responder siempre con un enlace**: el del modelo exacto si se conoce, y si no, el de la sección más específica posible.

## Cómo se arman los enlaces
Base: `https://americasportbolivia.com/index.php`

| Qué | Formato | Ejemplo |
|---|---|---|
| Producto específico | `?codigo={ID}` | https://americasportbolivia.com/index.php?codigo=14810 |
| Tipo | `?tipo=CALZADO` / `ROPA` / `ACCESORIOS` | https://americasportbolivia.com/index.php?tipo=CALZADO |
| Producto (familia) | `?familia={FAMILIA}` | https://americasportbolivia.com/index.php?familia=ZAPATILLAS |
| Deporte | `?grupo={DEPORTE}` | https://americasportbolivia.com/index.php?grupo=FUTBOL |
| Marca | `?marca={MARCA}` | https://americasportbolivia.com/index.php?marca=NIKE |
| Género | `?genero={GÉNERO}` | https://americasportbolivia.com/index.php?genero=MUJER |
| Ofertas | `?oferta=1` | https://americasportbolivia.com/index.php?oferta=1 |

**Los filtros se pueden combinar con `&`** para dar un enlace más preciso:
- Zapatillas Nike: https://americasportbolivia.com/index.php?marca=NIKE&familia=ZAPATILLAS
- Zapatillas de mujer: https://americasportbolivia.com/index.php?familia=ZAPATILLAS&genero=MUJER
- Chuteras de fútbol para niños: https://americasportbolivia.com/index.php?grupo=FUTBOL&familia=CHUTERAS&genero=NI%C2%A5OS

**Reglas técnicas:**
- Los espacios se escriben `%20` → `?marca=NEW%20BALANCE`, `?marca=UNDER%20ARMOUR`
- La Ñ se escribe `%C2%A5` → niños: `?genero=NI%C2%A5OS`, muñequeras: `?familia=MU%C2%A5EQUERAS`
- Los valores van en MAYÚSCULAS y tal como están escritos abajo (la web tiene algunas faltas de ortografía, por ejemplo `RUNING`; hay que copiarlas tal cual).
- Si el cliente envía un enlace o un ID de producto (`codigo=14810`), usar ese.

## Tipos
- Calzado: https://americasportbolivia.com/index.php?tipo=CALZADO
- Ropa: https://americasportbolivia.com/index.php?tipo=ROPA
- Accesorios: https://americasportbolivia.com/index.php?tipo=ACCESORIOS
- Ofertas: https://americasportbolivia.com/index.php?oferta=1

## Género
- Hombre: https://americasportbolivia.com/index.php?genero=HOMBRE
- Mujer: https://americasportbolivia.com/index.php?genero=MUJER
- Unisex: https://americasportbolivia.com/index.php?genero=HOMBRE/MUJER
- Niños: https://americasportbolivia.com/index.php?genero=NI%C2%A5OS

## Deportes (`grupo`)
| Deporte | Enlace |
|---|---|
| Fútbol | https://americasportbolivia.com/index.php?grupo=FUTBOL |
| Futsal | https://americasportbolivia.com/index.php?grupo=FUTSAL |
| Running | https://americasportbolivia.com/index.php?grupo=RUNNING (también `RUNING`) |
| Básquet | https://americasportbolivia.com/index.php?grupo=BASQUET |
| Vóley | https://americasportbolivia.com/index.php?grupo=VOLEIBOL |
| Tenis | https://americasportbolivia.com/index.php?grupo=TENIS |
| Raqueta (frontón/squash) | https://americasportbolivia.com/index.php?grupo=RAQUET |
| Ping pong | https://americasportbolivia.com/index.php?grupo=PING%20PONG |
| Gimnasio | https://americasportbolivia.com/index.php?grupo=GIMNASIO |
| Entrenamiento | https://americasportbolivia.com/index.php?grupo=ENTRENAMIENT |
| Boxeo | https://americasportbolivia.com/index.php?grupo=BOXEO |
| Natación | https://americasportbolivia.com/index.php?grupo=NATACION |
| Casual | https://americasportbolivia.com/index.php?grupo=CASUAL |
| Sport | https://americasportbolivia.com/index.php?grupo=SPORT |
| De vestir | https://americasportbolivia.com/index.php?grupo=DE%20VESTIR (también `VESTIR`) |
| Protectores | https://americasportbolivia.com/index.php?grupo=PROTECTOR |

## Familias más pedidas
**Calzado:** ZAPATILLAS · CHUTERAS · CHUTERA · BOTIN · BOTAS · CALZADOS · SANDALIAS · ZANDALIAS · CHINELAS · CROCS · ALPARGATAS · PANTUFLAS
**Ropa:** POLERAS · POLERAS%20EQUI (poleras de equipo) · SHORT · BERMUDAS · BUSOS · CONJUNTOS · CHAMARRAS · PANTALONES · CALZAS · SOLERAS · BLUSAS · BOXER · MEDIAS
**Accesorios:** PELOTAS · MOCHILAS · BOLSOS · GORRAS · GORROS · GUANTES · CANILLERAS · RODILLERAS · TOBILLERAS · CODERAS · MU%C2%A5EQUERAS · VINCHAS · BOTELLAS · MANCUERNAS · PESAS · CUERDAS · RAQUETAS · LENTES · RELOJES · BILLETERAS · CINTURONES · CARTERAS · PLANTILLAS · INFLADORES · VENDAS · TOHALLAS · PATINES

Ejemplos: https://americasportbolivia.com/index.php?familia=CHUTERAS · https://americasportbolivia.com/index.php?familia=PELOTAS · https://americasportbolivia.com/index.php?familia=MOCHILAS

## Marcas principales
ADIDAS · NIKE · PUMA · REEBOK · NEW%20BALANCE · UNDER%20ARMOUR · ASICS · FILA · UMBRO · PENALTY · KELME · LOTTO · OLYMPIKUS · VANS · ALL%20STAR · CROCS · HAVAIANAS · IPANEMA · ON%20RUNNING · MIKASA · MOLTEN · WILSON · SPALDING · SPEEDO · TOTTO · KIPLING · LEVIS · LACOSTE · TOMMY · REUSCH

Ejemplos: https://americasportbolivia.com/index.php?marca=ADIDAS · https://americasportbolivia.com/index.php?marca=PENALTY · https://americasportbolivia.com/index.php?marca=ON%20RUNNING

## Ejemplos de respuesta
- "¿Tienen chuteras Nike?" → "¡Sí! Aquí están todas las chuteras Nike 👟 https://americasportbolivia.com/index.php?marca=NIKE&familia=CHUTERAS"
- "Busco zapatillas para correr de mujer" → https://americasportbolivia.com/index.php?grupo=RUNNING&familia=ZAPATILLAS&genero=MUJER
- "¿Tienen pelotas de vóley?" → https://americasportbolivia.com/index.php?grupo=VOLEIBOL&familia=PELOTAS
- "¿Qué ofertas hay?" → https://americasportbolivia.com/index.php?oferta=1
