# -*- coding: utf-8 -*-
"""Descarga la ficha de cada vehiculo y saca TODOS sus datos y fotos reales.

De cada ficha de WordPress obtiene: combustible, cambio, potencia, garantia, IVA,
la descripcion escrita por MR Automocion y la galeria completa de fotos.
No inventa nada: si un campo no esta en la ficha, se queda vacio.

Uso:  python extraer-fichas.py [--solo-disponibles]
Salida: fichas.json
"""
import concurrent.futures as futuros
import html
import json
import os
import re
import sys
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}

COMBUSTIBLES = ("gasolina", "diésel", "diesel", "híbrido", "hibrido", "eléctrico",
                "electrico", "glp", "gnc", "hev", "phev")
CAMBIOS = ("automático", "automatico", "manual", "secuencial")


def limpia(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t).replace("​", "")
    return re.sub(r"\s+", " ", t).strip()


def campos_de(doc):
    """Valores en orden de aparicion, clasificados por su forma (no por posicion)."""
    crudos = [limpia(c) for c in re.findall(
        r'class="jet-listing-dynamic-field__content"[^>]*>(.*?)</div>', doc, re.S)]
    crudos = [c for c in crudos if c]
    f = {"combustible": None, "cambio": None, "potencia": None, "garantia": None,
         "iva": None, "descripcion": None, "km": None}
    visto_combustible = False
    for v in crudos:
        bajo = v.lower()
        if len(v) > 140 and not f["descripcion"]:
            f["descripcion"] = v
        elif any(c in bajo for c in COMBUSTIBLES) and not f["combustible"] and len(v) < 30:
            f["combustible"] = v
            visto_combustible = True
        elif any(c in bajo for c in CAMBIOS) and not f["cambio"] and len(v) < 30:
            f["cambio"] = v
        elif re.search(r"\b(año|años|meses|mes)\b", bajo) and len(v) < 25 and not f["garantia"]:
            f["garantia"] = v
        elif "deducible" in bajo and not f["iva"]:
            f["iva"] = v
        elif re.fullmatch(r"[\d.]+", v):
            n = int(v.replace(".", ""))
            if n > 1900 and n < 2100:
                continue                      # es el año, ya lo tenemos del listado
            if not visto_combustible and not f["km"] and n > 900:
                f["km"] = n                   # los km van antes del combustible
            elif not f["potencia"] and n < 1500:
                f["potencia"] = n
    return f


def galeria_de(doc):
    urls = re.findall(r'data-elementor-open-lightbox="yes"[^>]*href="([^"]+wp-content/uploads/[^"]+)"', doc)
    if not urls:                              # por si el carrusel cambia de forma
        urls = re.findall(r'class="swiper-slide-image"[^>]*src="([^"]+)"', doc)
        urls = [re.sub(r"-\d+x\d+(\.\w+)$", r"\1", u) for u in urls]
    fuera = ("logo", "favicon", "etiqueta", "banner", "icono")
    limpio = []
    for u in urls:
        if any(x in u.lower() for x in fuera):
            continue
        if u not in limpio:
            limpio.append(u)
    return limpio


def una(coche):
    try:
        req = urllib.request.Request(coche["ficha"], headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            doc = r.read().decode("utf-8", "replace")
    except Exception as e:                                        # noqa: BLE001
        return {"ficha": coche["ficha"], "error": str(e)[:90]}
    d = campos_de(doc)
    d["ficha"] = coche["ficha"]
    d["titulo"] = coche["titulo"]
    d["galeria"] = galeria_de(doc)
    return d


stock = json.load(open(os.path.join(BASE, "stock.json"), encoding="utf-8"))
if "--solo-disponibles" in sys.argv:
    stock = [c for c in stock if not c["vendido"]]

with futuros.ThreadPoolExecutor(max_workers=6) as ex:
    fichas = list(ex.map(una, stock))

errores = [f for f in fichas if f.get("error")]
buenas = [f for f in fichas if not f.get("error")]
json.dump(buenas, open(os.path.join(BASE, "fichas.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

fotos = sum(len(f["galeria"]) for f in buenas)
print("fichas: %d | errores: %d" % (len(buenas), len(errores)))
for e in errores[:5]:
    print("  !", e["ficha"], e["error"])
print("fotos de galeria: %d (media %.1f por coche)" % (fotos, fotos / max(len(buenas), 1)))
for campo in ("combustible", "cambio", "potencia", "garantia", "iva", "descripcion", "km"):
    print("  %-12s %d/%d" % (campo, sum(1 for f in buenas if f.get(campo)), len(buenas)))
