# -*- coding: utf-8 -*-
"""stock.json -> stock.js (datos limpios y listos para la web).

Anade marca normalizada, tipo (coche/moto/industrial) y valores numericos para
poder filtrar y ordenar. No inventa ningun dato: solo normaliza los que ya
estaban en la web original.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

MARCAS = {
    "MERCEDES-BENZ": "Mercedes-Benz", "MERCEDES": "Mercedes-Benz",
    "MERCEDES-AMG": "Mercedes-Benz", "BMW": "BMW", "AUDI": "Audi",
    "VOLKSWAGEN": "Volkswagen", "SEAT": "SEAT", "PORSCHE": "Porsche",
    "LAND-ROVER": "Land Rover", "LAND": "Land Rover", "RANGE": "Land Rover",
    "LAMBORGHINI": "Lamborghini", "MASERATI": "Maserati", "MINI": "MINI",
    "RENAULT": "Renault", "PEUGEOT": "Peugeot", "CITROEN": "Citroën",
    "CITROËN": "Citroën", "DACIA": "Dacia", "FORD": "Ford", "OPEL": "Opel",
    "TOYOTA": "Toyota", "INFINITI": "Infiniti", "SMART": "smart",
    "DUCATI": "Ducati", "KAWASAKI": "Kawasaki", "CAN-AM": "Can-Am",
    "FIAT": "Fiat", "AUTOCARAVANA": "Fiat", "NISSAN": "Nissan",
    "IVECO": "Iveco", "MERCEDES-BENZ,": "Mercedes-Benz",
}
MOTOS = ("DUCATI", "KAWASAKI", "CAN-AM", "YAMAHA", "HONDA CB", "PANIGALE", "Z900")


def num(txt):
    if not txt:
        return None
    d = re.sub(r"[^\d]", "", txt)
    return int(d) if d else None


def marca_de(titulo):
    prim = titulo.split()[0].upper().rstrip(",")
    if prim in MARCAS:
        return MARCAS[prim]
    dos = " ".join(titulo.split()[:2]).upper()
    for k, v in MARCAS.items():
        if dos.startswith(k):
            return v
    return titulo.split()[0].title()


stock = json.load(open(os.path.join(BASE, "stock.json"), encoding="utf-8"))
salida = []
for c in stock:
    t = c["titulo"]
    tipo = ("industrial" if c["categoria"] == "industrial"
            else "moto" if any(m in t.upper() for m in MOTOS) else "coche")
    contado, financiado = num(c["precio_contado"]), num(c["precio_financiado"])
    salida.append({
        "titulo": t,
        "marca": marca_de(t),
        "tipo": tipo,
        "anio": num(c["anio"]),
        "mes": c["mes"],
        "km": num(c["km"]),
        "precio": contado,
        # solo se muestra si de verdad es distinto del precio al contado
        "financiado": financiado if financiado and financiado != contado else None,
        "vendido": c["vendido"],
        "foto": c.get("foto"),
        "ficha": c["ficha"],
    })

salida.sort(key=lambda c: (c["vendido"], -(c["precio"] or 0)))
js = "window.STOCK = %s;\n" % json.dumps(salida, ensure_ascii=False, separators=(",", ":"))
open(os.path.join(BASE, "stock.js"), "w", encoding="utf-8").write(js)

disp = [c for c in salida if not c["vendido"]]
print("total %d | disponibles %d | vendidos %d" % (
    len(salida), len(disp), len(salida) - len(disp)))
print("tipos disponibles:", {t: sum(1 for c in disp if c["tipo"] == t)
                             for t in ("coche", "moto", "industrial")})
print("marcas:", sorted({c["marca"] for c in disp}))
print("con precio financiado distinto:", sum(1 for c in disp if c["financiado"]))
print("stock.js: %.1f KB" % (len(js.encode("utf-8")) / 1024))
