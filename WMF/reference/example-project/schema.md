# HyperFrames — Plan de contenido

**Slug:** example-hyperframes · **Generado:** 2026-09-13 · **Research:** digest.md

## Piezas aprobadas

| Pieza | Carpeta | Formato |
|---|---|---|
| 🎥 YouTube | `long-form/` | Long Form |
| 📱 YouTube Shorts #1 | `short-1/` | Short Form (deriva del long-form) |

> Se evaluó un post de X y se descartó: la idea no se sostiene sin la demo. Dos piezas.

## Ángulo / tesis general

HyperFrames apuesta a que el video se escribe, no se edita — y eso cambia quién puede producir
contenido, no solo qué tan rápido se produce.

---

## 🎥 YouTube — Long Form

### Hook (apertura)
Abrir con el resultado: el video que se está viendo, y la revelación de que atrás no hay timeline
sino un archivo HTML.

### Estructura

#### 1. El cuello de botella real (corta)
- Editar es el cuello de botella, no grabar
- Un cambio de guion invalida el corte

**Fuentes:** hn:47797513

#### 2. Qué hace distinto (media)
- HTML/CSS renderizado a MP4 determinístico
- Mismo input, mismo output
- Cualquier agente que sepa HTML ya sabe hacer video

**Fuentes:** hn:47797513, discovered:https://hyperframes.app

#### 3. Dónde duele (corta)
- Curva de aprendizaje si no vienes de front-end
- El render no es instantáneo

**Fuentes:** discovered:https://hyperframes.app

### Contrapuntos
- No reemplaza editar footage real. Se muestra, no se esquiva.

### Cierre
Si el video es código, se versiona y se automatiza como código. ¿Qué pasa cuando el que produce el
video no es una persona?

---

## 📱 YouTube Shorts #1

**Ángulo:** el determinismo como la parte que importa. Deriva de la sección 2.
**Puntos clave:** mismo input, mismo output; por eso se automatiza.
**Fuentes:** hn:47797513
**Hook:** "Este video no se editó. Se compiló."

---

## Preguntas abiertas / huecos
- Nadie documentó cuánto tarda un render largo en máquina local.
