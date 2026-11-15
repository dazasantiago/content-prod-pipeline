# DECISIONS — por qué es así, y qué apuestas siguen abiertas

Argumenta el **por qué** de cada decisión. Para las que todavía no se probaron contra un video real
deja el riesgo concreto y la alternativa ya pensada, para que si algo falla no haya que re-derivar el
razonamiento desde cero. El **qué** vive en el [WORKFLOW](WORKFLOW.md) y en las skills.

- 🟢 **Cerrada** — convención o consecuencia lógica. No hay nada que probar.
- 🟡 **Apuesta** — elegida sobre supuestos razonables, sin evidencia de un video real todavía. Lleva
  riesgo, qué mirar y alternativa.

Cuando una apuesta se prueba y funciona, pasa a 🟢 con fecha. Si falla, se aplica su alternativa; no se
rediseña en caliente.

---

## Transversales

### 🟢 Un proyecto = un tema, con `Raw/` y `Final pieces/` (2026-11-09)
Cada tema es un proyecto y vive en una carpeta con su **slug exacto**, igual en Planning y en
Production: son dos árboles que deben referirse al mismo tema sin que un agente tenga que inferir la
correspondencia entre dos strings. Dentro, solo `Raw/` (lo que entra) y `Final pieces/` (lo que sale,
por pieza). El orquestador crea el esqueleto al arrancar. Las dos líneas de contenido, `Personal
Content` y `Other Content`, comparten esta forma; Other no tiene Planning y su guion llega hecho.

### 🟢 El estilo vive en un Brand Kit por línea de contenido, no en el workflow (2026-11-09)
Las skills son genéricas y leen todos los `.md` de `<Línea>/Brand Kit/`. Un tema nuevo (audio, voz,
movimiento) es un `.md` nuevo, sin tocar skills. Se versiona en git aunque el resto del contenido no.
Nombre: *Brand Kit*, el término corriente para "lo que hace que se vea y suene como tu canal". Hoy los
dos kits están en blanco (decisión siguiente); sus archivos se crean cuando un estilo se repita o un
video muestre qué preferencias hacen falta.

### 🟢 Brand Kits en blanco por ahora; sin estilo por defecto (2026-11-09)
Santiago decidió blanquear `Personal Content/Brand Kit/` y `Other Content/Brand Kit/` "por el momento":
ambos quedan solo con su README (el de Personal conserva `experiments/`: pruebas de estilo antiguas que
no son entrada de ninguna etapa; sus scripts generadores aún contienen los colores de las paletas de la
identidad v1). La identidad v1 se **eliminó a pedido de Santiago**: no se archivó y no hay copia.
**Consecuencia:** `edit-composer` no asume ningún estilo. Sin `visual.md` en el kit se detiene y le
pregunta a Santiago el estilo del proyecto, lo registra en `Raw/visuals/style.md` (una re-edición no
vuelve a preguntar) y, si el estilo se va a repetir, le ofrece subirlo al kit como `visual.md` (solo con
su sí). Detalle en su [SKILL](../.claude/skills/edit-composer/SKILL.md), Fase 1. Cuando el kit tenga
`visual.md`, ese es la fuente.

### 🟢 Todo el sistema vive en `Production/.claude`; `Planning/` es solo datos y CLI (2026-11-09)
Santiago nunca trabaja desde `Planning/`, así que no hay `Planning/CLAUDE.md` ni skills allí. Las
skills de Planning se movieron a `Production/.claude/skills`, y todas las sesiones, incluidas las
hijas del orquestador, corren desde `Production/`. `Planning/` conserva el CLI de investigación y los
artefactos (`content/<slug>/`), y se versiona en el mismo repo (decisión siguiente).

### 🟢 Un solo repo git: `Production/` (2026-11-09)
Se eliminó `Planning/.git` (78 commits, sincronizado con su remoto de GitHub, `youtube-automation`, que
sigue existiendo y no se tocó: ahí queda la historia del antiguo scraper) y `Planning/.gitignore`. Un
solo repo es más simple de respaldar. Se versionan el CLI (`Planning/code/topic-deep-research`: código,
tests, `STAGE.md`, `uv.lock`), `Planning/content/` y el `digest.md` de cada tema; se ignoran el JSON crudo
de la investigación (`results/*/*.json`, se regenera), `.env`, `.venv` y cachés. Detalle en
[ARTIFACTS](ARTIFACTS.md).

### 🟢 Solo Claude Code; sin Codex (2026-11-09)
Se eliminaron las copias `.agents/`, `.codex/` y `AGENTS.md`. Mantenerlas obligaba a editar cada cambio
N veces y ya habían derivado entre sí. Si algún día se usa Codex, se genera desde `.claude/`.

### 🟢 La documentación la mantiene un agente (2026-11-09)
`wmf-documenter` escribe en `WMF/` cuando el orquestador se lo pide, enrutando cada hecho al documento
que le toca (regla "un hecho, un lugar") y manteniendo coherentes el diagrama y los enlaces. Evita que
la documentación dependa de que alguien se acuerde de actualizarla, y que cada sesión la edite con su
propio criterio. El orquestador no edita `WMF/`.

### 🟢 `GEN` se divide en `GEN` y `GFX`: lo que dibuja el código no se consigue (2026-11-09)
Santiago: "Divide GEN en 2. GEN con resources y animación… cuando no se necesitan resources sino solo
generar con html o animar". `GEN` queda para el compuesto que HyperFrames arma con varias piezas
(imágenes, video, sonido) que hay que conseguir; `GFX`, para texto, formas, diagramas, gráficas, líneas
de tiempo o contadores que HyperFrames dibuja solo con código. La prueba es *¿qué sostiene el punto?*:
imágenes o clips → `GEN`; lo dibuja el código → `GFX`. El nombre `GFX` lo eligió Santiago (Claude había
propuesto otro).

**Por qué:** una gráfica se hace de números, no de recursos. Bajo `GEN` se corría el riesgo de que se
consiguiera o se generara como imagen, y una gráfica generada por IA inventa cifras. Como `GFX` no entra
al flujo de recursos, sus números quedan explícitos con fuente y fecha (campo `Datos`, en
[ARTIFACTS](ARTIFACTS.md)) y el revisor puede comprobarlos: `edit-composer` dibuja exactamente lo
declarado y `edit-reviewer` trata un número no declarado o distinto como punto crítico obligatorio.
**Consecuencia:** un `GFX` casi no genera trabajo en `resources.md` ni en `resource-fetcher`
(`visuals-indexer` lo excluye de las listas). Con esto, los visuales de datos no necesitan un tag propio:
no se crea `DATA-n`.
**Costo:** había que tocar tres etapas (⑤ ⑥ ⑨) y los `visuals.md` ya escritos; por eso convino decidirlo
antes del primer video.

### 🟢 Canal solo en inglés; traducción parada (2026-10-30)
El público es angloparlante. Una pista de audio en español sobre texto en pantalla en inglés era una
tensión sin salida barata; la única resolución limpia es un canal en español aparte, que por ahora
cuesta más de lo que rinde para una sola persona. `script-transcreator` queda archivado en
[reference/parked](reference/parked/script-transcreator.md); ninguna etapa lo lanza.

### 🟢 Claude critica siempre y propone solo si se le pide (2026-10-30)
La autoría creativa es de Santiago, pero un coach que solo pregunta deja pasar problemas que un
espectador sí vería. Se separa **criticar** (siempre: qué falla, dónde, qué le cuesta al espectador) de
**proponer** (solo a petición: opciones de líneas, tomas, generaciones, estructuras). Excepción: si ve
una estructura mejor que la del schema, lo dice en una línea y pregunta si la quiere. Lentes por etapa:
estructura (`schema-builder`), retención y claridad (`script-writer`), creatividad (`visual-script`),
entrega (`take-organizer`, solo al elegir entre tomas sin marca).

### 🟢 Los temas los elige Santiago (2026-07-12)
Se eliminó el descubrimiento y la clasificación automática de temas: el ruido superaba a la señal (casi
todo era clickbait ya visible sin scraping), exigía triage manual constante y empujaba el canal a ser
un reportero de tendencias en vez de algo propio. Santiago elige el tema y decide si necesita
investigación.

### 🟢 YouTube es la fuente de la investigación para ver cómo otros cuentan el tema (2026-11-09)
Santiago: la API de YouTube es clave para la investigación; sirve para saber qué estructuras funcionan,
qué se ha dicho, qué extraer de otros creadores y qué información hay en la etapa de research. Por eso
cada video llega a ① con sus cifras (descriptivas, sin scoring), transcripción con marcas de tiempo,
capítulos y comentarios, y `research-digest` los condensa en una sección propia: por video, gancho,
estructura y recepción, más los patrones entre videos. Describe y no evalúa; qué hacer con eso es de
Santiago. Qué trae cada video: [STAGE.md](../Planning/code/topic-deep-research/STAGE.md).
**Hallazgo:** la transcripción fallaba en silencio (la librería 0.6 recibía respuestas vacías) y todo
video se descartaba: la investigación anterior del IPO tenía 0 señales de YouTube. Se arregló con la
librería 1.2+. Prueba real con "how an IPO works": 8 videos con cifras, 5 con transcripción, y un digest
útil (ganchos, estructuras, patrones y huecos).
**Límites conocidos:** las transcripciones vienen en bloques de 15 s, así que la estructura se infiere con
ese margen; hay pocos comentarios por video (algunos son el anuncio fijado o spam); y raspar
transcripciones depende de que YouTube no bloquee ([R-9](RISKS-AND-BACKLOG.md)).

### 🟢 Concept también investiga, en ligera y solo con YouTube (2026-11-10)
Santiago: quiere ver cómo otros creadores estructuran el concepto. Por eso ① corre para concept con
`--sources youtube` (el flag nuevo del CLI: solo YouTube, sin créditos de X ni búsquedas de Tavily) y ②
corre tras ella, con un digest corto. Qué corre en cada formato: [FORMATS](FORMATS.md).
**Evidencia:** `FORMATS` decía que concept casi no necesitaba investigación porque el deep research del
IPO devolvió casi solo glosarios, pero esa corrida no tenía datos de YouTube (la transcripción fallaba en
silencio; entrada anterior), así que no probaba nada contra esta vía. Prueba real con "what is a bond":
5 señales, todas de YouTube, 0 fuentes descubiertas.

### 🟢 Entender el tema es una etapa propia, `contextualizer`, no del schema (2026-11-15)
Santiago: mientras hacía el video del IPO sentía que le daba a `schema-builder` funciones que no le
pertenecen, al pedirle que le explicara todo lo que es un IPO; y lo mismo pasará después de una
investigación, cuando tenga que pedirle que le explique lo encontrado. Por eso nace ③ `contextualizer`,
entre ② y ④, **conversacional**: Claude (a) le explica el tema (qué es, cómo funciona, actores,
vocabulario) y (b) le explica lo que encontró la investigación (`digest.md`) en lugar de resumirlo otra
vez, y resuelve sus preguntas hasta que Santiago dice que ya entendió y `context.md` queda sellado. Qué
corre en cada formato: [FORMATS](FORMATS.md). Qué produce: [ARTIFACTS](ARTIFACTS.md).

**Por qué el schema no es el lugar:** `schema-builder` decide qué piezas salen y con qué ángulo; entender
el tema es un paso previo, no parte de esa decisión. Son roles distintos: ③ explica y critica la
comprensión (corrige sin que lo pidas lo impreciso o falso; mecanismos sí, consejos financieros
personalizados no) y **no propone** ángulos, ganchos, estructura ni piezas; `schema-builder` critica la
estructura. Ahora `schema-builder` lee `context.md` (y el digest) y no explica: si Santiago se lo pide, lo
remite al orquestador para lanzar ③. `script-writer` toma `context.md` como universo de hechos.
**Regla de cifras:** toda cifra, fecha, nombre propio, norma o plazo se verifica con fuente primaria (o dos
independientes) y se anota `dato · fuente · fecha de consulta`; lo que no se pueda verificar queda
`[UNVERIFIED]`, visible; si las fuentes se contradicen, se presentan las dos.
**Consecuencia:** el orquestador la lanza según el formato; si Santiago necesita que le expliquen algo en
cualquier sesión, la lanza o relanza.
**Riesgo abierto:** [R-10](RISKS-AND-BACKLOG.md).

### 🟢 Publicar queda fuera de alcance
El pipeline termina en "pieza editada, Notion en `Edited`"; subir a las plataformas es manual. Decisión
explícita, anotada para no reabrirla por accidente.

### 🟢 `fal` genera por defecto; Higgsfield es el respaldo (2026-10-31)
Una sola vía de generación (imagen, video, audio) con búsqueda de modelos de solo lectura, y se puede
elegir el modelo más barato que cumpla. Es un servidor MCP de ámbito usuario con inicio de sesión por
navegador; nunca claves de API en el chat. Magnific no se usa (exige cuenta premium). Los gates de
gasto no cambian: video generado siempre pregunta.

### 🟡 Orquestación con sesiones anidadas: una principal por proyecto, una hija por etapa (2026-11-01)
Santiago no quiere abrir ni nombrar sesiones a mano. `video-orchestrator` lleva el estado en
`<Línea>/<slug>/PIPELINE-STATE.md` y lanza cada etapa como sesión hija con contexto limpio (un brief
que apunta a archivos). Las creativas son hijas donde él entra a hablar; las automáticas se lanzan
solas al verificarse la anterior; los subagentes siguen siendo subagentes. El diseño por artefactos
—ninguna etapa lee la conversación de otra— es lo que lo hace seguro.

**Regla (2026-11-09): todo nace en el orquestador, con un contrato por etapa.** `video-orchestrator` es
la única entrada del pipeline: las skills de etapa ya no se invocan sueltas en un chat, y rehacer una
etapa también pasa por él (relanza la hija como revisión y marca `desactualizada`, estado nuevo de
`PIPELINE-STATE.md`, las etapas posteriores que leen lo que cambió). Las conversacionales (③ ④ ⑤ ⑥) son
hijas con las que Santiago habla directo; las automáticas (① ⑦ ⑧ ⑨) corren solas y lo llaman solo para
una decisión suya (gates en [WORKFLOW](WORKFLOW.md)). Cada skill de etapa abre con un *Contrato de la
etapa* y las reglas comunes de toda sesión hija. Consecuencia: `schema-builder` ya no investiga ni
invoca `research-digest`; la investigación es solo la etapa ①, y si Santiago la quiere se la pide al
orquestador.

**Regla (2026-11-09): el orquestador ejecuta, no interroga.** Lo que Santiago no especifica al arrancar
(línea, entrega, investigación) lo toma por defecto y lo registra en `PIPELINE-STATE.md`; las preguntas
de cada etapa (aprobar esquema, guion o visuales, aclarar una toma, aprobar un video generado) las hacen
las hijas. Su única pregunta posible es al cerrar el proyecto: si Santiago quiere un chat para dialogar
sobre cómo funcionó el flujo. Si acepta, el orquestador lanza una sesión hija limpia de retro y pasa su
reporte, tal como Santiago lo dijo, a `wmf-documenter`.

**Riesgo:** (1) las sesiones anidadas de la app de escritorio las conocemos por prensa, no por
documentación oficial; (2) los reportes de las hijas llegan truncados (~400 caracteres), por eso la
línea `ETAPA …` va primero y la principal verifica contra los archivos; (3) nunca se ha corrido un
proyecto completo así.

**Alternativa si falla:** volver a un chat nuevo por etapa abierto a mano (hoy las skills no lo permiten:
habría que reabrir esa vía en cada una), o dejar bajo el orquestador solo las etapas automáticas.

### 🟡 Piezas sin cara (voice-only): `take-organizer` recibe solo audio
Nada del algoritmo de `take-organizer` depende de la imagen (transcribir, marcas, fuzzy match, huecos,
corte). Cambia solo la salida: `voice.wav` y `timecodes.json` con `"media": "audio"`. El guion declara
`Delivery: on-camera | voice-only`; en voice-only no hay `CAM` y toda escena necesita un visual.

**Riesgo:** el corte de audio puro no se ha probado con una grabación real, y un video sin cara depende
más de que los visuales sostengan la retención.
**Qué mirar:** si el corte queda limpio y si hay instantes sin visual que `visuals.md` no cubrió.
**Alternativa si falla:** pasar el audio por `video-use`/`ffmpeg` con revisión manual, o grabar con
pantalla negra para volver al flujo de video.

### 🟡 Estilo visual: planning decide *qué*, edición decide *cómo*; se prueba con el primer video (2026-10-30)
Se mantiene la frontera: Planning dice "un b-roll de data centers", nunca color, tipografía ni
transición; eso lo aplica `edit-composer` desde el Brand Kit o, mientras esté en blanco, desde el estilo
que Santiago acuerda al editar. El primer video real se hace así y se evalúa; no se reabre antes.
**Riesgo:** monotonía, si HyperFrames converge en un look parecido entre videos porque nada aguas arriba
los diferencia.
**Alternativa si pasa:** (a) mover decisiones de estilo a `visual-script` (una pasada de estilo por
pieza: sesión más larga y reintroduce el solape que esta frontera quitó), o (b) refinar HyperFrames y
el Brand Kit (mejores prompts, plantillas más variadas, dirección por proyecto al editar).

---

## `resource-fetcher` (⑦)

### 🟡 Resolver (stock) antes que generar (IA), para imagen, video y SFX
El stock es búsqueda + descarga; generar se factura por llamada y el video generado por segundo de
salida: la llamada más cara de toda la etapa. La mayoría del b-roll es genérico y casi siempre existe
como stock. La vía de stock es el CLI de HeyGen (instalado y autenticado; en SFX y música exige
`--min-score 0.4`).
**Riesgo:** un match de stock puede ser de peor ajuste que uno generado, y el agente puede conformarse
con uno mediocre por seguir la regla al pie de la letra.
**Qué mirar:** si los recursos resueltos por stock se sienten genéricos o fuera de tono.
**Alternativa si falla:** subir la barra de "match razonable", o invertir el default solo para `IMG`
(son baratas de generar y el ajuste importa más que en video).

### 🟢 Gate asimétrico: solo el video generado pausa antes de gastar
Es la única categoría donde una mala decisión del agente cuesta dinero real y no solo tiempo de
revisión. Imagen y SFX generados son baratos; pausar por ellos sería fricción sin beneficio.

### 🟢 El nombre de archivo del recurso es su ID (`IMG-1.png`)
Sin esto, cada etapa posterior tendría que volver a buscar por descripción un recurso ya resuelto. Es
la base de la trazabilidad entre etapas.

### 🟢 `pre-capture-guide.md` no lo toca ningún agente de edición
Es el documento de Santiago para prepararse antes de grabar; no cumple función en la automatización
posterior.

---

## `take-organizer` (⑧)

### 🟡 Palabras de control por voz: "discarded" / "final"
Convierte la selección de tomas de "el agente adivina cuál es mejor" (juicio de Santiago, inaceptable)
a "el agente lee una instrucción explícita": determinístico y sin costo extra, porque él ya sabe en el
momento si la toma sirvió.
**Riesgo:** depende de que la transcripción aísle una palabra suelta rodeada de silencio; puede
confundirla con parte de una oración.
**Qué mirar:** que las marcas se detecten de forma confiable contra la transcripción real.
**Evidencia parcial (2026-11-07, proyecto de Other Content):** con la transcripción local (Parakeet) la
marca "discarded" salió a menudo como "Discord" o "Discard"; la regla funcionó aceptando esas variantes, y
una toma "final" con varios reinicios se resolvió usando la última corrida limpia.
**Alternativa si falla:** una palabra de control menos común, o nombrar archivos a mano
(`take2_discarded.mov`).

### 🟡 Auto-selección cuando hay un solo candidato sin marca y "limpio"
Si no hay muletillas ni reinicios y la línea se comunicó bien, no hace falta preguntar. Reduce
fricción sin sacrificar juicio, porque solo aplica sin ambigüedad entre tomas.
**Riesgo:** la heurística de "limpio" no está definida en detalle: puede ser permisiva (auto-selecciona
algo mediocre) o estricta (nunca ahorra nada).
**Qué mirar:** cuántas auto-selecciones Santiago no habría elegido.
**Alternativa si falla:** endurecer el criterio, o preguntar siempre.

### 🟢 Un archivo continuo por pieza; mapa de tiempos por escena y sub-frase
Dentro de una pieza se graban varias escenas seguidas sin cortar cámara; partir por escena fragmentaría
una toma continua, y `edit-composer` necesita un plano continuo donde montar. La sub-frase solo existe
donde la coreografía la exige.

### 🟢 Cámara y screen se resuelven en vivo con OBS
Santiago graba todo compuesto (iPhone como webcam dentro de OBS), así que no hay dos archivos que
fusionar ni dos pistas de audio que alinear. Queda descartado el diseño anterior (cross-correlación de
audio entre dos grabaciones simultáneas); es el mecanismo a retomar solo si un caso no se puede resolver
en vivo (p. ej. una captura que necesita reencuadre con el PiP de cámara ya quemado en el pixel).

### 🟡 Regla del silencio para decidir si una unión screen↔cámara necesita transición construida
Un hueco de silencio en la unión es una señal barata y objetiva de que ahí se puede cortar y animar.
Sin hueco, se respeta el corte de OBS salvo que la coreografía pida algo que ese corte no da.
**Riesgo:** no probada contra footage real: puede haber huecos que son solo una respiración, o
transiciones que ameritan trabajo pero no tienen hueco.
**Qué mirar:** en el primer video, si las transiciones "gratis" se ven bien y si algún corte duro
debió tener transición.
**Alternativa si falla:** que Santiago marque en `visuals.md` qué uniones necesitan transición
(señal autorada en vez de inferida; cuando inferir del footage falla, se prefiere una señal explícita).

---

## `edit-composer` (⑨)

### 🟢 Un proyecto HyperFrames por tema; long-form siempre primero; sin `shared/`
El long-form produce el material que las derivadas reusan, así que existe antes. Un proyecto por pieza
convertiría el reuso en sincronizar dos proyectos; uno por tema lo evita. Cada pieza queda en
`Final pieces/<pieza>/`, con su render.

### 🟡 Sin "vocabulario de coreografías": se inventa cada vez
Santiago lo difirió a propósito. Catalogar patrones antes de ver un video terminado es diseñar sobre
suposiciones; mejor usar las reglas de `hyperframes-animation` y congelar patrones cuando se repitan.
**Riesgo:** coreografías inconsistentes entre videos, o más lentas de construir que con bloques probados.
**Qué mirar:** si tras varios proyectos ciertas coreografías se repiten con variaciones triviales.
**Alternativa si falla:** mapear los patrones recurrentes a bloques de `hyperframes-registry`
parametrizados por el Brand Kit.

### 🟡 Reuso vía `Raw/visuals/` + recorte inspeccionado o reconstrucción desde fuente
Más simple que mantener sub-composiciones compartidas: todo termina siendo "footage", y HyperFrames ya
soporta reencuadre con verificación por snapshot. La distinción recorte/reconstrucción sale de la
redacción del `visuals.md` de la pieza derivada ("recortado" vs. "recompuesto").
**Riesgo:** es un juicio del agente sobre texto ambiguo; puede clasificar mal un caso límite.
**Qué mirar:** recortes que necesitaban reconstrucción, o al revés.
**Alternativa si falla:** un campo explícito en `visuals.md` (`**Reuso:** recorte | reconstrucción`).

### 🟡 `edit-reviewer`: verificación visual por un agente separado, solo en puntos críticos
Separa "quien construye" de "quien verifica": no crea ni arregla, reporta. Un snapshot en un punto
crítico es barato; no hace falta verificar todo, solo donde la coreografía depende de contenido real
(lenguaje relacional, aterrizajes, reencuadres y los `## Pendientes` del `visuals.md`).
**Riesgo:** falsos negativos (coreografías que dependían de contenido real sin una palabra relacional
obvia).
**Qué mirar:** errores de composición que lleguen a Santiago sin que el revisor los detecte.
**Alternativa si falla:** ampliar las señales, o verificar todo `GEN`/`GFX`/`BROLL` sin filtrar.

### 🟢 Tope de 3 intentos por punto crítico antes de escalar a Santiago
Evita bucles infinitos de autocorrección y da una salida concreta cuando el agente no puede resolver
algo solo (p. ej. el recurso no sirve para lo que la coreografía pedía).

### 🟡 Revisión "al vuelo" (visual por visual) en vez de por lote al final de la pieza
Decisión provisional, a revisar con uso real.
**Riesgo:** más idas y vueltas entre editor y revisor; puede ser más lento sin beneficio.
**Qué mirar:** el tiempo total de la etapa y si algún error solo se hizo visible por construir sobre
una base mal puesta (la razón original).
**Alternativa si falla:** un solo pase por lote al final de cada pieza.

### 🟢 El cierre a Notion reusa `content-hub-manager`
El schema real de Notion ya tiene lo necesario: `Status: Edited` en el flujo `Pending → Scripted →
Recorded → Edited → Scheduled → Published`, y un checkbox `Captions Ready` para short form. No hace
falta un mecanismo nuevo.

### 🟢 Subtítulos quemados: por visual, no por regla global (todavía)
Se decide en `visuals.md` como cualquier otro visual; el Brand Kit podría fijar un default para shorts
más adelante. `edit-composer` invoca `embedded-captions` cuando la coreografía lo pide.

---

## Registro rápido de apuestas activas

| Dónde | Decisión | Riesgo | Alternativa si falla |
|---|---|---|---|
| Sistema | Orquestación con sesiones anidadas | Función conocida por prensa; reportes truncados | Chat nuevo por etapa a mano |
| Sistema | Piezas voice-only | Corte de audio puro no probado | Revisión manual, o pantalla negra |
| Sistema | Estilo solo en edición (Brand Kit en blanco) | Resultado monótono | Estilo en `visual-script`, o refinar HyperFrames y el Brand Kit |
| 1 | Stock antes que generar | Match mediocre por regla rígida | Subir la barra, o generar `IMG` por default |
| 2 | Palabras "discarded"/"final" | La transcripción no aísla la palabra | Palabra menos común, o nombrar archivos |
| 2 | Auto-selección si "limpio" | Heurística mal calibrada | Endurecer criterio, o preguntar siempre |
| 2 | Regla del silencio en uniones | No probada con footage real | Marca explícita en `visuals.md` |
| 3 | Sin vocabulario de coreografías | Inconsistencia entre videos | Catálogo de bloques mapeados |
| 3 | Reuso por texto libre | Clasificación ambigua | Campo explícito en `visuals.md` |
| 3 | Puntos críticos por lenguaje relacional | Falsos negativos | Más señales, o verificar todo |
| 3 | Revisión al vuelo | Más lento sin beneficio | Revisión por lote |
