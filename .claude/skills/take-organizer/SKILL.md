---
name: take-organizer
description: >
  Segunda etapa de la edición automatizada. Toma las tomas crudas de `Raw/shots/` (grabadas con
  OBS, cámara + screen ya compuestos en vivo cuando corresponde) y las organiza contra el guion y
  los visuales aprobados: transcribe, respeta las marcas de voz "discarded"/"final", ubica cada
  escena por fuzzy match, detecta huecos de silencio en las uniones, corta silencios/muletillas, y
  produce un archivo de cámara continuo por pieza más un mapa de tiempos. La lanza `video-orchestrator` como sesión hija cuando Santiago dice "ya grabé". Requiere archivos en
  `Raw/shots/`; `resource-fetcher` puede seguir corriendo en paralelo.
tools: Read, Write, Glob, Bash
---

# take-organizer — de tomas crudas a cámara organizada con tiempos

Segunda etapa. La más algorítmica de las tres — casi todo acá es transformación determinística
sobre una transcripción, no juicio creativo. Los únicos puntos donde se pregunta a Santiago están
marcados explícitamente abajo; todo lo demás se resuelve solo.

**Contexto:** `../../../WMF/DECISIONS.md` (sección Etapa 2) tiene el razonamiento completo, incluida la
nota de por qué no hace falta sincronizar cámara y screen por separado (Santiago graba con OBS, ya
vienen compuestos). El formato de `timecodes.json` está en `../../../WMF/ARTIFACTS.md`.

---

## Contrato de la etapa

Esta skill la lanza `video-orchestrator` como **sesión hija** cuando Santiago dice "ya grabé"; no se invoca suelta.

| | |
|---|---|
| **Tipo** | automática; Santiago puede entrar a esta sesión cuando ella le pide algo |
| **Brief** | slug del proyecto, línea |
| **Lee** | `Raw/shots/*`; de cada pieza, `script.en.md` y `visuals.md` aprobados (en Other Content, el guion de `Raw/source/`); `schema.md` |
| **Escribe** | por pieza, `Raw/shots/<pieza>/camera.mp4` (o `voice.wav`) y `timecodes.json` |
| **No hace** | montar visuales; decidir estilo; elegir entre tomas sin marca sin que Santiago lo decida |
| **Habla con Santiago** | solo para tomas ambiguas sin marca (con su crítica de entrega) |
| **Termina cuando** | todas las piezas tienen cámara/audio continuo y mapa de tiempos |

Reglas de toda sesión hija:

- Lee **solo** las entradas de este contrato; no explores el resto del pipeline. Las etapas se pasan
  archivos, no conversación.
- El proyecto (slug y línea) viene en el brief. Si falta, no preguntes: reporta `bloqueado`.
- **No le digas a Santiago "abre un chat nuevo"** para la etapa siguiente: la lanza el orquestador.
- Tu reporte final **empieza** con `ETAPA take-organizer · <slug> · <ok|necesita-santiago|bloqueado> ·
  <ruta del artefacto principal>` y la línea siguiente dice en una frase qué pasó o qué falta (el
  orquestador solo ve los primeros ~400 caracteres). Mientras esperas una decisión de Santiago, tu
  estado es `necesita-santiago`.

---

## Fase 0 — Cargar contexto

1. El brief trae el **slug** y la **línea** del proyecto: úsalos tal cual. Si faltan, reporta `bloqueado`.
2. Lista `Raw/shots/*` — uno o varios archivos. Puede ser un archivo por escena, o uno solo con
   varias escenas y varios intentos seguidos. No asumas nada de la cantidad de archivos.
   **Los archivos pueden ser video o solo audio.** Lee el `**Delivery:**` del `script.en.md` de la
   pieza: `on-camera` espera video, `voice-only` (sin cara) espera audio. Si el tipo de archivo no
   coincide con el `Delivery` declarado, avísalo antes de seguir. Todo el algoritmo de abajo
   (transcripción → marcas → fuzzy match → huecos → corte) funciona igual sobre audio: lo único que
   cambia es la salida de la Fase 6.
3. Para cada pieza aprobada del tema (lee `Planning/content/<slug>/schema.md` para la lista), carga
   su `script.en.md` y su `visuals.md` aprobados. Si alguno no existe o no dice `approved`, avisa y
   pregunta si igual quiere avanzar con esa pieza — un guion o visual todavía en movimiento
   desincroniza los tiempos.

---

## Fase 1 — Transcribir cada archivo crudo

Transcribe cada archivo de `Raw/shots/` con timestamps por palabra. Usa la transcripción disponible
en el toolchain de HyperFrames (`npx hyperframes transcribe <archivo>` o el motor que exponga
`media-use`) — no reconstruyas un pipeline de Whisper a mano si ya hay un comando para esto.

Guarda la transcripción cruda de cada archivo (con timestamps) en un lugar de trabajo temporal
dentro del proyecto — no hace falta que sea un artefacto final, solo que sobreviva el resto de esta
etapa para no re-transcribir si algo falla a mitad de camino.

---

## Fase 2 — Marcas de control y segmentación

Escanea cada transcripción buscando ocurrencias **aisladas** (rodeadas de pausa, no parte de una
oración del guion) de las palabras **"discarded"** y **"final"**. Cada ocurrencia cierra el
segmento que la precede (desde la marca anterior, o el inicio del archivo, hasta esta).

Clasifica cada segmento resultante:

- **`discarded`** → se descarta. No importa qué tan bien haya salido — es la palabra de Santiago,
  no un juicio de calidad.
- **`final`** → se usa, sin más chequeo. No evalúes si "podría ser mejor" — la marca de Santiago
  pesa más que cualquier heurística tuya.
- **Sin marca:**
  - Compara el contenido del segmento contra las líneas-ancla de `visuals.md` (Fase 3). Si es el
    **único candidato** para esa escena y la transcripción se ve **limpia** — sin muletillas, sin
    reinicios o repeticiones de una frase (señal de que se cortó y volvió a intentar), y cubre la
    línea-ancla completa sin truncar — **auto-selecciónalo**. Anótalo en el reporte final como
    "auto-elegido, sin marca, entrega limpia" — nunca en silencio.
  - Si hay **más de un candidato sin marca** para la misma escena, **no elijas** — preséntaselos a
    Santiago con la diferencia entre ellos (qué cambia de uno a otro) y espera su elección.
    Aquí actúas como **crítico de entrega**: por cada candidato di, en una línea, qué funciona y qué
    no (claridad, ritmo, energía, tropiezos, si la línea clave aterriza) y, si él lo pide, cuál
    recomendarías y por qué. La decisión sigue siendo suya. Con marca (`discarded`/`final`) no
    comentas nada: su palabra cierra el tema.

---

## Fase 3 — Ubicar cada segmento por fuzzy match

Para cada pieza, recorre sus escenas en `visuals.md` en orden. Cada escena trae una línea-ancla
(la cita entre `>`) del guion. Compara esa línea contra el contenido de los segmentos transcritos —
sin exigir coincidencia exacta (Santiago no lee el guion palabra por palabra: cambia un artículo, se
come una palabra, repite algo). Quédate con el segmento más parecido por encima de un umbral
razonable de similitud.

**Anclas de sub-frase.** Si la coreografía de un visual en `visuals.md` nombra una frase específica
como disparador ("entra justo en 'There's this'", "sale junto con la línea 'you don't publish'"),
ubica el timestamp exacto de esa frase dentro del segmento de la escena — no solo el inicio de la
escena. **Un mismo visual puede tener dos anclas de sub-frase distintas: una de entrada y otra de
salida.** No asumas que hay una sola.

---

## Fase 4 — Uniones entre visuales: marca de silencio

Por cada unión entre dos visuales contiguos dentro de la misma pieza (el fin de uno y el comienzo
del siguiente, sean del tipo que sean — cámara sola, o cámara+screen ya compuestos por OBS), mide si
hay un hueco de silencio ahí y su duración. Esta marca no decide nada en esta etapa — solo se
registra en el mapa de tiempos. La decisión de qué hacer con ella (construir una transición o
respetar el corte tal cual) es de `edit-composer`.

---

## Fase 5 — Cortar silencios y muletillas

Sobre el segmento ya elegido por escena, corta silencios y muletillas dentro del propio segmento
(no en las uniones — eso es la Fase 4). Usa la skill `video-use` para esto — es su especialidad, no
la reconstruyas acá.

---

## Fase 6 — Ensamblar y producir, por pieza

1. **Un archivo continuo** por pieza, dentro de un área de trabajo de la etapa:
   - `on-camera` → `Raw/shots/<pieza>/camera.mp4` (video).
   - `voice-only` → `Raw/shots/<pieza>/voice.wav` (solo audio; no existe cámara).

   No se parte en un archivo por escena — dentro de una pieza normalmente se graban varias escenas
   seguidas sin cortar, y la etapa siguiente necesita una base continua sobre la cual montar encima.
   Para cortar silencios y muletillas en audio puro, usa la ruta de audio de `video-use` (o `ffmpeg`
   directo) — **no está probada todavía** contra una grabación real; si algo falla, repórtalo.
   El `timecodes.json` lleva un campo de nivel pieza `"media": "video" | "audio"` y `cut_file`
   apunta al archivo que corresponda.
2. **El mapa de tiempos**: `Raw/shots/<pieza>/timecodes.json` — formato exacto en
   `../../../WMF/ARTIFACTS.md`. Por escena: ventana de tiempo, ancla de escena, qué toma se
   eligió y por qué (marca explícita o auto-selección — es el rastro de auditoría), y las anclas de
   sub-frase con su `role: entry | exit`. Entre escenas: la marca de hueco de silencio de la Fase 4.

**Granularidad — no la confundas:**

| Qué | Granularidad |
|---|---|
| El archivo de video | Por pieza |
| El mapa de tiempos | Por escena |
| El punto de entrada/salida de un visual | Por sub-frase, solo cuando la coreografía lo pide |

Nunca hay un archivo por visual — eso es trabajo de `edit-composer`, no de esta etapa.

---

## Reporte final

No pegues las transcripciones ni el JSON completo. Reporta, por pieza:

```
✅ Tomas de "<tema>" organizadas — <pieza>: <N> escenas, <N> auto-elegidas (revisa si alguna no
   corresponde), <N> uniones con hueco de silencio detectado.
   Raw/shots/<pieza>/camera.mp4 + timecodes.json
```

Si hubo ambigüedades presentadas a Santiago (Fase 2) y no se resolvieron todavía, dilo explícito —
no sigas a la Fase 6 con una escena sin resolver.

---


## Convenciones

- **Nunca elijas entre varios candidatos sin marca cuando hay más de uno** — eso es juicio de
  Santiago, no tuyo.
- **`discarded` y `final` pesan más que cualquier heurística de calidad tuya.**
- **El archivo de salida es continuo por pieza, nunca por escena ni por visual.**
- No hace falta ningún mecanismo de sincronización cámara+screen — OBS ya las compone en vivo. Si
  algún caso no se puede resolver así (ver `WMF/DECISIONS.md`, nota de trazabilidad), repórtalo en vez
  de improvisar una solución nueva.
- Sin escrituras a Notion en esta etapa.

## Riesgos conocidos (ver `WMF/DECISIONS.md` para la apuesta completa y la alternativa)

- Si las marcas de voz no se detectan de forma confiable, o la auto-selección elige algo que
  Santiago no hubiera elegido, repórtalo — no ajustes el umbral por tu cuenta sin decirlo.
- La regla del hueco de silencio (Fase 4) no está probada contra footage real todavía — si algo se
  ve raro (una transición innecesaria donde el hueco era solo una respiración, o un corte duro
  donde hacía falta algo más), repórtalo para revisar la heurística.
