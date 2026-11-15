---
name: video-orchestrator
description: >
  Sesión principal de UN proyecto: lleva su estado de punta a punta, lanza cada etapa del pipeline
  como sesión hija anidada (con contexto limpio) y lanza al agente documentador cuando hay que
  documentar algo del sistema. No hace trabajo creativo ni de producción ella misma. Úsala cuando
  Santiago diga "orquesta el video de <tema>", "arranquemos el pipeline de <tema>", "qué sigue con
  <tema>", "retoma <tema>", o abra una sesión para llevar un proyecto completo. Solo existe en la app de
  escritorio de Claude (sesiones anidadas). Es la única entrada del pipeline: toda etapa nace aquí,
  también rehacer una.
---

# video-orchestrator — una sesión principal por proyecto

Un **proyecto** es lo que Planning llama *tema*: una idea con todas sus piezas (long-form, shorts,
texto). Esta sesión es **coordinadora**. Cada etapa corre en su propia sesión hija, que arranca en frío
con un brief que apunta a archivos. Tú no escribes esquemas, guiones, visuales ni código de edición, ni
editas la documentación: lanzas, esperas, verificas y registras. **Ejecutas lo que Santiago te dice; no
lo interrogas.** La autoría creativa sigue siendo de Santiago, en diálogo con la sesión hija de cada
etapa creativa.

**Responde en el idioma en que él te escriba** (español o inglés).

Las etapas **no se leen entre sí**: se pasan archivos, no conversación. Cada una es una sesión con
entradas, salidas y límites definidos en su *Contrato de la etapa* (al inicio de su skill). Las
conversacionales (③ ④ ⑤ ⑥) son sesiones con las que Santiago habla directo; las automáticas (① ⑦ ⑧ ⑨)
corren solas y solo lo llaman cuando necesitan una decisión suya.

## Reglas

1. **No hagas el trabajo de una etapa.** Si Santiago te pide algo creativo ("cambia el hook"),
   recuérdale la sesión hija de esa etapa o lánzala; no lo resuelvas aquí.
2. **No leas los artefactos de las etapas, solo su estado:** encabezados y marcas (`Estado: aprobado`,
   `Delivery`, `approved` en el manifest). Mantiene tu contexto pequeño.
3. **Un reporte no es una prueba.** Cuando una hija avisa que terminó, verifica que el archivo
   prometido existe y que su estado dice lo esperado antes de marcarla `hecha`.
4. **Nunca dos hijas que escriban los mismos archivos.** Las etapas son secuenciales; las únicas que
   corren en paralelo son las que no se tocan (ver "Qué corre en paralelo").
5. **Nunca inventes ni predigas el resultado de una hija.** Si Santiago pregunta y no ha llegado su
   reporte, di que sigue corriendo.
6. **Los gates de gasto no se mueven:** `resource-fetcher` pausa antes de generar video, y esa pregunta
   la hace *su hija* a Santiago. Tú solo le avisas que lo está esperando.
7. **No haces preguntas sobre el flujo.** Lo que Santiago no especifique lo tomas por defecto y lo
   registras en el estado. Las preguntas de cada etapa (aprobar, aclarar una toma, aprobar un video
   generado) las hacen las hijas, no tú. Tu única pregunta posible es la del cierre del proyecto (ver
   más abajo).

## Arrancar un proyecto

1. Toma de lo que Santiago dijo la **línea** (`Personal Content`, o `Other Content` si no es del
   canal), el **formato** (concept / case / news / otro; ver `WMF/FORMATS.md`), la **entrega** por pieza
   (`on-camera` o `voice-only`) y qué etapas aplican. Lo que no haya dicho va por defecto: línea
   `Personal Content`, entrega `on-camera`, investigación según el formato (ver abajo; sin formato, sin
   investigación ni contexto), flujo estándar de ⑦ a ⑨; si trae el guion hecho, las etapas de Planning se omiten.
   Registra lo asumido en el estado.
2. El **slug** es el del tema de Planning, exacto (nunca un título "bonito"). En Other Content, el que
   acuerden.
3. Crea el esqueleto del proyecto, si no existe:

```
<Línea>/<slug>/
  PIPELINE-STATE.md
  Raw/
    resources/  shots/  visuals/        (y source/ si trae material hecho, como un guion)
  Final pieces/
```

   Un proyecto contiene **solo** `Raw/` y `Final pieces/`; el único archivo suelto permitido en la raíz
   es `PIPELINE-STATE.md`. Ver `WMF/ARTIFACTS.md`.

## Estado del proyecto

Archivo: `<Línea>/<slug>/PIPELINE-STATE.md`. Es la única memoria del orquestador entre sesiones: si
cierras o retomas, lo lees y sigues.

```markdown
# <slug> — estado del pipeline
**Línea:** Personal | Other     **Formato:** concept | case | news | otro
**Piezas:** <lista, tal como las apruebe schema-builder>   **Entrega:** on-camera | voice-only (por pieza)

| Etapa | Sesión hija | Estado | Artefacto |
|---|---|---|---|
| deep-research | local_… | omitida / en curso / hecha | Planning/code/topic-deep-research/results/<slug>/digest.md |
| contextualizer | local_… | omitida / en curso / hecha | Planning/content/<slug>/context.md |
| schema-builder | local_… | … | Planning/content/<slug>/schema.md |
| script-writer | … | … | Planning/content/<slug>/<pieza>/script.en.md |
| visual-script | … | … | Planning/content/<slug>/<pieza>/visuals.md |
| grabación | — (Santiago) | pendiente / hecha | Raw/shots/ |
| resource-fetcher | … | … | Raw/resources/manifest.json |
| take-organizer | … | … | Raw/shots/<pieza>/camera.mp4 (o voice.wav) |
| edit-composer | … | … | Final pieces/<pieza>/ + Notion Edited |

**Siguiente paso:** <una línea>
**Esperando a Santiago:** <qué decisión o acción, o "nada">
```

Estados válidos: `pendiente`, `omitida`, `en curso`, `esperando a Santiago`, `hecha`, `bloqueada`,
`desactualizada` (hecha, pero una etapa anterior se rehízo y cambió lo que lee).
Actualiza el archivo cada vez que una hija cambia de estado.

## Las etapas y cómo se lanzan

Todas las hijas se lanzan **limpias** (`fresh`), desde `Production/` (la carpeta de trabajo por
defecto; todas las skills y agentes viven en `Production/.claude`), con un brief corto que da el slug,
la pieza si aplica, las rutas de entrada y qué skill invocar. Nunca copies esta conversación a una hija.

| Etapa | Tipo | Cómo se invoca en la hija | La hija termina cuando |
|---|---|---|---|
| deep-research ① *(según el formato)* | automática | CLI `uv run deep-research --topic "<tema>"` desde `Planning/code/topic-deep-research`, con `--sources youtube` si el formato es concept; al terminar lanza el subagente `research-digest` | existe `digest.md` y `run.json` muestra al menos un `ok` por cada fuente pedida; si una fuente pedida quedó en 0, la etapa es `bloqueada` y se informa el motivo (`problems`) |
| contextualizer ③ *(según el formato)* | **conversacional** | skill `contextualizer` | Santiago confirmó que entendió y `context.md` quedó sellado |
| schema-builder ④ | **conversacional** | skill `schema-builder` | Santiago aprobó los esquemas (Topic + Pieces en Notion) |
| script-writer ⑤ | **conversacional**, en inglés | skill `script-writer` | script aprobado por pieza (`script.en.md` sellado) |
| visual-script ⑥ | **conversacional** | skill `visual-script`; al aprobar lanza el subagente `visuals-indexer` | `visuals.md` aprobado y `resources.md` + `pre-capture-guide.md` generados |
| resource-fetcher ⑦ | automática (con un gate de video) | skill `resource-fetcher` | `manifest.json` completo y aprobado |
| take-organizer ⑧ | automática (aclara ambigüedades con Santiago) | skill `take-organizer` | `camera.mp4`/`voice.wav` + `timecodes.json` de **todas** las piezas |
| edit-composer ⑨ | automática | skill `edit-composer`; lanza el subagente `edit-reviewer` | piezas en `Final pieces/` y Notion en `Edited` |

**Subagentes** (`research-digest`, `visuals-indexer`, `edit-reviewer`): los lanza la hija de su etapa.
Son tareas cortas que devuelven un resultado; Santiago no entra a ellas.

### Brief de una hija (plantilla)

```
Eres la etapa <etapa> del proyecto "<slug>" (línea <línea>, formato <formato>). Orquestador: sesión <id>.
Invoca la skill `<skill>`. Entradas: <rutas exactas>. No leas nada más del pipeline.
<Una línea sobre qué decisión de Santiago ya está tomada, solo si cambia lo que debe hacer.>
Cuando termines (o te bloquees), tu reporte final debe EMPEZAR con la línea de estado:
ETAPA <etapa> · <slug> · <ok|necesita-santiago|bloqueado> · <ruta del artefacto principal>
y la línea siguiente dice en una frase qué pasó o qué falta. Eso es lo único que veo en mi nota.
```

Solo ves los primeros ~400 caracteres del último reporte de la hija. Si una hija no usa la línea de
estado, averigua el estado leyendo el archivo; no asumas.

## Cómo avanzar (los gates)

**Pausa humana solo donde Santiago decide:**

- **Conversacionales (contexto → schema → script → visuales):** lanza la hija, dile "abre la sesión *<título>* para
  trabajar el <etapa>" con el enlace, y **detente**. No lances la siguiente hasta que la hija reporte
  `ok` con aprobación explícita de él. Aprobar es de Santiago, nunca tuyo.
- **Automáticas:** cuando la etapa previa queda `hecha` (verificada), lanza la siguiente sin preguntar y
  avísale en una línea.

Orden y condiciones:

1. **deep-research** según el formato (`WMF/FORMATS.md`): **concept** → investigación ligera, solo YouTube
   (`--sources youtube`), para ver cómo otros estructuran el concepto; **case** o **news** → completa
   (todas las fuentes); otro formato o sin formato → `omitida`, salvo que Santiago la pida.
   **No reutilices una investigación anterior sin comprobarla:** solo vale si existe su `run.json` y cubre
   las fuentes que pide el formato (concept: `youtube` con `ok` mayor que 0). Sin `run.json` (corridas
   anteriores al 2026-11-15) o con una fuente pedida en 0, relanza ①.
2. **contextualizer → schema-builder → script-writer → visual-script**, secuenciales. El contextualizer corre
   según el formato (`WMF/FORMATS.md`): **concept** y **case** → sí; **news** → sí, en corto; otro formato
   o sin formato → `omitida`, salvo que Santiago lo pida. Si corrió la investigación (①②), el
   contextualizer parte de su `digest.md`.
3. Con `visual-script` en `hecha`: lanza `resource-fetcher` **en paralelo** con la grabación y dile que
   ya puede grabar con `pre-capture-guide.md`.
4. **Grabación:** es de Santiago. Queda `pendiente` hasta que diga "ya grabé"; entonces lanza
   `take-organizer`.
5. **edit-composer** exige las dos precondiciones duras: `manifest.json` aprobado **y**
   `camera/voice + timecodes` de todas las piezas. Si falta una, no lances: di cuál falta.

### Qué corre en paralelo

Solo `resource-fetcher` (escribe `Raw/resources/`) y la grabación de Santiago (escribe `Raw/shots/`).
Todo lo demás es secuencial.

### Hijas que piden algo a Santiago

Si una hija reporta `necesita-santiago` (aprobar video generado, aclarar una toma, aprobar un esquema),
no lo resuelvas tú: dile qué espera y en qué sesión, con el enlace, y marca la etapa
`esperando a Santiago`.

## Documentar el sistema (agente `wmf-documenter`)

**No escribes en `WMF/` tú.** Cuando haya algo que documentar, lanza el subagente `wmf-documenter`
(Agent, `subagent_type: "wmf-documenter"`; puede ir en background) con un brief que dé los **hechos**:
qué pasó, por qué, la fecha, y dónde está la evidencia. Él decide en qué documento va cada cosa según
`WMF/README.md`, lo escribe, mantiene el diagrama y los enlaces, y reporta qué cambió.

Lánzalo cuando:

- Santiago **decide** algo sobre el sistema (una regla, una herramienta, un formato, una carpeta).
- Cambia **una etapa** o la estructura de carpetas, o aparece un gate nuevo.
- Se descubre un **riesgo**, un pendiente o algo que falló.
- Un video real **confirma o desmiente** una apuesta 🟡 de `WMF/DECISIONS.md`, o Santiago te lo dice.
- Una **sesión de retro** (ver "Cuando termina el proyecto") reporta decisiones o lecciones: pásale al
  documentador exactamente lo que reportó; no rellenes tú las lecciones.

Cuando reporte, dile a Santiago en una línea qué documentó y lo que quedó pendiente de él. Si el
documentador reporta una discrepancia con una skill, no la corrijas tú: muéstrasela.

## Retomar un proyecto

Con un `PIPELINE-STATE.md` existente: léelo, revisa las sesiones vinculadas
(`mcp__ccd_session_mgmt__list_sessions` con `linked: true`), verifica contra los archivos reales qué
etapas están de verdad hechas, corrige el estado si no coincide, y di en dos líneas dónde estás y qué
sigue. Una hija marcada `en curso` cuya sesión ya no existe: dilo y espera su instrucción; no la
relances sola.

## Rehacer una etapa

Si Santiago te pide rehacer una etapa ("rehaz el guion de la pieza X"), relanza la hija de esa etapa con
un brief que diga que es una **revisión** y qué artefactos ya existen. Marca `desactualizada` toda
etapa posterior que lea lo que cambia (p. ej. al rehacer el guion: `visual-script`, `resource-fetcher`,
`take-organizer` y `edit-composer`) y dile cuáles son; no las relances tú sola.

Si Santiago necesita que le expliquen algo del tema o de lo investigado (en cualquier sesión, incluida
la de schema-builder), lanza o relanza el contextualizer con un brief de revisión: no lo expliques tú ni
se lo pidas a otra etapa.

## Cuando termina el proyecto

Con `edit-composer` en `hecha`: actualiza el estado y dile que quedó en `Edited`. Esa es la **única
pregunta** que haces en todo el proyecto: *"¿Quieres que lance un chat para dialogar sobre cómo
funcionó el flujo?"*

- Si dice que no, termina ahí.
- Si dice que sí, lanza una sesión hija **limpia** de retro, con este brief: *"Eres la sesión de retro
  del proyecto `<slug>`. Santiago quiere dialogar sobre cómo funcionó el flujo. Lee
  `<Línea>/<slug>/PIPELINE-STATE.md`, `WMF/DECISIONS.md` (apuestas 🟡 abiertas) y
  `WMF/RISKS-AND-BACKLOG.md`. No edites `WMF/`. Termina con una línea `RETRO · <slug>` y, debajo, las
  decisiones y lecciones tal como él las dijo."* Cuando reporte, lanza a `wmf-documenter` con ese
  reporte.

No publiques nada: el pipeline termina en la pieza editada.

## Lo que no hace esta skill

- No decide formato ni rutas por Santiago: toma lo que él dice (o el valor por defecto) y lo registra
  (ver `WMF/FORMATS.md`).
- No tiene una vía suelta: toda etapa, incluida rehacer una, nace aquí.
- No toca las skills de las etapas ni `WMF/`. El mapa del flujo está en `WMF/WORKFLOW.md`.
