# Brand Kit — Personal Content

Todo lo que hace que un video se **vea y suene como tu canal**, separado del workflow. Las skills son
genéricas y leen esta carpeta; si cambia tu estilo, cambias estos archivos, no las skills. Cada línea
de contenido tiene su propio kit (`Other Content/Brand Kit/`).

**Hoy está en blanco a propósito (2026-11-09).** El primer video prueba el estilo en la edición:
`edit-composer` te pregunta el estilo del proyecto y lo guarda en `Raw/visuals/style.md` del proyecto.
Cuando un estilo se repita, se sube aquí.

## Cómo crece

- **Un tema = un `.md`:** `visual.md` (identidad visual), `palettes.md` (colores), `audio.md`, `voice.md`,
  `motion.md`… `edit-composer` lee todos los `.md` de esta carpeta; ninguno es obligatorio mientras el
  kit esté en blanco, y `visual.md` es el que activa el kit.
- **Valores normativos en el frontmatter, criterio en la prosa**, y lo rechazado con su razón, para no
  reabrirlo.
- Las skills **no** llevan valores de estilo dentro; los citan de aquí. Un valor nuevo se prueba
  renderizado antes de entrar.
- Esta carpeta sí se versiona en git (el resto de `Personal Content/` no).

## Pruebas de estilo

`experiments/` conserva las pruebas de estilo hechas antes del giro del canal. No es entrada de ninguna
etapa ni parte del kit.
