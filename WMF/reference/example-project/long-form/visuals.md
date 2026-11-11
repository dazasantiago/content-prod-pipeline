# HyperFrames — Visuales · Long Form

**Slug:** example-hyperframes · **Pieza:** long-form · **Generado:** 2026-09-13
**Estado:** aprobado 2026-09-13
**Guion:** script.en.md (aprobado 2026-09-13) · 6 escenas

---

## Escena 1 — Hook
> "There's no timeline. There's no track. There's this — an HTML file."

### CAM-1
**Coreografía:** plano fijo, Santiago hablando de frente. Arranca el video sobre él.

### SCR-1
**Coreografía:** entra ocupando toda la pantalla justo en "There's this". Se queda quieto mientras
se scrollea lentamente hasta el bloque de la escena 2 del HTML. No hay movimiento de cámara.
**Preparación:** VS Code abierto en `composition.html` de este mismo proyecto, scrolleado hasta el
bloque `<section class="clip">`. Barra lateral oculta (tiene rutas personales). Fuente grande: esta
captura se reutiliza recortada a vertical en el short.

---

## Escena 2 — The real bottleneck
> "you rewrite one line — and now the cut you spent two hours on is wrong"

### CAM-2
**Coreografía:** plano fijo hablando. Sostiene casi toda la escena.

### GEN-1
**Coreografía:** aparece brevemente la imagen de alguien editando en su computadora. Entra el logo
de IA desde arriba y se posa sobre su cabeza; la persona se queda quieta. Sale junto con la línea
"you don't publish".
**Recursos:** `IMG-1` persona editando video en su computadora · `IMG-2` logo de IA genérico ·
`SFX-1` pop corto al aterrizar el logo

---

## Escena 3 — Same input, same output
> "Same input, same output. Every time."

### CAM-3
**Coreografía:** plano fijo hablando, ritmo más rápido que las escenas anteriores.

### SCR-2
**Coreografía:** la terminal corre el render hasta terminar y aparece el MP4. Inmediatamente se
corre otra vez y termina igual. Las dos corridas se ven completas, sin cortar el tiempo de render.
**Preparación:** terminal con `hyperframes render` sobre este mismo proyecto. Correrlo dos veces
seguidas. **No acelerar ni cortar**: la escena 5 dice que el render tarda, y cortarlo lo
contradiría. Fuente grande, se reutiliza en vertical.
**Texto en pantalla:** "same input → same output"

---

## Escena 4 — Anything that writes HTML
> "anything that can write HTML can make one"

### CAM-4
**Coreografía:** plano fijo hablando.

### GFX-1
**Coreografía:** tres elementos aparecen uno por uno, encadenados de izquierda a derecha: guion,
HTML, MP4. Cada uno entra cuando la narración llega a él. Quedan los tres en pantalla al cerrar.
**Recursos:** ninguno — se dibuja con código en edición.

---

## Escena 5 — Where it still hurts
> "long compositions take real time to render"

### CAM-5
**Coreografía:** plano fijo hablando. Sostiene la escena completa, incluido el contrapunto.

### BROLL-1
**Coreografía:** entra de fondo, detrás de él o a pantalla completa según el montaje, mientras
habla del tiempo de render. Acelerado. Sale antes del contrapunto.
**Recursos:** `VID-1` barra de progreso de un render largo avanzando

---

## Escena 6 — Payoff and close
> "not that it was easy, but that it was repeatable"

### SCR-1 *(ya descrito en Escena 1)*
**Coreografía:** vuelve exactamente igual que en la escena 1, mismo encuadre y mismo punto del
archivo. El eco visual es el punto: cierra el loop que abrió.

### CAM-6
**Coreografía:** plano fijo hablando. La pregunta final va sin nada más en pantalla.

---

## Escenas sin especificar
- Ninguna. Las seis escenas tienen al menos un visual especificado.

## Pendientes
- Confirmar que correr el render dos veces no cambia el nombre del archivo de salida. Si cambia, no
  se ve el punto del determinismo en SCR-2.
