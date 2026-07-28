# -*- coding: utf-8 -*-
"""Descarga y optimiza las galerias reales de cada vehiculo disponible.

Por cada coche disponible baja hasta MAX fotos de su ficha y las convierte a
webp de 1400 px (galeria) para que carguen rapido. Actualiza fichas.json con
las rutas locales.
"""
import concurrent.futures as futuros
import json
import os
import re
import subprocess
import unicodedata
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
GAL = os.path.join(BASE, "medios", "galeria")
TEMP = os.path.join(BASE, ".descargas")
MAX = 24
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
os.makedirs(GAL, exist_ok=True)
os.makedirs(TEMP, exist_ok=True)


def slugify(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()[:60] or "coche"


stock = {c["ficha"]: c for c in json.load(open(os.path.join(BASE, "stock.json"), encoding="utf-8"))}
fichas = json.load(open(os.path.join(BASE, "fichas.json"), encoding="utf-8"))


def una_foto(tarea):
    url, destino = tarea
    if os.path.isfile(destino):
        return destino
    tmp = os.path.join(TEMP, os.path.basename(destino) + os.path.splitext(url)[1][:5])
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=45) as r, open(tmp, "wb") as f:
            f.write(r.read())
    except Exception:                                             # noqa: BLE001
        return None
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp,
                        "-vf", "scale='min(1400,iw)':-2", "-quality", "70", destino],
                       capture_output=True)
    try:
        os.remove(tmp)
    except OSError:
        pass
    return destino if os.path.isfile(destino) else None


tareas, indice = [], {}
for f in fichas:
    coche = stock.get(f["ficha"])
    if not coche or coche["vendido"] or not f.get("galeria"):
        continue
    slug = coche.get("slug") or slugify(coche["titulo"])
    locales = []
    for i, url in enumerate(f["galeria"][:MAX]):
        destino = os.path.join(GAL, "%s-%02d.webp" % (slug, i + 1))
        tareas.append((url, destino))
        locales.append("medios/galeria/%s-%02d.webp" % (slug, i + 1))
    indice[f["ficha"]] = locales

print("a descargar: %d fotos de %d coches" % (len(tareas), len(indice)))
with futuros.ThreadPoolExecutor(max_workers=10) as ex:
    hechas = list(ex.map(una_foto, tareas))
fallos = sum(1 for h in hechas if not h)

for f in fichas:
    rutas = indice.get(f["ficha"], [])
    f["fotos"] = [r for r in rutas if os.path.isfile(os.path.join(BASE, r.replace("/", os.sep)))]
json.dump(fichas, open(os.path.join(BASE, "fichas.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

pesos = [os.path.getsize(os.path.join(GAL, x)) for x in os.listdir(GAL)]
print("descargadas %d | fallos %d" % (len(pesos), fallos))
if pesos:
    print("peso medio %.0f KB | total %.1f MB" % (sum(pesos) / len(pesos) / 1024,
                                                  sum(pesos) / 1048576))
