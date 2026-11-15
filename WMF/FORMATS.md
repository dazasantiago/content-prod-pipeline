# FORMATS — qué etapas corren según el tipo de video

El canal no tiene formato fijo. Esta tabla dice qué etapa corre y en qué modo para cada tipo. Los
formatos son **recomendaciones de ruta**, no reglas de las skills: las skills son genéricas y tú
decides la ruta al arrancar el proyecto (el orquestador no te pregunta: lo que no digas lo toma por
defecto y lo registra en `PIPELINE-STATE.md`).

Leyenda: ● corre · ◐ versión ligera · ○ se omite · ◌ por definir

| Etapa | Concept (IPO, bonos, acciones) | Case (startup, industria) | News (tech, industrias) | Coverage (vida real, futuro) |
|---|---|---|---|---|
| ① research | ◐ **solo YouTube** (`--sources youtube`): cómo otros creadores estructuran el concepto | ● **profundo**: filings, rondas, prensa, entrevistas | ● hoy completa, todas las fuentes; el modo **fresco** (ventana de días, pocas fuentes) es [B-3](RISKS-AND-BACKLOG.md) | ○ o contexto previo ligero |
| ② digest | ◐ corto: la sección de YouTube y poco más | ● contradicciones y huecos son el ángulo | ◐ corto | ○ |
| ③ schema | ◐ analogía, 3–5 beats, malentendidos comunes | ● tesis, línea de tiempo, cifras, contrapunto | ◐ qué pasó, por qué importa, qué sigue | ◐ plan del evento |
| ④ script | ● | ● | ● | ◌ guion posterior al footage |
| ⑤ visual-script | ● pesado en `GFX`: mecanismos, analogías | ● pesado en dato: gráficas y timelines (`GFX`), capturas de filings (`SCR`) | ◐ titulares, citas, una gráfica | ◐ solo overlays |
| ⑥ resource-fetcher | ◐ pocos recursos | ● muchos: logos, stock, capturas | ◐ capturas y logos | ○ |
| Grabación | cámara | cámara + `SCR` de fuentes | cámara, rápido | footage de campo, sin guion |
| ⑦ take-organizer | ● | ● | ● | ◌ sin anclas de guion |
| ⑧ edit-composer | ● | ● | ● | ● |
| Regla del formato | cada cifra con fuente; sin asesoría personalizada | cada cifra con fuente y fecha | fecha visible del dato; no afirmar lo no confirmado | — |

## Notas

- **Concept** es donde más sobra pipeline. Ruta realista: tema → investigación ligera (solo YouTube) →
  digest corto → schema ligero → script → visual-script → edición. La investigación busca estructura,
  no confirma cifras: eso sigue siendo la regla del formato. Por qué corre: [DECISIONS](DECISIONS.md).
- **Otro formato o sin formato:** ① se omite salvo que la pidas (regla del orquestador).
- **Case** es el único donde ①② pagan su costo completo.
- **News** compite contra el tiempo; el orquestador ya quita la fricción de abrir chats a mano.
- **Coverage** rompe el supuesto central (guion → grabación → edición). Hoy no cabe; la costura (que ⑦
  no exija guion) está reservada, no construida, hasta el primer caso real.
- **Voice-only (sin cara)** es un modo de entrega, no un formato: cualquier formato puede serlo. Se
  declara por pieza en `script.en.md` (`Delivery`). Sin `CAM`; todo instante necesita un visual.
- **Proyectos de Other Content** (fuera del canal, p. ej. una tarea): no pasan por Planning; el guion
  llega hecho a `Raw/source/` y corren ⑥ ⑦ ⑧ con el Brand Kit de Other Content.
- **Disciplina de cifras:** `[UNVERIFIED]` en el guion y ninguno sobrevive a la aprobación. Para
  finanzas basta endurecerlo por formato (cifra → fuente → fecha); no hace falta una etapa de
  fact-check aparte.
- **`GFX` para datos:** es el visual dominante en finanzas: gráficas, líneas de tiempo y contadores
  los dibuja el código, y cada número lleva su `**Datos:**` (cifra, fuente, fecha) en `visuals.md`. Las
  capturas de filings siguen siendo `SCR`. No hay tag `DATA-n` (ver [DECISIONS](DECISIONS.md)).
