/* Ficha de vehículo: galería, visor a pantalla completa y menú. */
(function () {
  "use strict";
  var fotos = window.FOTOS || [];
  var i = 0;
  var $ = function (s) { return document.querySelector(s); };
  var grande = $("#fotoGrande"), num = $("#numFoto"), marco = $("#visorPrincipal");
  var lb = $("#lightbox"), lbFoto = $("#lbFoto"), lbNum = $("#lbNum");
  var minis = Array.prototype.slice.call(document.querySelectorAll(".mini"));

  function pon(n) {
    if (!fotos.length) return;
    i = (n + fotos.length) % fotos.length;
    grande.src = fotos[i];
    num.textContent = i + 1;
    lbNum.textContent = i + 1;
    if (lb.hasAttribute("open")) lbFoto.src = fotos[i];
    minis.forEach(function (m, k) { m.classList.toggle("activa", k === i); });
    /* un tercio de las fotos son verticales: el marco se adapta a cada una
       para que se vean lo más grandes posible sin recortar nada */
    var ajusta = function () {
      marco.classList.toggle("vertical", grande.naturalHeight > grande.naturalWidth);
    };
    if (grande.complete && grande.naturalWidth) ajusta();
    else grande.addEventListener("load", ajusta, { once: true });
    /* Nada de scrollIntoView aquí: las miniaturas se ven todas y mover el foco
       arrastraba la página entera hacia arriba al cambiar de foto. */
    // precarga la siguiente para que no parpadee
    if (fotos[i + 1]) { var p = new Image(); p.src = fotos[i + 1]; }
  }

  minis.forEach(function (m) {
    m.addEventListener("click", function () { pon(+m.dataset.i); });
  });
  $("#anterior").addEventListener("click", function (ev) { ev.stopPropagation(); pon(i - 1); });
  $("#siguiente").addEventListener("click", function (ev) { ev.stopPropagation(); pon(i + 1); });

  /* Con el dedo, tocar la foto pasa a la siguiente (mitad derecha) o a la anterior
     (mitad izquierda). Ampliar es cosa del botón ⤢. Con ratón se mantiene el
     clic para ampliar, que es lo que espera quien va con ordenador. */
  function esTactil() {
    return matchMedia("(hover: none) and (pointer: coarse)").matches;
  }
  var vieneDeDeslizar = false;

  function abre() {
    lbFoto.src = fotos[i];
    lb.setAttribute("open", "");
    document.body.style.overflow = "hidden";
  }
  function cierra() { lb.removeAttribute("open"); document.body.style.overflow = ""; }

  function tocada(ev, zona) {
    if (vieneDeDeslizar) { vieneDeDeslizar = false; return true; }
    if (!esTactil()) return false;
    var caja = zona.getBoundingClientRect();
    pon(ev.clientX - caja.left > caja.width / 2 ? i + 1 : i - 1);
    return true;
  }

  $("#ampliar").addEventListener("click", function (ev) { ev.stopPropagation(); abre(); });
  $("#visorPrincipal").addEventListener("click", function (ev) {
    if (tocada(ev, this)) return;
    abre();
  });
  $("#cerrarLb").addEventListener("click", cierra);
  $("#lbAnterior").addEventListener("click", function (ev) { ev.stopPropagation(); pon(i - 1); });
  $("#lbSiguiente").addEventListener("click", function (ev) { ev.stopPropagation(); pon(i + 1); });
  lb.addEventListener("click", function (ev) {
    if (ev.target === lb) { cierra(); return; }          // tocar el fondo cierra siempre
    if (ev.target !== lbFoto) return;
    if (tocada(ev, lbFoto)) return;                      // con el dedo, la foto pasa
    cierra();
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") cierra();
    if (ev.key === "ArrowLeft") pon(i - 1);
    if (ev.key === "ArrowRight") pon(i + 1);
  });

  /* deslizar con el dedo */
  [$("#visorPrincipal"), lb].forEach(function (zona) {
    var x0 = null;
    zona.addEventListener("touchstart", function (ev) { x0 = ev.touches[0].clientX; }, { passive: true });
    zona.addEventListener("touchend", function (ev) {
      if (x0 === null) return;
      var dx = ev.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 45) {
        pon(dx < 0 ? i + 1 : i - 1);
        vieneDeDeslizar = true;      // que el clic posterior no haga nada más
      }
      x0 = null;
    }, { passive: true });
  });

  /* compartir el vehículo */
  var btnCompartir = $("#compartir");
  if (btnCompartir) {
    btnCompartir.addEventListener("click", function () {
      var datos = { title: document.title, text: document.querySelector("h1").textContent,
                    url: location.href };
      if (navigator.share) {
        navigator.share(datos).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(location.href).then(function () {
          btnCompartir.textContent = "Enlace copiado ✓";
          setTimeout(function () { btnCompartir.textContent = "Compartir este vehículo"; }, 2600);
        });
      } else {
        window.open("https://wa.me/?text=" + encodeURIComponent(datos.text + " " + location.href),
                    "_blank", "noopener");
      }
    });
  }

  /* cabecera y menú */
  var cab = $("#cabecera");
  addEventListener("scroll", function () { cab.classList.toggle("pegado", scrollY > 20); }, { passive: true });
  var boton = $("#botonMenu");
  if (boton) {
    boton.addEventListener("click", function () {
      var abierto = $("#menu").classList.toggle("abierto");
      this.setAttribute("aria-expanded", abierto ? "true" : "false");
    });
  }

  pon(0);
})();
