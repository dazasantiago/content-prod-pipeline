# WMF — Workflow Management Folder

La documentación del sistema que produce los videos del canal (negocio / finanzas / emprendimiento,
audiencia en inglés). Aquí vive **lo que cruza etapas**: el mapa, los contratos de datos, las
decisiones, los riesgos y cómo operarlo. Lo que es de una sola etapa vive junto a esa etapa.

## Qué leer según lo que necesitas

| Quiero… | Lee |
|---|---|
| Ver el flujo completo de un vistazo | [WORKFLOW](WORKFLOW.md) |
| Saber qué etapas corren para un concepto, un caso o una noticia | [FORMATS](FORMATS.md) |
| Saber qué archivo produce cada etapa, dónde vive y cómo se llama | [ARTIFACTS](ARTIFACTS.md) |
| Arrancar, retomar o arreglar un proyecto | [RUNBOOK](RUNBOOK.md) |
| Entender por qué se decidió algo, o el riesgo de una apuesta | [DECISIONS](DECISIONS.md) |
| Ver qué puede fallar y qué falta por hacer | [RISKS-AND-BACKLOG](RISKS-AND-BACKLOG.md) |
| Saber qué cambió y cuándo | [CHANGELOG](CHANGELOG.md) |
| Ver cómo luce el output de Planning | [reference/example-project](reference/example-project/) |
| Ver lo que está parado a propósito | [reference/parked](reference/parked/) |

## Reglas para que esto se mantenga limpio

1. **Un hecho, un lugar.** Cada cosa se documenta una sola vez; lo demás enlaza.
   - Reglas internas de una etapa → su `SKILL.md` (es lo que Claude ejecuta).
   - Mapa, contratos entre etapas, decisiones, riesgos, operación → aquí.
   - Estilo y preferencias de producción → el `Brand Kit/` de la línea de contenido, no aquí.
2. **Las skills mandan.** Si una skill y un documento de aquí discrepan, gana la skill y se corrige el
   documento.
3. **Una decisión nueva = una entrada en DECISIONS** (con fecha, argumento y, si es apuesta, riesgo y
   alternativa) y una línea en el CHANGELOG. Nada de decisiones sueltas en el chat.
4. **Una apuesta se cierra con un video real**, no con opinión: pasa a 🟢 o se aplica su alternativa.
5. **Todo cambio que toque más de una etapa actualiza [WORKFLOW](WORKFLOW.md)** en el mismo momento,
   para que el diagrama no se desactualice.
6. **Lo obsoleto se borra.** El CHANGELOG es la historia; los demás documentos describen solo lo que
   rige hoy.

## Quién escribe aquí

El agente [`wmf-documenter`](../.claude/agents/wmf-documenter.md). Lo lanza `video-orchestrator`
cuando hay algo que documentar (una decisión, un cambio de etapa o de estructura, un riesgo, una apuesta
confirmada o desmentida, las decisiones y lecciones que reporta la sesión de retro de un proyecto).
Decide a qué documento va cada hecho con la tabla de enrutamiento que lleva incorporada, mantiene el
diagrama y los enlaces y reporta qué tocó.

## Dónde vive el resto

| Qué | Dónde |
|---|---|
| Skills de etapa (Planning y edición) | `.claude/skills/<etapa>/SKILL.md` |
| Orquestación | `.claude/skills/video-orchestrator/SKILL.md` |
| Subagentes | `.claude/agents/` |
| Estilo del canal | `Personal Content/Brand Kit/` (y `Other Content/Brand Kit/`) |
| CLI de investigación | `Planning/code/topic-deep-research/` (su `STAGE.md`) |
| Contexto base para Claude en esta carpeta | `CLAUDE.md` (raíz de `Production/`) |

## Documentación que **no** se crea (a propósito)

Es un canal de una sola persona, así que no hay valor en lo siguiente; se crea cuando cambie el
contexto:

- **Matriz RACI / roles:** hay un solo humano; los dos roles de Claude (coach y crítico) están en
  [WORKFLOW](WORKFLOW.md).
- **Roadmap o cronograma:** el backlog priorizado cubre el siguiente paso real; el calendario de
  publicación es del canal, no del sistema.
- **Plan de pruebas formal:** la prueba es el primer video; el [RUNBOOK](RUNBOOK.md) trae la checklist.
- **SLAs o métricas de pipeline:** sin volumen todavía.
- **Guía de incorporación:** si entra un editor o guionista, se escribe entonces.
