# -*- coding: utf-8 -*-
"""Construye la web: stock.js + una pagina por vehiculo + sitemap.

Todo sale de stock.json y fichas.json (datos reales de MR Automocion).
Ningun dato se inventa: lo que no esta, no se escribe.

  python construir-web.py
"""
import html
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DOMINIO = "https://mrautomocion.com"

# VISTA PREVIA: mientras la web viva en GitHub Pages (y no en el dominio real del
# cliente), se pide a Google que NO la indexe. Si dos webs iguales estan en
# Google, se hacen la competencia entre ellas y pierde la del cliente.
# Al publicar de verdad en mrautomocion.com, poner esto en False y reconstruir.
VISTA_PREVIA = True
TEL, TEL_TXT = "+34677369936", "+34 677 36 99 36"
WA = "34602452593"
DIR = "C. Bubión, Nave 46 · Pol. Juncaril · Peligros (Granada)"

stock = json.load(open(os.path.join(BASE, "stock.json"), encoding="utf-8"))
fichas = {f["ficha"]: f for f in json.load(open(os.path.join(BASE, "fichas.json"), encoding="utf-8"))}

MARCAS = {
    "MERCEDES-BENZ": "Mercedes-Benz", "MERCEDES": "Mercedes-Benz", "MERCEDES-AMG": "Mercedes-Benz",
    "BMW": "BMW", "AUDI": "Audi", "VOLKSWAGEN": "Volkswagen", "SEAT": "SEAT", "PORSCHE": "Porsche",
    "LAND-ROVER": "Land Rover", "LAND": "Land Rover", "RANGE": "Land Rover",
    "LAMBORGHINI": "Lamborghini", "MASERATI": "Maserati", "MINI": "MINI", "RENAULT": "Renault",
    "PEUGEOT": "Peugeot", "CITROEN": "Citroën", "CITROËN": "Citroën", "DACIA": "Dacia",
    "FORD": "Ford", "OPEL": "Opel", "TOYOTA": "Toyota", "INFINITI": "Infiniti", "SMART": "smart",
    "DUCATI": "Ducati", "KAWASAKI": "Kawasaki", "CAN-AM": "Can-Am", "FIAT": "Fiat",
    "AUTOCARAVANA": "Fiat", "NISSAN": "Nissan", "IVECO": "Iveco",
}
MOTOS = ("DUCATI", "KAWASAKI", "CAN-AM", "PANIGALE", "Z900")


def num(t):
    if not t:
        return None
    d = re.sub(r"[^\d]", "", str(t))
    return int(d) if d else None


def marca_de(t):
    p = t.split()[0].upper().rstrip(",")
    if p in MARCAS:
        return MARCAS[p]
    for k, v in MARCAS.items():
        if " ".join(t.split()[:2]).upper().startswith(k):
            return v
    return t.split()[0].title()


def e(t):
    return html.escape(str(t if t is not None else ""), quote=True)


def euros(n):
    return "{:,}".format(n).replace(",", ".") + " €" if n else "Consultar"


def miles(n):
    return "{:,}".format(n).replace(",", ".") if n else None


# ---------------------------------------------------------------- datos
coches = []
for c in stock:
    f = fichas.get(c["ficha"], {})
    contado, financiado = num(c["precio_contado"]), num(c["precio_financiado"])
    t = c["titulo"]
    coches.append({
        "titulo": t,
        "slug": c.get("slug"),
        "marca": marca_de(t),
        "tipo": ("industrial" if c["categoria"] == "industrial"
                 else "moto" if any(m in t.upper() for m in MOTOS) else "coche"),
        "anio": num(c["anio"]),
        "mes": c["mes"],
        "km": num(c["km"]) or f.get("km"),
        "precio": contado,
        "financiado": financiado if financiado and financiado != contado else None,
        "vendido": c["vendido"],
        "foto": c.get("foto"),
        "fotos": f.get("fotos") or [],
        "combustible": f.get("combustible"),
        "cambio": f.get("cambio"),
        "potencia": f.get("potencia"),
        "garantia": f.get("garantia"),
        "iva": f.get("iva"),
        "descripcion": f.get("descripcion"),
        "original": c["ficha"],
    })
coches.sort(key=lambda c: (c["vendido"], -(c["precio"] or 0)))
disponibles = [c for c in coches if not c["vendido"]]

ligero = []
for c in coches:
    d = {k: c[k] for k in ("titulo", "slug", "marca", "tipo", "anio", "mes", "km", "precio",
                           "financiado", "vendido", "foto", "combustible", "cambio",
                           "potencia", "garantia")}
    d["nfotos"] = len(c["fotos"]) or None
    ligero.append(d)
open(os.path.join(BASE, "stock.js"), "w", encoding="utf-8").write(
    "window.STOCK = %s;\n" % json.dumps(ligero, ensure_ascii=False, separators=(",", ":")))

# ---------------------------------------------------------------- plantilla
CABECERA = """<div class="tira">
  <div class="env">
    <span class="ocultar-movil">Lunes a viernes · <b>07:00 – 15:00</b></span>
    <span>Pol. Juncaril, Peligros <b>(Granada)</b></span>
    <a href="tel:{tel}"><b>{tel_txt}</b></a>
  </div>
</div>
<header id="cabecera">
  <div class="env">
    <a class="logo" href="../index.html"><img src="../medios/logo.svg" alt="MR Automoción" width="200" height="44"></a>
    <nav id="menu">
      <a href="../index.html#stock">Stock</a>
      <a href="../index.html#box">El box</a>
      <a href="../index.html#vendidos">Vendidos</a>
      <a href="../index.html#contacto">Contacto</a>
    </nav>
    <div class="acciones">
      <a class="btn btn-linea" href="https://wa.me/{wa}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="btn btn-oro" href="tel:{tel}">Llamar</a>
      <button class="menu-movil" id="botonMenu" aria-label="Abrir menú" aria-expanded="false">
        <svg width="20" height="14" viewBox="0 0 20 14" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M0 1h20M0 7h20M0 13h20"/></svg>
      </button>
    </div>
  </div>
</header>""".format(tel=TEL, tel_txt=TEL_TXT, wa=WA)

PIE = """<footer>
  <div class="env">
    <div>
      <img src="../medios/logo.svg" alt="MR Automoción" style="height:40px;margin-bottom:12px">
      <div>© 2026 MR Automoción · {dir}</div>
    </div>
    <div class="legales">
      <a href="{d}/aviso-legal/" target="_blank" rel="noopener">Aviso Legal</a>
      <a href="{d}/politica-de-privacidad/" target="_blank" rel="noopener">Política de Privacidad</a>
      <a href="{d}/politica-de-cookies/" target="_blank" rel="noopener">Política de Cookies</a>
    </div>
  </div>
</footer>
<div class="barra-movil">
  <a class="llamar" href="tel:{tel}">Llamar</a>
  <a class="wasap" href="https://wa.me/{wa}" target="_blank" rel="noopener">WhatsApp</a>
</div>""".format(dir=DIR, d=DOMINIO, tel=TEL, wa=WA)


def mensaje_wa(c):
    t = "Hola, me interesa el " + c["titulo"]
    if c["precio"]:
        t += " (" + euros(c["precio"]) + ")"
    return "https://wa.me/%s?text=%s" % (WA, __import__("urllib.parse", fromlist=["x"]).quote(
        t + " que tenéis en la web. ¿Sigue disponible?"))


def parrafos(texto):
    if not texto:
        return ""
    trozos = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¡¿])", texto)
    bloques, actual = [], ""
    for t in trozos:
        actual += (" " if actual else "") + t
        if len(actual) > 290:
            bloques.append(actual)
            actual = ""
    if actual:
        bloques.append(actual)
    return "".join("<p>%s</p>" % e(b) for b in bloques)


def parecidos(c):
    otros = [o for o in disponibles if o["slug"] != c["slug"]]
    mismos = [o for o in otros if o["marca"] == c["marca"]]
    resto = sorted([o for o in otros if o not in mismos],
                   key=lambda o: abs((o["precio"] or 0) - (c["precio"] or 0)))
    return (mismos + resto)[:3]


def tarjeta_mini(c):
    return ('<a class="coche" href="%s.html"><div class="marco">'
            '<img src="../%s" alt="%s" loading="lazy" width="1000" height="750"></div>'
            '<div class="cuerpo"><h3>%s</h3><div class="precio">'
            '<span class="grande">%s</span></div></div></a>') % (
        e(c["slug"]), e(c["foto"]), e(c["titulo"]), e(c["titulo"]), euros(c["precio"]))


def pagina(c):
    fotos = c["fotos"] or ([c["foto"]] if c["foto"] else [])
    principal = fotos[0] if fotos else c["foto"]
    desc_corta = re.sub(r"\s+", " ", (c["descripcion"] or c["titulo"]))[:158]

    especificaciones = [
        ("Marca", c["marca"]),
        ("Modelo", c["titulo"]),
        ("Año", ("%s %s" % (c["mes"], c["anio"])).strip() if c["anio"] else None),
        ("Kilómetros", miles(c["km"]) + " km" if c["km"] else None),
        ("Combustible", c["combustible"]),
        ("Cambio", c["cambio"]),
        ("Potencia", "%s CV" % c["potencia"] if c["potencia"] else None),
        ("Garantía", c["garantia"]),
        ("IVA", c["iva"]),
    ]
    filas = "".join("<tr><th>%s</th><td>%s</td></tr>" % (e(k), e(v))
                    for k, v in especificaciones if v)

    chips = []
    if c["anio"]:
        chips.append(("%s %s" % (c["mes"] or "", c["anio"])).strip())
    if c["km"]:
        chips.append(miles(c["km"]) + " km")
    for x in (c["combustible"], c["cambio"]):
        if x:
            chips.append(x)
    if c["potencia"]:
        chips.append("%s CV" % c["potencia"])

    miniaturas = "".join(
        '<button class="mini%s" data-i="%d" aria-label="Foto %d"><img src="../%s" alt="" loading="lazy" width="200" height="150"></button>'
        % (" activa" if i == 0 else "", i, i + 1, e(f)) for i, f in enumerate(fotos))

    jsonld = {
        "@context": "https://schema.org", "@type": "Car",
        "name": c["titulo"], "brand": {"@type": "Brand", "name": c["marca"]},
        "image": ["%s/coche/%s" % (DOMINIO, os.path.basename(f)) for f in fotos[:6]],
        "description": re.sub(r"\s+", " ", c["descripcion"] or "")[:600],
        "offers": {"@type": "Offer", "price": c["precio"] or 0, "priceCurrency": "EUR",
                   "availability": "https://schema.org/InStock",
                   "seller": {"@type": "AutoDealer", "name": "MR Automoción",
                              "telephone": TEL, "address": DIR}},
    }
    if c["anio"]:
        jsonld["productionDate"] = str(c["anio"])
    if c["km"]:
        jsonld["mileageFromOdometer"] = {"@type": "QuantitativeValue",
                                         "value": c["km"], "unitCode": "KMT"}
    if c["combustible"]:
        jsonld["fuelType"] = c["combustible"]
    if c["cambio"]:
        jsonld["vehicleTransmission"] = c["cambio"]
    if c["potencia"]:
        jsonld["vehicleEngine"] = {"@type": "EngineSpecification",
                                   "enginePower": {"@type": "QuantitativeValue",
                                                   "value": c["potencia"], "unitText": "CV"}}

    return """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} de ocasión en Granada · MR Automoción</title>
<meta name="description" content="{desc}">
<meta name="HandheldFriendly" content="true">
<meta name="MobileOptimized" content="width">
<meta name="theme-color" content="#0b0b0d">
<link rel="icon" href="../medios/favicon.png">
<link rel="canonical" href="{dominio}/coche/{slug}.html">
<meta property="og:title" content="{titulo} · MR Automoción">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="../{principal}">
<meta property="og:type" content="product">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Barlow:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../estilos.css">
<script type="application/ld+json">{jsonld}</script>
</head>
<body class="pagina-ficha">
{cabecera}

<div class="env miga"><a href="../index.html">Inicio</a> › <a href="../index.html#stock">Stock</a> › <span>{titulo}</span></div>

<div class="env ficha">
  <div class="galeria">
    <div class="visor-principal" id="visorPrincipal">
      <img id="fotoGrande" src="../{principal}" alt="{titulo}" width="1400" height="1050" fetchpriority="high">
      <button class="flecha izq" id="anterior" aria-label="Foto anterior">‹</button>
      <button class="flecha der" id="siguiente" aria-label="Foto siguiente">›</button>
      <span class="cuenta"><b id="numFoto">1</b> / {total}</span>
      <button class="ampliar" id="ampliar" aria-label="Ver a pantalla completa">⤢</button>
    </div>
    <div class="miniaturas" id="miniaturas">{miniaturas}</div>
  </div>

  <aside class="panel">
    <p class="sello">{marca}{sello_tipo}</p>
    <h1>{titulo}</h1>
    <div class="datos">{chips}</div>
    <div class="bloque-precio">
      <div class="precio"><span class="grande">{precio}</span></div>
      {financiado}
      {avales}
    </div>
    <div class="acciones-coche">
      <a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener">Preguntar por WhatsApp</a>
      <a class="btn btn-oro" href="tel:{tel}">Llamar ahora</a>
    </div>
    <p class="nota-panel">Disponible en nuestras instalaciones de {dirtxt}.
      Avísanos antes de venir y lo tenemos preparado.</p>
    <button class="compartir" id="compartir">Compartir este vehículo</button>
  </aside>
</div>

<div class="env ficha-abajo">
  <div class="descripcion">
    <h2>Sobre este vehículo</h2>
    {descripcion}
  </div>
  <div class="tabla-tecnica">
    <h2>Ficha técnica</h2>
    <table>{filas}</table>
  </div>
</div>

<section class="otros">
  <div class="env">
    <div class="cabecera-seccion"><p class="sello">Quizá también te encaje</p>
      <h2>Otros vehículos disponibles</h2></div>
    <div class="rejilla">{parecidos}</div>
    <div style="text-align:center;margin-top:34px">
      <a class="btn btn-linea" href="../index.html#stock">Ver todo el stock</a>
    </div>
  </div>
</section>

{pie}

<div class="lightbox" id="lightbox">
  <button class="cerrar" id="cerrarLb" aria-label="Cerrar">✕</button>
  <button class="flecha izq" id="lbAnterior" aria-label="Anterior">‹</button>
  <img id="lbFoto" src="" alt="{titulo}">
  <button class="flecha der" id="lbSiguiente" aria-label="Siguiente">›</button>
  <span class="cuenta"><b id="lbNum">1</b> / {total}</span>
</div>

<script>
window.FOTOS = {fotos_js};
</script>
<script src="../ficha.js"></script>
</body>
</html>""".format(
        titulo=e(c["titulo"]), desc=e(desc_corta), dominio=DOMINIO, slug=e(c["slug"]),
        principal=e(principal), jsonld=json.dumps(jsonld, ensure_ascii=False),
        cabecera=CABECERA, pie=PIE, total=len(fotos), miniaturas=miniaturas,
        marca=e(c["marca"]),
        sello_tipo=" · Industrial" if c["tipo"] == "industrial" else (" · Moto" if c["tipo"] == "moto" else ""),
        chips="".join("<span>%s</span>" % e(x) for x in chips),
        precio=euros(c["precio"]),
        financiado=('<div class="fin-linea">Precio financiado: <b>%s</b></div>' % euros(c["financiado"])) if c["financiado"] else "",
        avales="".join('<div class="aval">%s</div>' % e(x) for x in
                       filter(None, [("Garantía de " + c["garantia"]) if c["garantia"] else None,
                                     ("IVA: " + c["iva"]) if c["iva"] else None])),
        wa=mensaje_wa(c), tel=TEL, dirtxt=e(DIR),
        descripcion=parrafos(c["descripcion"]), filas=filas,
        parecidos="".join(tarjeta_mini(o) for o in parecidos(c)),
        fotos_js=json.dumps(["../" + f for f in fotos], ensure_ascii=False))


# ---------------------------------------------------------------- escribir
destino = os.path.join(BASE, "coche")
os.makedirs(destino, exist_ok=True)
for c in disponibles:
    open(os.path.join(destino, c["slug"] + ".html"), "w", encoding="utf-8").write(pagina(c))

# --- versionado de css/js: el navegador no se queda con la version vieja ---
def sello(nombre):
    ruta = os.path.join(BASE, nombre)
    if not os.path.isfile(ruta):
        return ""
    import hashlib
    return hashlib.md5(open(ruta, "rb").read()).hexdigest()[:8]


versiones = {n: sello(n) for n in ("estilos.css", "ficha.js", "stock.js")}


def versiona(texto):
    for nombre, v in versiones.items():
        if not v:
            continue
        texto = re.sub(r'(["\'/])(\.\./)?%s(\?v=[0-9a-f]+)?(["\'])'
                       % re.escape(nombre),
                       lambda m: "%s%s%s?v=%s%s" % (m.group(1), m.group(2) or "", nombre, v, m.group(4)),
                       texto)
    return texto


for nombre in ["index.html"] + ["coche/" + f for f in os.listdir(destino) if f.endswith(".html")]:
    ruta = os.path.join(BASE, nombre.replace("/", os.sep))
    original = open(ruta, encoding="utf-8").read()
    nuevo = versiona(original)
    if nuevo != original:
        open(ruta, "w", encoding="utf-8").write(nuevo)

urls = ['<url><loc>%s/</loc><priority>1.0</priority></url>' % DOMINIO]
urls += ['<url><loc>%s/coche/%s.html</loc><priority>0.8</priority></url>' % (DOMINIO, c["slug"])
         for c in disponibles]
open(os.path.join(BASE, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n'
    % "\n".join(urls))
if VISTA_PREVIA:
    open(os.path.join(BASE, "robots.txt"), "w", encoding="utf-8").write(
        "# Vista previa: no indexar (la web buena es %s)\nUser-agent: *\nDisallow: /\n" % DOMINIO)
else:
    open(os.path.join(BASE, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % DOMINIO)

# la etiqueta noindex en cada pagina (robots.txt solo no siempre basta)
for nombre in ["index.html"] + ["coche/" + f for f in os.listdir(destino) if f.endswith(".html")]:
    ruta = os.path.join(BASE, nombre.replace("/", os.sep))
    doc = open(ruta, encoding="utf-8").read()
    doc = doc.replace('<meta name="robots" content="noindex, nofollow">\n', "")
    if VISTA_PREVIA:
        doc = doc.replace("<title>", '<meta name="robots" content="noindex, nofollow">\n<title>', 1)
    open(ruta, "w", encoding="utf-8").write(doc)

sin_fotos = [c["titulo"] for c in disponibles if len(c["fotos"]) < 2]
print("paginas de coche: %d" % len(disponibles))
print("fotos por ficha: media %.1f" % (sum(len(c["fotos"]) for c in disponibles) / len(disponibles)))
print("con descripcion propia: %d/%d" % (sum(1 for c in disponibles if c["descripcion"]), len(disponibles)))
print("con garantia: %d/%d" % (sum(1 for c in disponibles if c["garantia"]), len(disponibles)))
print("fichas con menos de 2 fotos: %d %s" % (len(sin_fotos), sin_fotos[:4]))
