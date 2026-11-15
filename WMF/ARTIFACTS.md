# ARTIFACTS — qué archivos existen, dónde viven y cómo se llaman

El contrato de datos del pipeline. Las etapas se hablan **solo** a través de estos archivos.

## Carpetas

```
Production/                          ← único repo git. Todas las skills y agentes viven en .claude/
├─ .claude/skills/  .claude/agents/  ← el pipeline ejecutable
├─ WMF/                              ← esta documentación
├─ Planning/                         ← el CLI de investigación y los artefactos de Planning (mismo repo)
│  ├─ code/topic-deep-research/      ← CLI de Python (results/<slug>/ = su salida, con `run.json`: qué entregó cada fuente; se versiona solo digest.md)
│  └─ content/<slug>/                ← artefactos de Planning de un proyecto
│     ├─ context.md                  ← lo que entendiste del tema y de lo investigado, con cifras verificadas
│     ├─ schema.md                   ← ángulo + piezas aprobadas
│     ├─ resources.md                ← qué conseguir, sin duplicados entre piezas
│     ├─ pre-capture-guide.md        ← qué preparar antes de grabar
│     └─ <pieza>/                    ← long-form, short-1, x-post…
│        ├─ script.en.md             ← lo que dices y lo que aparece, escena por escena
│        └─ visuals.md               ← coreografía y sonido, por escena
├─ Personal Content/                 ← línea de contenido del canal
│  ├─ Brand Kit/                     ← estilo del canal; hoy en blanco; se versiona (ver su README)
│  └─ <slug>/                        ← un proyecto
│     ├─ PIPELINE-STATE.md           ← memoria del orquestador (el único archivo suelto permitido)
│     ├─ Raw/                        ← entradas
│     │  ├─ resources/               ← <ID>.* y manifest.json
│     │  ├─ shots/                   ← grabaciones; por pieza: camera.mp4 | voice.wav + timecodes.json
│     │  ├─ visuals/                 ← visuales reutilizables que construye edit-composer; `style.md` si el kit no tiene `visual.md`
│     │  └─ source/                  ← solo si llega material hecho (un guion, documentos)
│     └─ Final pieces/               ← salidas
│        └─ <pieza>/                 ← proyecto HyperFrames de la pieza + su render final
└─ Other Content/                    ← proyectos que no son del canal; misma forma que Personal Content
   ├─ Brand Kit/
   └─ <slug>/                        ← sin Planning: el guion y la lista de recursos los trae Santiago
```

**Proyecto** = lo que Planning llama *tema*: una idea con todas sus piezas (long-form, shorts, texto).
No es un video ni una pieza. Su slug es el mismo en `Planning/content/<slug>/` y en la carpeta del
proyecto.

**Un proyecto contiene solo `Raw/` y `Final pieces/`**, más `PIPELINE-STATE.md`. El orquestador crea
el esqueleto al arrancar. Lo que entra va en `Raw/`; lo que sale (renders y los archivos de trabajo de
cada pieza) va en `Final pieces/<pieza>/`.

**El estilo no vive en el workflow.** Las skills son genéricas y leen el Brand Kit de la línea de
contenido; cambiar de estilo es editar archivos del Brand Kit, no skills. Mientras el kit no tenga
`visual.md` (hoy, en ambas líneas), el estilo del proyecto lo acuerda `edit-composer` con Santiago y
queda en `Raw/visuals/style.md` (texto libre, no JSON); si se va a repetir, sube al kit como `visual.md`.

**Git.** `Production/` es el único repo. Versiona el sistema (skills, agentes, WMF
y los Brand Kit), el CLI de investigación (`Planning/code/topic-deep-research`: código, tests, `STAGE.md`,
`uv.lock`), `Planning/content/` y el `digest.md` de cada tema. Ignora el JSON crudo de la investigación
(`results/*/*.json`), `.env`, `.venv` y cachés, el contenido de los proyectos y todo archivo de media.

## Reglas de nombres

- **Slug del proyecto:** exacto, nunca un título "bonito". Lo crea un agente, nunca Santiago a mano.
- **Slug de pieza:** se acuerda en `schema-builder` y lo reutiliza todo lo que viene después.
- **Escenas:** el número viene de `script.en.md` y es permanente. Una escena es una sección
  argumentativa, no un visual; suele tener varios visuales.
- **IDs correlativos por proyecto** (permite deduplicar):
  - Visuales: `CAM-n`, `SCR-n`, `BROLL-n`, `GEN-n`, `GFX-n`
  - Recursos: `IMG-n`, `VID-n`, `SFX-n`. El archivo se llama como su ID (`IMG-1.png`).
- Un visual reutilizado de otra pieza se nombra con su origen: `SCR-2 (long-form)`. La escena nunca se
  reutiliza; el visual sí.

## Estados

| Archivo | Cómo marca "aprobado" |
|---|---|
| `context.md` | `**Estado:** aprobado <fecha>` en el encabezado (`en progreso` mientras se trabaja); cada `[UNVERIFIED]` se verifica o Santiago decide dejarlo fuera, y queda anotado |
| `schema.md` | lista de piezas aprobadas al inicio; al aprobar se crean Topic y Pieces en Notion (`In Production`) |
| `script.en.md` | estado en el encabezado; sin `[UNVERIFIED]` pendientes |
| `visuals.md` | `**Estado:** aprobado <fecha>` |
| `manifest.json` | `approved: true` por recurso |
| `PIPELINE-STATE.md` | por etapa: `pendiente`, `omitida`, `en curso`, `esperando a Santiago`, `hecha`, `bloqueada`, `desactualizada` (hecha, pero se rehízo una etapa anterior y cambió lo que lee) |
| Notion (Content Hub) | Topic y Pieces: `In Production` → `Edited` (lo cierra `edit-composer`) |

Cabeceras que otras etapas leen: en `script.en.md`, `**Delivery:** on-camera | voice-only` y
`**Research:**` (`ninguno` si no hubo). `timecodes.json` lleva `"media": "audio"` si la pieza es
voice-only.

`context.md` es el universo de hechos de ④ y ⑤ (secciones y reglas: [SKILL](../.claude/skills/contextualizer/SKILL.md)):
toda cifra, fecha, nombre propio, norma o plazo va como `dato · fuente · fecha de consulta` (fuente
primaria, o dos independientes); lo no verificable queda `[UNVERIFIED]`, visible. Lo que no está en
`context.md` ni en `digest.md` es `[UNVERIFIED]` para ⑤.

Campo de `visuals.md` que otras etapas leen: `**Datos:** <cifra> · <fuente> · <fecha>` en todo `GFX`
que muestre números. Lo escribe ⑥ con las fuentes que ya declara el guion; ⑨ dibuja exactamente eso y
`edit-reviewer` lo contrasta. Si falta una cifra va a `## Pendientes`. Por qué:
[DECISIONS](DECISIONS.md).

## Contrato de datos (JSON, nunca se editan a mano)

Tres archivos, uno por etapa; no se fusionan porque cada etapa siguiente lee solo el suyo.

### `Raw/resources/manifest.json` — lo escribe `resource-fetcher`

Traduce ID → archivo real + procedencia, para que `edit-composer` no busque por descripción.

```json
{
  "topic": "<slug>",
  "generated": "<ISO date>",
  "resources": {
    "IMG-1": {
      "type": "image",
      "file": "IMG-1.png",
      "origin": "resolved",
      "provider": "heygen-stock",
      "query_or_prompt": "persona editando video en su computadora, plano medio",
      "used_in": ["long-form GEN-1 (Escena 2)"],
      "approved": true
    },
    "VID-1": {
      "type": "video",
      "file": "VID-1.mp4",
      "origin": "generated",
      "provider": "fal",
      "query_or_prompt": "barra de progreso de un render largo avanzando",
      "used_in": ["long-form BROLL-1 (Escena 5)"],
      "approved": false
    }
  }
}
```

`approved: false` es el gate del video generado: `edit-composer` no monta un recurso con esa bandera.

### `Raw/shots/<pieza>/timecodes.json` — lo escribe `take-organizer`

Todo lo que `edit-composer` necesita para saber *cuándo* entra cada visual: qué toma cubre qué escena,
anclas de entrada/salida y marcas de silencio en cada unión.

```json
{
  "topic": "<slug>",
  "piece": "long-form",
  "cut_file": "camera.mp4",
  "generated": "<ISO date>",
  "scenes": [
    {
      "scene": 1,
      "start": 0.0,
      "end": 14.2,
      "anchor_line": "There's no timeline. There's no track. There's this — an HTML file.",
      "selection": {
        "raw_source": "Raw/shots/session1.mov",
        "segment": [12.4, 26.6],
        "marker": "final",
        "auto_selected": false
      },
      "sub_anchors": [
        { "phrase": "There's this", "timestamp": 5.8, "role": "entry", "visual": "SCR-1" }
      ]
    }
  ],
  "boundaries": [
    { "between": [1, 2], "silence_gap": true, "gap_duration": 0.4 }
  ]
}
```

`marker` deja rastro de si la selección vino de una marca explícita o de auto-selección.
`sub_anchors` lleva `role: entry | exit` porque un mismo visual puede anclar su entrada y su salida a
dos frases distintas de la misma escena.

### `Raw/visuals/manifest.json` — lo escribe `edit-composer` al terminar el long-form

Qué visuales quedaron disponibles para reuso y cómo debe tratarlos la pieza derivada; se resuelve una
vez, al construir el long-form. Si el Brand Kit trae un pool de paletas (`palettes.md`), guarda también
el `palette_id` sorteado del proyecto; sin pool el campo no existe.

```json
{
  "topic": "<slug>",
  "palette_id": "e-slate",
  "visuals": {
    "SCR-2": {
      "origin_piece": "long-form",
      "file": "SCR-2.mp4",
      "rendered": "<ISO date>",
      "reused_by": ["short-1"],
      "reuse_type": "crop"
    },
    "GFX-1": {
      "origin_piece": "long-form",
      "file": "GFX-1.mp4",
      "source_composition": "Final pieces/long-form/index.html#GFX-1",
      "rendered": "<ISO date>",
      "reused_by": ["short-1"],
      "reuse_type": "reconstruct"
    }
  }
}
```

`reuse_type` es `crop` (recorte) o `reconstruct` (reconstrucción con otro layout). `source_composition`
solo existe para `reconstruct`: dice dónde está el HTML/GSAP original.

## Ejemplo de referencia

[reference/example-project/](reference/example-project/) es el output completo de Planning de un
proyecto de punta a punta (`schema.md`, `script.en.md`, `visuals.md`, `resources.md`,
`pre-capture-guide.md`). Es la referencia de forma de las skills; **no lo borres**. Muestra un visual
que vuelve en otra escena, uno reutilizado entre piezas y uno que no se puede reutilizar (vertical).
