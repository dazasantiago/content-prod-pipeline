# RUNBOOK — cómo operar el pipeline

Guía práctica. Para el porqué de cada regla: [DECISIONS](DECISIONS.md). Para el mapa: [WORKFLOW](WORKFLOW.md).

## Arrancar un proyecto

1. Abre una sesión en `Production/` y di: *"orquesta el video de `<tema>`"*. Se activa
   `video-orchestrator`.
2. Dile la **línea** (Personal Content por defecto, u Other Content), el **formato** (concept / case /
   news / otro) y si el video lleva cara o es voice-only. El orquestador no te interroga: lo que no
   digas (línea, entrega, investigación) lo toma por defecto y lo registra, junto con lo que sí dijiste,
   en `PIPELINE-STATE.md`. Con eso decide si corren investigación y contexto y crea la carpeta del proyecto
   (`Raw/` y `Final pieces/`).
3. Trabaja en las sesiones hijas que te abra para ③ ④ ⑤ ⑥ (③ según el formato). Cada una te dice cuándo está lista; nada
   avanza sin tu aprobación explícita.
4. Graba con `pre-capture-guide.md` en la mano. Cuando termines, dile al orquestador **"ya grabé"**.
5. El resto (recursos, organizar tomas, edición) corre solo. Las preguntas las hacen las sesiones hijas,
   no el orquestador, y son las que ya hacían las skills: aprobar video generado, aclarar tomas
   ambiguas y, con el Brand Kit en blanco, el estilo del proyecto al editar; además, escalar un punto
   crítico tras 3 intentos de `edit-reviewer`.

**No hay modo suelto.** Toda etapa nace en el orquestador: también rehacerla (*"rehaz el guion de
`<pieza>`"*), pedir investigación (*"investiga `<tema>`"*; es solo la etapa ①, `schema-builder` no la
hace) y pedir que te expliquen el tema o lo investigado (etapa ③; `schema-builder` tampoco lo hace, y
puedes pedirlo en cualquier sesión). Al rehacer, el orquestador relanza la hija como revisión y marca `desactualizada` las etapas
posteriores que leen lo que cambió; te dice cuáles y no las relanza solo.

## Retomar un proyecto

Sesión nueva en `Production/` → *"retoma `<tema>`"*. El orquestador lee `PIPELINE-STATE.md`, revisa
qué sesiones hijas siguen vivas, verifica contra los archivos y te dice dónde estás. Una hija marcada
"en curso" cuya sesión ya no existe: te avisa y espera tu instrucción, no la relanza sola.

## Documentar un cambio del sistema

Dile al orquestador qué cambió o qué decidiste; él lanza a `wmf-documenter`, que lo escribe en el
documento que corresponde de `WMF/` y te reporta qué tocó. No edites `WMF/` a mano salvo para algo
trivial: el agente mantiene coherentes el diagrama y los enlaces.

## Herramientas y cómo comprobarlas

| Herramienta | Para qué | Cómo comprobar | Si falla |
|---|---|---|---|
| HeyGen CLI (`C:\Users\dazas\.local\bin\heygen.exe`) | stock de imagen, ícono y audio | `heygen asset search --query test --type image --limit 1` | La carpeta está en el `PATH` de usuario (abre una terminal nueva). Si Defender lo borra (falso positivo `Trojan:Win32/Bearfoos.A!ml`), **no lo restaura un asistente**: lo restauras tú |
| Búsqueda de audio | SFX y música | siempre con `--min-score 0.4` | Sin ese umbral devuelve vacío en búsquedas que sí tienen resultados |
| `fal` (MCP, ámbito usuario) | generación por IA por defecto | `claude mcp list` debe decir `Connected` | Si pide autenticación: `/mcp` en una sesión interactiva y entra por navegador. Nunca pegues claves en el chat |
| `xapi` (MCP de X, ámbito usuario, `https://api.x.com/mcp`) | consultar X desde cualquier sesión; token app-only: solo lectura, sin contexto de usuario (según la documentación de X) | `claude mcp list` debe decir `Connected`; sus herramientas aparecen en las sesiones que arranquen después de agregarlo. Autenticación y saldo: la herramienta `get_usage_credits` (solo lectura) devuelve el saldo prepago; verificada así el 2026-11-09. La búsqueda de X se factura por publicación devuelta contra ese saldo: consúltalo antes de una corrida grande | Revisa que `X_BEARER_TOKEN` exista como variable de entorno de usuario (el token no se guarda en la config del MCP; es el de la X Developer Portal, y el CLI de investigación usa la misma variable). Si falta el servidor: `claude mcp add --transport http --scope user xapi https://api.x.com/mcp --header 'Authorization: Bearer ${X_BEARER_TOKEN}'`. Nunca pegues el token en el chat |
| Higgsfield (conector claude.ai) | respaldo de generación | llamar `balance` antes de generar en volumen | Si faltan créditos, avisa antes de dejar un proyecto a medias |
| Notion (Content Hub) | Topic y Pieces | las crea `schema-builder`, las cierra `edit-composer` | reautoriza el conector desde `/mcp` |
| HyperFrames | edición y render | skills `hyperframes*` en `.claude/skills` | `hyperframes doctor` |
| CLI de investigación | deep research. `--sources youtube` = investigación ligera de concept: consulta solo YouTube, sin gastar créditos de X ni búsquedas de Tavily (`--sources`: `all` por defecto, o una lista de `hn`, `youtube`, `x`, `web`; solo con `--topic`) | en `Planning/code/topic-deep-research`: `uv run python -m pytest -q` (no `uv run pytest`: el trampolín falla en Windows) | — |
| API de YouTube y transcripciones (CLI de investigación; la clave `YOUTUBE_API_KEY` vive en `Planning/code/topic-deep-research/.env`) | etapa ①: cifras, capítulos, comentarios y transcripción de los videos | Transcripción (no gasta cuota), en `Planning/code/topic-deep-research`: `uv run python -c "from youtube_transcript_api import YouTubeTranscriptApi as Y; print(len(Y().fetch('jNQXAC9IVRw', languages=['en','es']).to_raw_data()))"` debe imprimir un número. Cuota: cada corrida del CLI gasta ~200 unidades de las 10 000 diarias. Tras una corrida, las señales de YouTube salen `ok` con marcas `[MM:SS]` en `full_text` | Sin señales de YouTube: falta la clave o la API falló (clave inválida, cuota agotada); la corrida sigue sin esa fuente y solo lo deja en el log. Transcripciones en `error` que mencionan `YOUTUBE_COOKIES_FILE`: YouTube bloquea la IP; exporta las cookies de un navegador con sesión iniciada y apunta `YOUTUBE_COOKIES_FILE` a ese archivo (detalle en [STAGE.md](../Planning/code/topic-deep-research/STAGE.md)). Todas fallan sin error claro: la librería debe ser 1.2+ (la 0.6 falla en silencio). Un video `skipped` no tiene transcripción en inglés ni español. Nunca pegues la clave en el chat |

Las claves de API nunca van en el chat ni en archivos del proyecto.

## Gastos: qué pide permiso

| Recurso | Regla |
|---|---|
| Imagen y SFX generados | se aprueban en bloque |
| **Video generado** | siempre pausa y te pregunta; es la única categoría cara |
| Stock (HeyGen) | sin costo por recurso; no pide permiso |
| Música generada | se trata como audio generado: aviso antes |

## Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El orquestador no ve el reporte completo de una hija | Solo recibe ~400 caracteres | Verifica el archivo. Si la hija no empezó con la línea `ETAPA …`, abre su estado leyendo el artefacto |
| `edit-composer` se niega a arrancar | Falta `manifest.json` aprobado o `camera/voice + timecodes` de alguna pieza | Corre la etapa que falta; no se construye parcial |
| `edit-composer` pregunta por el estilo | El Brand Kit de la línea no tiene `visual.md` (hoy pasa en las dos líneas; no es un fallo) | Dile tipografía, fondo, colores y forma de los contenedores; queda en `Raw/visuals/style.md` y una re-edición no vuelve a preguntar. Si se va a repetir, acepta que lo suba al Brand Kit como `visual.md` |
| `take-organizer` marca archivo de tipo distinto al `Delivery` | Grabaste audio de una pieza `on-camera` (o al revés) | Corrige el `Delivery` en `script.en.md` o regraba |
| La transcripción no reconoce "discarded" | Suena a "Discord" o "Discard" | Aceptar esas variantes; es evidencia de la apuesta 🟡 de las marcas de voz |
| Stock genérico o fuera de tono | La barra de "match razonable" es baja | Decisión tuya: subir la barra o invertir el orden solo para `IMG` |
| Miniaturas vacías al abrir una página local en el panel | El panel muestra `file://` como captura estática | Servir la carpeta con `python -m http.server` |

## Checklist antes de grabar el primer video

- [ ] Formato y modo de entrega decididos.
- [ ] `schema.md`, `script.en.md` y `visuals.md` aprobados.
- [ ] `resources.md` y `pre-capture-guide.md` generados.
- [ ] `fal` conectado y HeyGen respondiendo (tabla de arriba).
- [ ] Estilo del primer video pensado (tipografía, fondo, colores, contenedores): el Brand Kit está en
      blanco y `edit-composer` te lo preguntará al editar.

## Después de cada proyecto

Con la pieza editada, el orquestador te hace **una sola pregunta**: *"¿Quieres que lance un chat para
dialogar sobre cómo funcionó el flujo?"*. Si dices no, el proyecto termina ahí. Si dices sí, abre una
sesión de retro limpia donde hablas del flujo; cuando reporta tus decisiones y lecciones tal como las
dijiste, el orquestador lanza a `wmf-documenter` con ese reporte, que pasa a 🟢 las apuestas que
funcionaron, aplica la alternativa a las que fallaron y actualiza el [backlog](RISKS-AND-BACKLOG.md).
