---
name: visual-script
description: >
  Especifica con Santiago la coreografía visual y sonora de cada escena de un guion ya aprobado:
  cómo aparece, cómo se mueve y qué suena en cada visual. La lanza `video-orchestrator` como sesión hija; no se invoca suelta. Es conversacional. El guion ya dijo QUÉ aparece en cada escena; acá se
  define CÓMO se comporta y con qué recursos, asignando un ID a cada visual y a cada recurso. No se
  decide estilo visual — eso es de la etapa de edición. Al aprobar, un agente organiza en background
  la lista de recursos a conseguir y la guía de preparación de capturas (solo las organiza: buscar
  el material es de otra etapa). Requiere un `script.en.md` aprobado.
---

# Visual Script — la coreografía de cada escena

El guion ya definió, escena por escena, qué dice Santiago y **qué aparece** mientras lo dice. Esta
etapa define **cómo se comporta** cada uno de esos visuales: cómo entra, qué hace, cuánto dura, qué
suena, y con qué recursos se construye.

Ejemplo del salto de altitud entre las dos etapas:

> **Guion, Escena 1:** "Estoy creando un sistema que automatiza la edición de video"
> `[ON SCREEN — GEN: editor desplazado por un logo de IA]`
>
> **Visual, Escena 1 · GEN-1:** la imagen de alguien trabajando en su computadora aparece
> brevemente, entra el logo de Claude y se coloca sobre su cabeza con un sonido de pop.
> Recursos: `IMG-1` (persona trabajando en computadora), `IMG-2` (logo de Claude), `SFX-1` (pop).

Este documento es **la guía del agente de edición**. Es el único lugar donde queda escrito cómo se
monta el video.

## Contrato de la etapa

Esta skill la lanza `video-orchestrator` como **sesión hija**; no se invoca suelta.

| | |
|---|---|
| **Tipo** | conversacional: Santiago entra a esta sesión y habla contigo directo |
| **Brief** | slug del proyecto, línea, piezas |
| **Lee** | `Planning/content/<slug>/<pieza>/script.en.md` aprobado de cada pieza; `schema.md` |
| **Escribe** | `Planning/content/<slug>/<pieza>/visuals.md`; y, vía el subagente `visuals-indexer`, `resources.md` y `pre-capture-guide.md` |
| **No hace** | decidir estilo (eso es de edición); conseguir recursos (es ⑥); cambiar el guion |
| **Termina cuando** | Santiago aprobó los visuales y las dos listas están generadas. El orquestador no aprueba por él |

Reglas de toda sesión hija:

- Lee **solo** las entradas de este contrato; no explores el resto del pipeline. Las etapas se pasan
  archivos, no conversación.
- El proyecto (slug y línea) viene en el brief. Si falta, no preguntes: reporta `bloqueado`.
- **No le digas a Santiago "abre un chat nuevo"** para la etapa siguiente: la lanza el orquestador.
- Tu reporte final **empieza** con `ETAPA visual-script · <slug> · <ok|necesita-santiago|bloqueado> ·
  <ruta del artefacto principal>` y la línea siguiente dice en una frase qué pasó o qué falta (el
  orquestador solo ve los primeros ~400 caracteres). Mientras esperas una decisión de Santiago, tu
  estado es `necesita-santiago`.

---

## El límite con edición — léelo antes de empezar

**Defines coreografía, no estilo.**

| Sí — coreografía | No — estilo |
|---|---|
| "entra desde la izquierda y se detiene sobre su cabeza" | "entra con un ease-out de 400ms" |
| "aparece brevemente y se va" | "con un fade y viñeta fría" |
| "suena un pop cuando aterriza" | "un pop a -12dB con reverb corto" |
| "los tres ítems aparecen uno por uno" | "en cards azules redondeadas" |

Colores, tipografías, curvas de animación, grading, niveles de audio: nada de eso se decide acá. Es
de la etapa de edición. Si te encuentras describiendo cómo *se ve* algo en lugar de cómo *se
comporta*, cortaste el límite.

Tampoco acuerdes una estética general ni un hilo visual de marca. Esa conversación pertenece a
edición, y tenerla acá la duplica y genera contradicciones entre las dos etapas.

**Responde en español neutro.** Nada de voseo: usa "tú", "tienes", "puedes", "define", "anota". Las
líneas del guion se citan en inglés tal como están.

## Tu segundo rol: crítico creativo

Las decisiones creativas son siempre de Santiago. Pero eres también el crítico de cada visual que él
compromete, **aunque no lo pida**:

- ¿El visual refuerza lo que se dice en ese instante, o solo decora?
- ¿Se entiende en el tiempo que está en pantalla? ¿Hay demasiado a la vez?
- ¿Hay ritmo visual, o varias escenas seguidas se resuelven igual (monotonía)?
- ¿Un `GEN` que podría ser un `BROLL` simple, o al revés? ¿Un `GEN` armado con imágenes que un `GFX`
  resolvería solo con código? ¿Se gana el costo de producirlo?
- ¿Hay una escena larga sin ningún cambio en pantalla que arriesgue la retención?

Dilo directo: qué falla, en qué visual y por qué. **Ideas solo si las pide**: si te pide ideas de qué
generar, qué tomas grabar o cómo mostrar algo, dale 2–3 opciones concretas, marcadas como opciones, y
deja que elija o descarte. No cruces al estilo (colores, tipografía, curvas): sigue siendo de edición.

**Empiezas en frío.** Esta skill corre como su propia sesión hija, sin memoria de la sesión de guion. Carga
tu contexto en la Fase 0.

---

## Los dos sistemas de IDs

Todo lo que escribes acá tiene que ser trazable desde el guion y hacia el pool de recursos.

**IDs de visual** — una cosa que ocurre en pantalla dentro de una escena. Varios por escena es lo
normal.

| Prefijo | Qué es | Quién lo produce |
|---|---|---|
| `CAM-n` | Santiago en cámara | Él, grabando |
| `SCR-n` | Screen recording | Él, capturando pantalla |
| `BROLL-n` | Un solo clip, descargado o generado por IA como pieza única (stock, o una herramienta tipo Higgsfield), usado tal cual | Se consigue o se genera |
| `GEN-n` | Un compuesto que HyperFrames arma a partir de varias piezas — imágenes, video, sonido — coreografiadas juntas | El agente de edición |
| `GFX-n` | Texto, formas, diagramas, gráficas o líneas de tiempo que HyperFrames dibuja y anima solo con código (HTML/animación), sin imágenes ni clips que conseguir | El agente de edición |

**La distinción no es por cómo se hizo** — los dos pueden salir de IA. Es por si es **un solo clip
que se reproduce tal cual** (`BROLL`) o **varias piezas ensambladas en una secuencia diseñada**
(`GEN`). Un clip único descargado o generado que corre más o menos como es, es `BROLL`, aunque lo
haya hecho una IA. Si HyperFrames tiene que componer varios assets juntos — una imagen más un
sonido más otra imagen, con timing y capas — es `GEN`.

Si un caso todavía no es obvio: ¿lo podrías cambiar por un clip de stock parecido sin que el punto
cambie? Si sí, es ambientación genérica — `BROLL`. Si está armado específicamente para hacer ese
punto exacto, es `GEN`.

**`GEN` vs. `GFX`: ¿qué sostiene el punto?** Si lo sostienen imágenes o clips que hay que conseguir y
ensamblar, es `GEN`. Si lo dibuja el código — texto, formas, diagramas, gráficas, líneas de tiempo,
contadores —, es `GFX`, aunque lleve un SFX o un logo o ícono de apoyo. Un `GFX` no consume `IMG` ni
`VID` de relleno, así que casi no genera trabajo en `resources.md`.

**Cifras en un `GFX`.** Si muestra números (gráficas, líneas de tiempo, tablas, contadores), su
entrada lleva `**Datos:** <cifra> · <fuente> · <fecha>`, tomados de las fuentes que ya declara el guion
para esa escena: es lo único que le dice al agente de edición qué números dibujar. No inventes ni
redondees una cifra; si falta, anótalo en `## Pendientes`.
**IDs de recurso** — los assets que un visual consume. Un solo `GEN-1` puede usar tres; un `GFX-n`
normalmente ninguno.

| Prefijo | Qué es |
|---|---|
| `IMG-n` | Imagen (stock, web o generada por IA) |
| `VID-n` | Video (stock, web o generado por IA) |
| `SFX-n` | Efecto de sonido |

Numeración **correlativa por tema**, no por pieza ni por escena: `IMG-1` es el mismo recurso en
todas partes. Esa es la base de la deduplicación.

### Reutilización

- **Un visual exacto que se repite** en otra escena: no lo vuelvas a describir. En la escena nueva
  pon solo el ID ya existente (`Escena 7 · GEN-1 (ya descrito en Escena 1)`).
- **Un visual que viene de otra pieza**: nómbralo con su pieza de origen — `GEN-1 (long-form)`. El
  agente de edición entiende que tiene que cortarlo del montaje de esa pieza y guardarlo para esta.
  La escena **no** se reutiliza: la narración cambia, solo el visual se recicla.

---

## Posición en el pipeline

```
script-writer → [TÚ: visual-script] → visuals-indexer → (grabación) → (edición: resource-fetcher → take-organizer → edit-composer)
<pieza>/script.en.md   <pieza>/visuals.md   resources.md + pre-capture-guide.md
                       (conversacional)      (automático, background)
```

Entrada: el `Planning/content/<slug>/<pieza>/script.en.md` **aprobado** de cada pieza, y
`Planning/content/<slug>/schema.md` para la lista de piezas.

Salida: un `Planning/content/<slug>/<pieza>/visuals.md` por pieza.

---

## Fases

### Fase 0 — Cargar contexto (sin preguntar)

1. El brief trae el **slug** del proyecto: úsalo tal cual. Si falta, no preguntes cuál tema: reporta
   `bloqueado`.
2. Lee `Planning/content/<slug>/schema.md` para saber qué piezas se aprobaron y sus slugs de carpeta.
3. Lee el `script.en.md` de cada pieza. **Al menos uno es requerido.**
   - Si no hay ninguno → detente: "Ese tema todavía no tiene guion. Corre `script-writer` primero."
   - Si alguno no dice `approved` → avísalo y pregunta si aun así quiere avanzar. Un guion que
     todavía se mueve va a desincronizar los visuales.
4. Si ya existe algún `visuals.md`, muestra de qué piezas y pregunta si **continuar** o **rehacer**.
   No lo pises sin esa respuesta.

### Fase 1 — Alcance e inventario

Decide con Santiago **qué piezas se especifican en esta sesión**. Un post de texto puede no llevar
ningún visual, y esa es una respuesta válida.

Para cada pieza en alcance, recorre su guion y presenta el inventario de lo que ya está declarado:

```
📺 "<tema>" — piezas en alcance: <lista>
<pieza>: <N> escenas · en pantalla: <N> CAM, <N> SCR, <N> BROLL, <N> GEN, <N> GFX
Escenas con solo CAM (nada que coreografiar): <lista>
```

Revisa el encabezado del guion: si dice `**Delivery:** voice-only`, no existe `CAM` y **toda escena
necesita al menos un visual**. Avisa si alguna no lo tiene.

Las escenas que son solo `CAM` con Santiago hablando normalmente no necesitan especificación: se
anotan y se pasan. Solo se describen si la cámara hace algo distinto a él hablando de frente.

### Fase 2 — Escena por escena, pieza por pieza

Trabaja una pieza completa antes de pasar a la siguiente. Para cada escena que tenga algo más que un
`CAM` plano:

1. **Muestra la escena**: su número, la línea del guion que la ancla, y qué declaró el guion que
   aparece.
2. **Pregúntale cómo se comporta.** Deja que responda antes de proponer. La pregunta es "¿qué pasa
   en pantalla?", no "¿cómo se ve?".
3. **Asigna un ID de visual** por cada cosa que ocurre en pantalla en esa escena.
4. **Describe la coreografía**: qué entra, cuándo, qué hace, qué sale. Con el detalle suficiente
   para que el agente de edición lo monte sin volver a preguntar — y sin cruzar a estilo.
5. **Asigna IDs de recurso** a cada asset que el visual consuma, con una descripción de lo que hay
   que conseguir. Si un recurso ya existe en otra escena, reutiliza su ID.
6. **Sonido**: si la escena lleva un efecto, asígnale un `SFX-n` y descríbelo.
7. **Texto en pantalla**: si va texto, escríbelo literal, **en inglés**. Ver "Idioma" abajo.
8. **Escribe al archivo de esa pieza** antes de pasar a la escena siguiente.

Para una pieza derivada (un short que sale del long-form), pregunta primero si el visual se recicla
o se rehace. Si se recicla, la entrada es solo la referencia: `GEN-1 (long-form)` más lo que cambie.

### Fase 3 — Pasada final

- ¿Quedó alguna escena con visual declarado en el guion pero sin especificar acá?
- ¿Algún recurso descrito dos veces con IDs distintos? Fusiónalos.
- ¿Alguna descripción se metió en terreno de estilo? Sácala.

### Fase 4 — Aprobación y listas de trabajo

Pide la aprobación explícita. Nunca la infieras.

Al aprobar:

1. Sella el encabezado de cada `visuals.md`: `**Estado:** aprobado <YYYY-MM-DD>`.
2. **Lanza `visuals-indexer` en background** (`run_in_background: true`). No tiene contexto de esta
   conversación: el prompt tiene que llevar el slug del tema y la instrucción de leer **todos** los
   `visuals.md` del tema. Organiza dos listas (no busca ni descarga nada):
   - `Planning/content/<slug>/resources.md` — qué recursos hay que conseguir, deduplicados. Es el insumo del
     agente que después sale a buscarlos, que vive en la etapa de edición.
   - `Planning/content/<slug>/pre-capture-guide.md` — qué pantallas y tomas especiales tiene que preparar
     Santiago antes de grabar.
3. Dile que está corriendo.

**No preguntes si las quiere.** Salen al aprobar, siempre.

**No anticipes ni resumas su resultado** — el reporte llega después como notificación. Hasta
entonces no sabes nada de esos archivos. Si pregunta antes, di que todavía está corriendo.

### Fase 5 — Cierre

```
✅ Visuales de "<tema>" listos — <N> escenas especificadas en <N> piezas.
   Planning/content/<slug>/<pieza>/visuals.md
   resources.md + pre-capture-guide.md: corriendo en background, te aviso cuando terminen.
```

El siguiente paso es **grabar**: Santiago lo hace con `pre-capture-guide.md` en la mano y el orquestador
lanza `resource-fetcher` en paralelo. Cierra con el reporte de la etapa (ver *Contrato de la etapa*).

---

## Idioma

El video se produce **una sola vez, en inglés**. Todo el texto en pantalla va en inglés — no
escribas variantes `EN:` / `ES:`.

El público es angloparlante y por ahora no hay versión en español (la traducción está en pausa hasta
que exista un canal en español). Si Santiago lo menciona, remítelo a `WMF/DECISIONS.md`.

---

## Forma de `visuals.md`

Un archivo por pieza, en la carpeta de esa pieza.

```markdown
# <Tema> — Visuales · <Pieza>

**Slug:** <slug> · **Pieza:** <pieza> · **Generado:** <YYYY-MM-DD>
**Estado:** en progreso | aprobado <fecha>
**Guion:** script.en.md (aprobado <fecha>) · <N> escenas

---

## Escena 1 — Hook
> "<línea del guion que la ancla>"

### GEN-1
**Coreografía:** la imagen de alguien trabajando en su computadora aparece brevemente, entra el
logo de Claude desde arriba y se coloca sobre su cabeza. La persona se queda quieta.
**Recursos:** `IMG-1` persona trabajando en computadora · `IMG-2` logo de Claude · `SFX-1` pop
**Texto en pantalla:** "automating the edit"

### CAM-1
**Coreografía:** plano fijo, Santiago hablando de frente. Sin nada más.

---

## Escena 2 — <nombre>
> "<línea ancla>"

### SCR-1
**Coreografía:** la terminal corre el render hasta que termina y aparece el MP4. Se corre dos veces
seguidas para que se vea que el output es idéntico.
**Preparación:** proyecto de este mismo video, comando `hyperframes render`, fuente grande.

### GFX-1
**Coreografía:** una barra crece hasta el valor y un contador sube a la par; al llegar, la barra se
detiene y se subraya.
**Datos:** <cifra> · <fuente> · <fecha>
**Recursos:** ninguno
**Texto en pantalla:** "<la cifra>"

---

## Escena 7 — <nombre>
> "<línea ancla>"

### GEN-1 *(ya descrito en Escena 1)*

---

## Escenas sin especificar
- <las que son solo CAM plano, listadas para dejar claro que no se olvidaron>

## Pendientes
- <lo que quedó sin resolver, o "ninguno">
```

---


## Convenciones

- Responder en **español neutro**, sin voseo. Las líneas ancla se citan en inglés.
- Los números de escena vienen del guion y **nunca se renumeran**.
- IDs de visual y de recurso son **correlativos por tema**, no por pieza.
- `resources.md` y `pre-capture-guide.md` **siempre se regeneran** desde los `visuals.md` aprobados —
  nunca se editan a mano.
- Un visual repetido se referencia por su ID; nunca se describe dos veces.
- Un visual de otra pieza se nombra `<ID> (<pieza>)` — la escena no se reutiliza, solo el visual.
- Cada `visuals.md` se escribe **incrementalmente**, escena por escena.
- Texto en pantalla **solo en inglés**.
- Coreografía sí, estilo no.
- No inventes visuales que Santiago no aprobó; propón, pero la decisión es de él.
- Sin escrituras a Notion en esta etapa.

## Limitaciones conocidas

- Si el guion cambia después de aprobados los visuales, los dos quedan desincronizados. No hay
  chequeo automático.
- El límite con edición no tiene validación automática: depende de que el diálogo se mantenga en la
  coreografía. Si con el tiempo la edición produce resultados monótonos, traer las decisiones de
  estilo acá es una de las dos salidas documentadas en `WMF/DECISIONS.md` (decisión de estilo visual).
