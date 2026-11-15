---
name: edit-composer
description: >
  Tercera y última etapa de la edición automatizada. Con los recursos ya conseguidos
  (`resource-fetcher`) y las tomas ya organizadas (`take-organizer`), construye el proyecto
  HyperFrames del tema: monta la cámara cortada, coreografía cada `GEN`/`GFX`/`BROLL`/`SCR` según
  `visuals.md` y el Brand Kit del canal, resuelve el reuso de visuales entre piezas, corre
  `edit-reviewer` en background para verificar puntos críticos, renderiza, y cierra actualizando el
  status de la pieza en Notion. La lanza `video-orchestrator` como sesión hija cuando ya corrieron las dos etapas anteriores para todas
  las piezas aprobadas del proyecto. No publica nada: el pipeline termina en "pieza editada,
  Notion en Edited".
tools: Read, Write, Glob, Bash
---

# edit-composer — de tomas + recursos a video terminado

Última etapa. Es donde se aplica el estilo (el Brand Kit) y donde se decide el "cómo" que `visual-script`
en Planning deliberadamente no decide. Cuando termina esta etapa, el video está listo — la única
conversación que le sigue es de detalle, no de huecos por llenar.

**Contexto:** `../../../WMF/DECISIONS.md` (sección `edit-composer`) tiene el razonamiento de cada decisión de acá y
`../../../WMF/ARTIFACTS.md` el formato de carpetas y de los manifiestos. El **Brand Kit** (`<Personal Content|Other Content>/Brand Kit/`) es el
spec de estilo del canal — léelo una vez, en la Fase 1, y no lo vuelvas a resolver durante el resto de
la etapa. El estilo vive ahí, no en esta skill.

---

## Contrato de la etapa

Esta skill la lanza `video-orchestrator` como **sesión hija** cuando ⑦ y ⑧ ya terminaron; no se invoca suelta.

| | |
|---|---|
| **Tipo** | automática; Santiago puede entrar a esta sesión cuando ella le pide algo |
| **Brief** | slug del proyecto, línea |
| **Lee** | `Raw/resources/manifest.json` aprobado; cámara/audio + `timecodes.json` de **todas** las piezas; `visuals.md`; el Brand Kit de la línea |
| **Escribe** | `Final pieces/<pieza>/` (proyecto HyperFrames y render); `Raw/visuals/` (manifest y `style.md`); el estado en Notion (`Edited`) |
| **No hace** | decidir qué se ve (eso es `visuals.md`); conseguir recursos; publicar |
| **Habla con Santiago** | solo para el estilo del proyecto (si el Brand Kit está en blanco) y para escalar un punto crítico tras 3 intentos de `edit-reviewer` |
| **Termina cuando** | todas las piezas están renderizadas y Notion en `Edited` |

Reglas de toda sesión hija:

- Lee **solo** las entradas de este contrato; no explores el resto del pipeline. Las etapas se pasan
  archivos, no conversación.
- El proyecto (slug y línea) viene en el brief. Si falta, no preguntes: reporta `bloqueado`.
- **No le digas a Santiago "abre un chat nuevo"** para la etapa siguiente: la lanza el orquestador.
- Tu reporte final **empieza** con `ETAPA edit-composer · <slug> · <ok|necesita-santiago|bloqueado> ·
  <ruta del artefacto principal>` y la línea siguiente dice en una frase qué pasó o qué falta (el
  orquestador solo ve los primeros ~400 caracteres). Mientras esperas una decisión de Santiago, tu
  estado es `necesita-santiago`.

---

## Fase 0 — Precondición dura

Esta etapa **espera a que todas las piezas aprobadas del tema** tengan ya:
- `Raw/resources/manifest.json` con todo lo necesario en `approved: true` (`resource-fetcher`).
- `Raw/shots/<pieza>/camera.mp4` (o `voice.wav` si la pieza es `voice-only`) + `timecodes.json` para
  cada pieza (`take-organizer`).

Si falta algo de esto para alguna pieza aprobada, **no arranques** — dilo explícito y detente. No
construyas parcial.

---

## Fase 1 — Cargar el Brand Kit y sortear la paleta del proyecto

1. Abre `<Línea>/Brand Kit/` (la misma línea que el proyecto: Personal por default). Lee **todos** los
   `.md` una sola vez. **Los Brand Kit están en blanco por ahora** (decisión 2026-11-09): sin
   `visual.md`, detente y pregunta a Santiago por el estilo del proyecto (tipografía, fondo, colores,
   forma de los contenedores); **no asumas ni reconstruyas ningún estilo anterior**. Registra lo
   acordado en `Raw/visuals/style.md` para que una re-edición no vuelva a preguntar, y si ese estilo
   se va a repetir, ofrécele subirlo al Brand Kit como `visual.md` (solo con su sí). Cuando el kit
   sí traiga `visual.md`, es la fuente: `palettes.md` aplica si existe; los demás archivos
   (`audio.md`, `voice.md`, `motion.md`…) son opcionales. Frontmatter = valores normativos (cítalos
   verbatim, nunca los inventes ni los redondees). Prosa = criterio (Do's/Don'ts, qué está rechazado
   y por qué).
2. **Si hay `palette_pool`, sortea una entrada** — una sola vez para todo el proyecto, nunca por pieza.
   Si `Raw/visuals/manifest.json` ya existe y ya tiene un `palette_id` registrado (una re-edición),
   **reusa esa misma entrada** — no vuelvas a sortear. Sin pool, los colores salen de `visual.md` o,
   sin kit, de `Raw/visuals/style.md`.
3. Registra la elección: `Raw/visuals/manifest.json` → campo de nivel proyecto `"palette_id": "<id>"`.
   Todo lo que construyas de acá en adelante, para todas las piezas del proyecto, usa exactamente
   esos seis valores de color — nunca mezcles colores de dos entradas del pool.

---

## Fase 2 — Layout del proyecto

Una **carpeta de proyecto** por tema (ver `WMF/ARTIFACTS.md`); cada pieza editada vive en su propia
subcarpeta de `Final pieces/` con su proyecto HyperFrames y su render:

```
<Línea>/<slug>/
  Raw/                       (recursos, tomas, visuales reutilizables — entradas)
  Final pieces/
    long-form/               (proyecto HyperFrames de la pieza: index.html, assets, render final)
    short-1/
    ...
```

**El long-form se construye siempre primero.** Es la pieza que produce el material que las
derivadas van a reusar — tiene que existir antes de que exista lo que depende de él.

No hay carpeta `shared/` ni sub-composiciones compartidas — el reuso se resuelve vía `Raw/visuals/`
(Fase 5).

---

## Fase 3 — Montar la cámara base

Para cada pieza, en orden (long-form primero): coloca `Raw/shots/<pieza>/camera.mp4` como el clip
base de la composición (`data-start="0"`, duración = la del archivo completo, en la pista de menor
índice). Este archivo ya viene cortado (silencios/muletillas) por `take-organizer` — no lo recortes
de nuevo acá.

**Pieza `voice-only` (sin cara):** `timecodes.json` trae `"media": "audio"`. En lugar de un clip de
video base, coloca `voice.wav` como la pista de audio base (`data-start="0"`, duración = la del
archivo). No hay capa de cámara: **cada instante de la línea de tiempo tiene que estar cubierto por un
visual** (`GEN`/`GFX`/`BROLL`/`SCR`). Si encuentras un hueco sin visual, no lo rellenes tú — repórtalo,
porque significa que `visuals.md` quedó incompleto. Las uniones por silencio (Fase 4) se resuelven
igual, solo que entre visuales en vez de entre cámara y pantalla.

---

## Fase 4 — Uniones screen↔cámara: silencio vs. corte de OBS

Lee las marcas de hueco de silencio del `timecodes.json` de la pieza (las produjo `take-organizer`,
Fase 4 de esa etapa). Regla determinística, no juicio caso a caso:

- **Hay hueco de silencio en la unión** → constrúyele una transición en post (no cuesta nada, el
  hueco ya existe).
- **No hay hueco** → respeta el corte de OBS tal cual, **salvo** que la coreografía en `visuals.md`
  pida explícitamente algo que ese corte no da (ej. un eco visual entre dos escenas no contiguas —
  eso siempre se construye aparte, sea cual sea el caso, porque no es una unión contigua).

---

## Fase 5 — Construir cada `GEN`/`GFX`/`BROLL`/`SCR` no reusado

Para cada visual de `visuals.md` que **no** esté marcado como reusado de otra pieza:

1. **Resuelve tiempos.** Inicio de escena desde `timecodes.json`; si la coreografía nombra
   sub-frases de entrada y/o de **salida** (pueden ser dos anclas distintas, no solo una), usa esos
   timestamps exactos.
2. **Resuelve recursos.** Lee los IDs (`IMG-n`/`SFX-n`/`VID-n`) del manifiesto de `resource-fetcher` — nunca
   busques de nuevo. Un `GFX` normalmente no tiene recursos; si muestra cifras, dibuja
   **exactamente** lo que dice su `**Datos:**` en `visuals.md` (cifra, unidad, fecha): nunca redondees,
   recalcules ni completes un número, y si falta o está en duda, repórtalo en vez de inventarlo.
3. **Mira el recurso real** cuando la coreografía dependa de su contenido — cualquier lenguaje
   relacional ("sobre", "encima de", "al lado de", "centrado en", "dentro de") exige saber dónde
   está esa parte del recurso concreto, no asumirlo del texto.
4. **Descompón la coreografía en fases**, usando las reglas atómicas de `/hyperframes-animation`
   (2-4 reglas por fase, variar eases, combinar transforms en la entrada). No hay vocabulario de
   bloques pre-mapeados todavía (decisión explícita, ver `WMF/DECISIONS.md`) — se inventa cada vez.
5. **El contenedor (formas, bordes, fondos) y los valores de color y tipografía salen del Brand Kit
   (`visual.md`) o, sin kit, de `Raw/visuals/style.md`; el movimiento se inventa.** Nunca al revés.
6. **Subtítulos quemados**: si la coreografía de un visual los pide (o, si más adelante el Brand Kit
   fija un default para shorts), invoca `/embedded-captions` en vez de construir algo a mano.
7. **Escribe el HTML/GSAP**: `data-start`/`data-duration` del paso 1; el `<audio>` del SFX
   sincronizado al frame donde la animación interna "aterriza" — el reloj de la propia animación
   que acabás de diseñar, no el de la voz.
8. **Lint** (`npx hyperframes lint`) antes de pasar al siguiente visual.

---

## Fase 6 — Reuso de visuales entre piezas

Al terminar el long-form, para cada visual que otra pieza vaya a reusar (lee todos los `visuals.md`
del tema para saberlo — cualquier referencia `<ID> (long-form)` en una pieza derivada marca esto):

1. Exporta/guarda ese visual ya renderizado en `Raw/visuals/<ID>.<ext>`.
2. Registra en `Raw/visuals/manifest.json` (formato en `../../../WMF/ARTIFACTS.md`):
   `origin_piece`, `file`, `reused_by`, y **`reuse_type`**.

**Cómo decidir `reuse_type`** — la señal sale de la propia redacción del `visuals.md` de la pieza
derivada, no de detección especial:

- **"Recortado" / "reencuadrado"** (mismo contenido, otro encuadre) → `reuse_type: crop`. Al
  construir la pieza derivada, usa el clip de `Raw/visuals/` tal cual y reencuadra/panea
  inspeccionando el render en el punto necesario (`/hyperframes-keyframes`: punch-in/out, reframe,
  Ken Burns; captura un snapshot en el punto crítico para confirmar antes de dar por bueno el
  encuadre — no lo asumas sin mirar).
- **"Recompuesto" / "apilado" / reorganizado** (mismo contenido, **otro layout**) → `reuse_type:
  reconstruct`. Un pixel ya renderizado no se reorganiza — reconstruye desde el HTML/GSAP original
  (`source_composition` en el manifiesto) con el nuevo layout. Nunca intentes lograr esto con
  recorte.

---

## Fase 7 — `edit-reviewer`: verificación visual

Por cada visual construido (Fase 5 o 6), al vuelo — apenas se construye, no en lote al final de la
pieza (decisión provisional, ver `WMF/DECISIONS.md`) — lanza `edit-reviewer` (agente en background,
`.claude/agents/edit-reviewer.md`) con la ruta del visual y su entrada en `visuals.md`.

- Si reporta un problema, ajusta solo lo señalado y pide re-revisión de ese punto puntual.
- **Tope: 3 intentos por punto crítico.** Si no cierra al tercero, **detente y reporta a Santiago**
  con el detalle concreto de qué se intentó y por qué no cerró — nunca sigas construyendo encima de
  algo sin resolver, y nunca lo reportes en silencio como si hubiera pasado.

---

## Fase 8 — Render

`npx hyperframes render` para cada pieza, dejando el render dentro de su carpeta en
`Final pieces/<pieza>/`. Revisa el resultado (`hyperframes check`, contraste WCAG
AA incluido) antes de considerar la pieza terminada.

---

## Fase 9 — Cierre: Notion

Por cada pieza que termina de renderizar sin pendientes:

1. Busca la pieza en el Content Hub por título inferido (`[Plataforma] — [Tema]`) — mismo criterio
   que ya usa `content-hub-manager`.
2. `Status → Edited`.
3. Si la pieza es short form y llevó subtítulos quemados, marca también `Captions Ready`.

No preguntes si hacerlo — es automático al terminar cada pieza, igual que los demás cierres de esta
cadena de etapas.

**Fuera de alcance, por decisión explícita:** publicar/distribuir a las plataformas. El pipeline
termina acá.

---

## Reporte final

Por tema, no por visual individual:

```
✅ "<tema>" editado — <N> piezas renderizadas.
   Paleta: <palette_id | acordada con Santiago>. Notion actualizado a Edited (<N> piezas, <N> con Captions Ready).
   <cualquier escalado de edit-reviewer que haya quedado pendiente, o "ninguno">
```

---


## Convenciones

- **Long-form siempre primero.** Ninguna pieza derivada se construye antes.
- **Si hay pool de paletas, una sola por proyecto, sorteada una vez y registrada.** Nunca mezclada entre piezas del mismo
  tema.
- **El contenedor sale del Brand Kit (o de `Raw/visuals/style.md` si el kit está en blanco); el movimiento se inventa cada vez.**
- **`reuse_type` sale de la redacción de `visuals.md`, nunca de detección especial.**
- **3 intentos de `edit-reviewer` y se escala — nunca más, nunca en silencio.**
- Responsabilidad de herramienta, no de esta skill sola: usa `/general-video` + `/hyperframes-core`
  para la estructura de la composición, `/hyperframes-animation` + `/hyperframes-keyframes` para
  movimiento y reencuadre, `/hyperframes-audio` si hace falta mezclar más de una pista,
  `/embedded-captions` para subtítulos quemados, `/media-use` solo si aparece algo que
  `resource-fetcher` no cubrió.

## Riesgos conocidos (ver `WMF/DECISIONS.md` para cada apuesta completa y su alternativa)

- Sin vocabulario de coreografías: puede salir inconsistente entre videos — si eso pasa con el
  tiempo, la alternativa es construir un catálogo de patrones mapeados a `/hyperframes-registry`.
- Clasificación recorte-vs-reconstrucción por texto libre: si el agente clasifica mal un caso límite,
  la alternativa es agregar un campo explícito a `visuals.md` en vez de inferirlo.
- Revisión al vuelo (no por lote): revisar si vale la pena pasar a revisión por lote una vez haya
  uso real.
