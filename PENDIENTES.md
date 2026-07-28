# MR Automoción — lo que hay que preguntar o decidir

Todo lo que aparece en la web nueva sale de su web actual. **No se ha inventado ni un dato.**
Esta lista es lo que falta o lo que no cuadra, para preguntárselo al cliente.

---

## 1. Descuadres detectados en SUS propios datos (revisar antes de publicar)

En cuatro vehículos, los kilómetros del listado no coinciden con los que dice la descripción
de la propia ficha. La web nueva muestra **los del listado**. Hay que confirmar cuál es el bueno:

| Vehículo | Km en el listado | Km en su descripción |
|---|---|---|
| Mercedes-Benz Clase S 580 4Matic 503CV 2024 | 56.000 km | 53.000 km |
| MINI Cooper D | 191.151 km | 200.000 km |
| Range Rover Autobiography | 186.500 km | 182.502 km |
| BMW X6 M Competition xDrive | 98.000 km | 95.300 km |

En un coche de segunda mano el kilometraje es un dato con consecuencias legales. Que lo revisen.

## 2. Datos que faltan en algunas fichas

- **Sin garantía indicada:** AUDI S4 (B5) 2.7 V6 Bi-Turbo Quattro 265 CV. Los otros 41 tienen
  "1 Año". ¿Este también?
- **Sin IVA indicado:** BMW 420i Gran Coupé 184CV 2022, Audi A5 Sportback 40 TFSI, CAN-AM Maveric
  Trail DPS 800T. ¿Deducible o no deducible?

## 3. Cosas que harían vender más y que no están en su web actual

Nada de esto se puede inventar: hay que pedírselo.

- **Reseñas de Google.** No hay ni una opinión en toda la web. Es lo que más convence al comprar
  un coche caro. Hace falta el enlace a su ficha de Google Business.
- **Años de experiencia / coches vendidos.** La franja de confianza dice "39 ya entregados"
  (contados de su web). Si llevan X años o venden X coches al año, es un número mucho más potente.
- **¿Aceptan tu coche como parte del pago?** Casi todos los compradores lo preguntan. Si lo hacen,
  merece una sección propia.
- **Financiación: ¿con qué entidad y desde qué cuota?** Hoy solo aparece "Precio financiado" en
  11 vehículos, sin explicar nada. Poner "desde X €/mes" multiplica las llamadas.
- **¿Entregan fuera de Granada?** Si envían a toda España, hay que decirlo bien grande.
- **Etiqueta medioambiental DGT** (B, C, ECO, CERO) por vehículo. Los iconos están en su
  WordPress pero no vienen asociados a cada coche en el listado; habría que exportarlos.

## 4. Técnico, antes de publicar

- **El formulario** hoy abre WhatsApp con el mensaje escrito (funciona y no pierde ningún
  contacto), pero **no envía email**. Hay que conectarlo a su correo o a su CRM.
- **Páginas legales.** Aviso legal, privacidad y cookies enlazan a las de su WordPress actual.
  Si se sustituye la web entera, hay que migrar esas tres páginas.
- **Cookies.** La web nueva no lleva analítica ni cookies de terceros, así que hoy no necesita
  banner. En cuanto se añada Google Analytics, sí hará falta.
- **Cómo se actualiza el stock.** Hoy la web es una foto del stock a 28 de julio de 2026. Ver
  `README.md`: con su WordPress funcionando, la web nueva se regenera entera en unos minutos.
  Hay que decidir si mantienen WordPress como panel de carga o quieren otra cosa.

## 5. Lo que sí está resuelto y verificado

- 42 vehículos disponibles con precio, año, km, combustible, cambio, potencia y garantía reales.
- 969 fotos reales suyas (23 por vehículo de media), optimizadas de ~2 MB a ~74 KB cada una.
- Las 42 descripciones son las que ellos mismos escribieron, íntegras.
- Teléfono, WhatsApp, email, dirección y horario verificados contra su web original.
- 39 vehículos vendidos como prueba social.
- Datos estructurados para Google (schema.org Car + Offer) en cada ficha, sitemap y robots.txt.
