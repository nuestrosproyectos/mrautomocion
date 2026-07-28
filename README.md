# MR Automoción — web nueva

Web estática (HTML puro): carga muy rápido, se puede subir a cualquier hosting y no se rompe.
Todo el contenido sale de su web actual `mrautomocion.com`.

## Ver la web

Doble clic en **`Abrir web.bat`**. Se abre en el navegador en `http://localhost:4832`.
Para cerrarla, cierra la ventana negra.

## Qué hay dentro

| Archivo o carpeta | Qué es |
|---|---|
| `index.html` | La portada: hero, buscador de stock, box, vendidos y contacto |
| `coche/` | Una página por vehículo (42), con su galería y su ficha técnica |
| `estilos.css` · `ficha.js` · `stock.js` | Diseño y funcionamiento (compartidos por todas las páginas) |
| `medios/` | Fotos optimizadas, vídeos, logo |
| `original/` | Copia de seguridad de la web antigua: textos, fotos y datos tal cual estaban |
| `PENDIENTES.md` | Lo que hay que preguntar al cliente antes de publicar |

## Actualizar el stock cuando entren o salgan coches

Mientras su WordPress siga funcionando, la web nueva se regenera sola. Cuatro comandos, en orden,
desde esta carpeta:

```bash
python extraer-web.py https://mrautomocion.com ./original --paginas 6
```

```bash
python parsear-stock.py
```

```bash
python extraer-fichas.py
```

```bash
python descargar-galerias.py
```

```bash
python construir-web.py
```

El último es el que reconstruye las 42 páginas, el `sitemap.xml` y el buscador. Las fotos que ya
estaban descargadas no se vuelven a bajar, así que la actualización tarda poco.

Para comprobar que no se ha roto nada (con la web abierta):

```bash
python comprobar.py
```

## Publicar

1. Empaquetar con rutas correctas para servidores Linux:

```bash
python C:/Users/tradu/.claude/skills/creador-webs/scripts/empaquetar-web.py
```

2. Subir el .zip al hosting y descomprimir en la carpeta pública.

**Antes de publicar, leer `PENDIENTES.md`.** Hay cuatro coches con los kilómetros descuadrados en
su propia web y el formulario todavía no envía correo.

## Medios generados con IA (Higgsfield)

Solo se ha usado IA donde no engaña a nadie:

- `medios/hero.mp4` — su Lamborghini Huracán real, con movimiento de cámara. 10 créditos.
- `medios/box.mp4` — su box real con el Porsche Cayenne. 10 créditos.
- `medios/detalles/` — recortes macro de una foto suya ampliada a 4K. 4 créditos (2 ampliaciones).

**Total: 24 créditos.** No se ha generado ninguna foto falsa de ningún vehículo en venta: las
fotos de coches son todas suyas.
