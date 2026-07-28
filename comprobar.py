# -*- coding: utf-8 -*-
"""Comprobador de la web: revisa las 43 páginas y todos sus recursos.

Trabaja sobre los archivos, así que no hace falta tener el servidor arrancado
y tarda segundos.

  python comprobar.py
"""
import json
import os
import re
import urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))

paginas = ["index.html"] + ["coche/" + f for f in sorted(os.listdir(os.path.join(BASE, "coche")))
                            if f.endswith(".html")]
rotos, sin_alt, sin_titulo, recursos = [], [], [], set()

for p in paginas:
    ruta = os.path.join(BASE, p.replace("/", os.sep))
    doc = open(ruta, encoding="utf-8").read()
    carpeta = os.path.dirname(p)

    if not re.search(r"<title>[^<]{10,}</title>", doc):
        sin_titulo.append(p)
    for img in re.findall(r"<img[^>]*>", doc):
        if not re.search(r'\balt="', img):
            sin_alt.append((p, img[:70]))

    for ref in re.findall(r'(?:src|href)="([^"#][^"]*)"', doc):
        if ref.startswith(("http", "mailto:", "tel:", "//", "data:", "#")):
            continue
        if "' +" in ref or "+ '" in ref:
            continue                      # trozo de plantilla dentro del JavaScript, no es un enlace
        limpio = urllib.parse.unquote(ref.split("#")[0].split("?")[0])   # fuera ancla y ?v=
        if not limpio:
            continue
        destino = os.path.normpath(os.path.join(carpeta, limpio))
        recursos.add((p, destino))

for p, destino in sorted(recursos):
    if not os.path.exists(os.path.join(BASE, destino)):
        rotos.append((p, destino))

stock = json.loads(open(os.path.join(BASE, "stock.js"), encoding="utf-8")
                   .read().replace("window.STOCK = ", "").rstrip(";\n"))
disponibles = [c for c in stock if not c["vendido"]]
faltan_paginas = [c["titulo"] for c in disponibles
                  if not os.path.isfile(os.path.join(BASE, "coche", (c["slug"] or "") + ".html"))]
faltan_fotos = [c["titulo"] for c in stock
                if not c["foto"] or not os.path.isfile(os.path.join(BASE, c["foto"].replace("/", os.sep)))]

home = open(os.path.join(BASE, "index.html"), encoding="utf-8").read()
contacto = {
    "teléfono +34 677 36 99 36": "tel:+34677369936" in home,
    "whatsapp 602 452 593": "wa.me/34602452593" in home,
    "email ventas@mrautomocion.com": "ventas@mrautomocion.com" in home,
    "dirección C. Bubión": "Bubi" in home,
    "horario 07:00 – 15:00": "07:00" in home,
}

pesados = []
for carpeta, _, ficheros in os.walk(os.path.join(BASE, "medios")):
    for f in ficheros:
        ruta = os.path.join(carpeta, f)
        kb = os.path.getsize(ruta) / 1024
        if kb > 400:
            pesados.append((os.path.relpath(ruta, BASE), round(kb)))

print("páginas: %d | recursos referenciados: %d" % (len(paginas), len(recursos)))
print("\n--- RESULTADO ---")
print("recursos que no existen: %d" % len(rotos))
for p, d in rotos[:12]:
    print("   %s -> %s" % (p, d))
print("imágenes sin alt: %d %s" % (len(sin_alt), sin_alt[:3]))
print("páginas sin <title>: %s" % (sin_titulo or "ninguna"))
print("vehículos disponibles sin página: %s" % (faltan_paginas or "ninguno"))
print("vehículos sin foto: %s" % (faltan_fotos or "ninguno"))
print("archivos de más de 400 KB: %s" % (pesados or "ninguno"))
print("datos de contacto en portada:")
for k, v in contacto.items():
    print("   %s  %s" % ("OK " if v else "MAL", k))
print("\nvehículos disponibles: %d | páginas de coche: %d"
      % (len(disponibles), len(paginas) - 1))
