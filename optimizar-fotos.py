# -*- coding: utf-8 -*-
"""Optimiza las fotos originales para la web nueva.

Por cada coche del stock genera:
  medios/coches/<slug>.webp   ~1000 px de ancho, para la tarjeta y el visor
Y actualiza stock.json con la ruta nueva ('foto') y el slug.
"""
import json
import os
import re
import subprocess
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(BASE, "original")
SALIDA = os.path.join(BASE, "medios", "coches")
os.makedirs(SALIDA, exist_ok=True)


def slugify(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return t[:60] or "coche"


stock = json.load(open(os.path.join(BASE, "stock.json"), encoding="utf-8"))
usados, hechas, fallos = set(), 0, []

for c in stock:
    if not c.get("img"):
        continue
    slug = slugify(c["titulo"])
    n = 1
    while slug in usados:
        slug = "%s-%d" % (slugify(c["titulo"]), n)
        n += 1
    usados.add(slug)
    c["slug"] = slug
    entrada = os.path.join(ORIG, c["img"].replace("/", os.sep))
    destino = os.path.join(SALIDA, slug + ".webp")
    c["foto"] = "medios/coches/%s.webp" % slug
    if os.path.isfile(destino):
        continue
    # 1000 px de ancho, sin agrandar las que ya son pequenas
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", entrada,
         "-vf", "scale='min(1000,iw)':-2", "-quality", "72", destino],
        capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(destino):
        fallos.append((c["titulo"], r.stderr.strip()[:120]))
    else:
        hechas += 1

json.dump(stock, open(os.path.join(BASE, "stock.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

pesos = [os.path.getsize(os.path.join(SALIDA, f)) for f in os.listdir(SALIDA)]
print("optimizadas: %d | fallos: %d" % (hechas, len(fallos)))
for t, e in fallos[:5]:
    print("  !", t, "->", e)
if pesos:
    print("peso medio: %.0f KB | mayor: %.0f KB | total: %.1f MB"
          % (sum(pesos) / len(pesos) / 1024, max(pesos) / 1024, sum(pesos) / 1048576))
