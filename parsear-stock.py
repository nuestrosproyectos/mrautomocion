# -*- coding: utf-8 -*-
"""Parsea el stock de MR Automocion desde el HTML descargado -> stock.json

No intenta equilibrar etiquetas (el HTML de WordPress no lo permite): trocea el
documento por el marcador de cada tarjeta y saca los campos con expresiones
regulares dentro de cada trozo.
"""
import html
import json
import os
import re
import urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(BASE, "original")

MESES = ("ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT",
         "NOV", "DIC", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
         "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE")


def texto(fragmento):
    fragmento = re.sub(r"<[^>]+>", " ", fragmento)
    return re.sub(r"\s+", " ", html.unescape(fragmento)).strip()


def trocear(doc):
    marcas = [m.start() for m in re.finditer(r'<div[^>]*class="[^"]*jet-listing-grid__item', doc)]
    trozos = []
    for i, ini in enumerate(marcas):
        fin = marcas[i + 1] if i + 1 < len(marcas) else min(
            [x for x in (doc.find("</footer>", ini), len(doc)) if x > 0] or [len(doc)])
        trozos.append(doc[ini:fin])
    return trozos


def campos(trozo):
    return [texto(m) for m in re.findall(
        r'class="jet-listing-dynamic-field__content"[^>]*>(.*?)</div>', trozo, re.S)]


def normaliza(trozo, categoria):
    cs = [c for c in campos(trozo) if c]
    if not cs:
        return None
    titulo, mes, anio, km, precios = cs[0], None, None, None, []
    for c in cs[1:]:
        limpio = c.replace("/", "").strip()
        if limpio.upper()[:3] in [m[:3] for m in MESES] and not mes and not limpio[0].isdigit():
            mes = limpio.capitalize()
        elif re.fullmatch(r"[12]\.?\d{3}", limpio) and not anio:
            anio = limpio.replace(".", "")
        elif "km" in c.lower():
            km = c
        elif "€" in c:
            precios.append(c)
    img = re.search(r'<img[^>]+src="([^"]+)"', trozo)
    ficha = re.search(r'href="([^"]*/(?:venta|industrial)/[^"]+)"', trozo)
    return {
        "titulo": titulo,
        "mes": mes,
        "anio": anio,
        "km": km,
        "precio_financiado": precios[0] if precios else None,
        "precio_contado": precios[1] if len(precios) > 1 else (precios[0] if precios else None),
        "vendido": bool(re.search(r">\s*VENDIDO", trozo, re.I)),
        "img_origen": img.group(1) if img else None,
        "ficha": ficha.group(1) if ficha else None,
        "categoria": categoria,
    }


def clave(url):
    if not url:
        return None
    p = urllib.parse.urlparse(url)
    return (p.netloc.replace("www.", ""), p.path)


inv = json.load(open(os.path.join(ORIG, "INVENTARIO.json"), encoding="utf-8"))
mapa = {clave(i["origen"]): i["archivo"] for i in inv["imagenes"]}

coches, vistos = [], set()
for archivo, categoria in (("pagina-2.html", "venta"), ("pagina-3.html", "industrial"),
                           ("pagina-1.html", "venta")):
    ruta = os.path.join(ORIG, "fuente", archivo)
    if not os.path.isfile(ruta):
        continue
    for trozo in trocear(open(ruta, encoding="utf-8").read()):
        c = normaliza(trozo, categoria)
        if not c or not c["titulo"] or not c["ficha"]:
            continue
        clave_ficha = clave(c["ficha"])
        if clave_ficha in vistos:
            continue
        vistos.add(clave_ficha)
        c["img"] = mapa.get(clave(c["img_origen"]))
        coches.append(c)

falta = [c["titulo"] for c in coches if not c["img"]]
sin_precio = [c["titulo"] for c in coches if not c["precio_contado"] and not c["vendido"]]

json.dump(coches, open(os.path.join(BASE, "stock.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("coches: %d (venta %d | industrial %d)" % (
    len(coches),
    sum(1 for c in coches if c["categoria"] == "venta"),
    sum(1 for c in coches if c["categoria"] == "industrial")))
print("vendidos: %d | disponibles: %d" % (
    sum(1 for c in coches if c["vendido"]), sum(1 for c in coches if not c["vendido"])))
print("sin foto local: %d %s" % (len(falta), falta[:6]))
print("disponibles sin precio: %d %s" % (len(sin_precio), sin_precio[:6]))
