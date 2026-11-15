# CHANGELOG — qué cambió en el sistema y cuándo

Solo cambios del **sistema** (etapas, herramientas, reglas, estructura). El contenido de los proyectos
no va aquí. Lo más nuevo, arriba. El porqué está en [DECISIONS](DECISIONS.md).

## 2026-11-15

- **Etapa nueva ③ `contextualizer`** (conversacional), entre ② y el schema: explica el tema y lo
  investigado (`digest.md`), verifica cada cifra con fuente y deja `context.md`. `schema-builder` lo lee y
  ya no explica; `script-writer` lo toma como universo de hechos. Corre en concept y case; en news, en
  corto; otro formato o sin formato, omitida salvo que la pidas. Ver [DECISIONS](DECISIONS.md),
  [WORKFLOW](WORKFLOW.md) y [FORMATS](FORMATS.md). Riesgo R-10.
- **Renumeración:** schema-builder ④, script-writer ⑤, visual-script ⑥, resource-fetcher ⑦,
  take-organizer ⑧, edit-composer ⑨ (① y ② no cambian). Las conversacionales son ③ ④ ⑤ ⑥.

## 2026-11-10

- **Concept investiga, en ligera y solo con YouTube.** ① corre con el flag nuevo `--sources` del CLI
  (`all` por defecto, o `hn`/`youtube`/`x`/`web`; solo modo `--topic`) y ② corre tras ella. Case y news:
  completa; otro formato o sin formato: omitida salvo que la pidas. Ver [DECISIONS](DECISIONS.md),
  [FORMATS](FORMATS.md) y [RUNBOOK](RUNBOOK.md).
- **WORKFLOW y FORMATS corregidos:** ① pasa de "opcional" a "según el formato" y la arista "se omite en
  conceptos" ya no existe; la fila News dice "completa" (el modo `fresco` es B-3, aún sin construir).

## 2026-11-09 — consolidación

- **Un proyecto = un tema, con `Raw/` y `Final pieces/`.** El orquestador crea el esqueleto;
  `edit-composer` deja cada pieza (proyecto HyperFrames + render) en `Final pieces/<pieza>/`. El
  proyecto existente de Other Content (`zero-residual-news-g1`) se migró a esta estructura: grabaciones
  a `Raw/shots/`, recursos a `Raw/resources/`, guion a `Raw/source/`, exportaciones y archivos de
  trabajo a `Final pieces/theta-part/`; `build.py` se actualizó a las nuevas rutas y desaparecieron las
  carpetas `Productions/` y `Raw Media/`.
- **Brand Kit.** `frame.md` se partió en `Personal Content/Brand Kit/visual.md` y `palettes.md`;
  `style-test*` pasó a `Brand Kit/experiments/`. `edit-composer` lee todos los `.md` del kit de la
  línea. Other Content tiene su propio kit (aún sin `visual.md`).
- **Brand Kits en blanco "por el momento"**; la identidad v1 se eliminó a pedido de Santiago (sin copia).
  `edit-composer` ya no asume estilo: lo pregunta (gate nuevo en [WORKFLOW](WORKFLOW.md)).
- **Todo el sistema vive en `Production/.claude`.** Las skills y agentes de Planning se movieron allí;
  `Planning/` queda como datos y CLI. Se eliminaron `Planning/CLAUDE.md`, `Planning/AGENTS.md`, los
  `STAGE.md` duplicados de las etapas conversacionales y la config MCP de X sin uso. Se agregó un
  `CLAUDE.md` mínimo en la raíz.
- **Sin Codex:** se eliminaron `.agents/`, `.codex/` y `AGENTS.md`.
- **Agente `wmf-documenter`** y regla en `video-orchestrator`: el orquestador lo lanza cuando hay algo
  que documentar.
- **El orquestador ejecuta, no interroga.** Toma por defecto lo que Santiago no especifica; su única
  pregunta es al cierre: un chat de retro opcional ([WORKFLOW](WORKFLOW.md), [DECISIONS](DECISIONS.md)).
- **WMF depurada:** se eliminó el diseño de edición histórico (los contratos de datos pasaron a
  [ARTIFACTS](ARTIFACTS.md)), `DECISIONS` se podó a lo vigente, el ejemplo de referencia pasó a
  `reference/example-project/` y `script-transcreator` a `reference/parked/`.
- **Limpieza de skills:** `schema-builder`, `script-writer` y `visual-script` ya no abren con `git pull`
  (`Production/` no tiene remoto); `video-orchestrator` "toma lo que dice Santiago o el valor por defecto".
- **Todo nace en el orquestador, con contrato por etapa.** Sin modo suelto; rehacer una etapa marca
  `desactualizada` las posteriores. `schema-builder` ya no investiga ([DECISIONS](DECISIONS.md)).
- **Un solo repo git.** `Production/` absorbe `Planning/` (se eliminó `Planning/.git`; el remoto de GitHub
  no se tocó). Se cierran D-2 y R-3; se actualiza B-2.
- **MCP `xapi` (X) a nivel usuario**, con el token en la variable `X_BEARER_TOKEN`: ya disponible desde
  `Production/` (antes solo en el `Planning/.mcp.json` borrado). Ver [RUNBOOK](RUNBOOK.md).
- **Nuevo visual `GFX-n`** (texto, formas, gráficas y líneas de tiempo dibujados con código, sin
  recursos); `GEN-n` queda para compuestos con imágenes, video y sonido. Todo `GFX` con números lleva
  `**Datos:**` (cifra · fuente · fecha) en `visuals.md`, que `edit-composer` dibuja y `edit-reviewer`
  verifica. Tocó `script-writer`, `visual-script`, `edit-composer`, `edit-reviewer` y `visuals-indexer`;
  el encadenado de tres pasos del ejemplo de referencia pasó a ser `GFX-1`. Ver
  [DECISIONS](DECISIONS.md).
- **Se cierra D-1:** los visuales de datos se resuelven con `GFX`; no se crea `DATA-n`.
- **YouTube en la investigación (①).** La transcripción fallaba en silencio (`youtube-transcript-api` 0.6) y
  todo video se descartaba; la librería pasa a `>=1.2,<2.0` y se reescribió el enricher. Cada video trae
  cifras, transcripción con marcas `[MM:SS]`, capítulos y comentarios; el descubrimiento hace dos búsquedas
  (relevancia y más vistos). Ver [DECISIONS](DECISIONS.md) y [RUNBOOK](RUNBOOK.md).
- **`research-digest`** escribe la sección "Cómo lo cuentan otros creadores (YouTube)": por video, gancho,
  estructura y recepción, más patrones; describe y no evalúa.
- Riesgo R-9 (bloqueo de YouTube) y pendiente B-11 (probar la búsqueda de X del CLI) en
  [RISKS-AND-BACKLOG](RISKS-AND-BACKLOG.md).

## 2026-11-07

- `git init` en `Production/` con `.gitignore` (sin commits todavía).
- `C:\Users\dazas\.local\bin` añadido al `PATH` de usuario, para que `media-use` encuentre `heygen`.

## 2026-11-01

- **Orquestación con sesiones anidadas:** skill `video-orchestrator`; cada skill de etapa ganó una
  sección "Modo sesión hija" y un reporte que empieza con `ETAPA <etapa> · <slug> · <estado> ·
  <artefacto>`. Apuesta 🟡.
- Se creó WMF como carpeta de documentación del flujo.

## 2026-10-31

- **`fal` es el generador de IA por defecto** (Higgsfield de respaldo).
- **HeyGen CLI instalado y autenticado** para stock de imagen, ícono, sonido y música. Hallazgo: el
  audio exige `--min-score 0.4`.

## 2026-10-30 — giro del canal a negocio / finanzas / emprendimiento

1. `capture-guide.md` → `pre-capture-guide.md`.
2. Piezas voice-only: `script.en.md` declara `Delivery`; `take-organizer` acepta audio.
3. Claude como crítico en las etapas con decisión de Santiago.
4. Solo inglés; la traducción queda parada.
5. Estilo visual pendiente a propósito: el primer video toma su look solo de edición.
