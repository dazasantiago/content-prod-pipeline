# RISKS-AND-BACKLOG — qué puede fallar y qué falta

Una sola lista viva. Cuando algo se resuelve se **borra** de aquí y se anota en el
[CHANGELOG](CHANGELOG.md); la razón de fondo vive en [DECISIONS](DECISIONS.md). Las apuestas técnicas
con su alternativa están en el registro rápido de DECISIONS; aquí van los riesgos del **sistema** y el
trabajo pendiente.

## Riesgos

| # | Riesgo | Impacto | Mitigación / disparador |
|---|---|---|---|
| R-1 | **Ningún proyecto del canal ha pasado por todo el pipeline.** Las apuestas 🟡 son hipótesis (el proyecto de Other Content solo aportó evidencia parcial de `take-organizer`) | Alto | El primer video del canal es la prueba; cerrar cada apuesta después |
| R-2 | **Sesiones anidadas conocidas por prensa**, no por documentación oficial; los reportes de las hijas llegan truncados (~400 caracteres) | Medio | Línea `ETAPA …` primero + verificación por archivo. Si falla: chat nuevo por etapa a mano |
| R-4 | **Dependencia de terceros** (HeyGen, fal, Higgsfield, Notion) | Medio | Stock + dos generadores dan redundancia en recursos; Notion es único |
| R-5 | **Defender puede borrar el CLI de HeyGen** (falso positivo, ya pasó una vez) | Bajo | Lo restaura Santiago; ver [RUNBOOK](RUNBOOK.md) |
| R-6 | **Sesgo tech residual** en las fuentes de investigación (HN, YouTube, X, Tavily) | Bajo-medio | B-3 |
| R-7 | **Monotonía visual** si todo converge al mismo look | Medio | Decisión de estilo pendiente a propósito; el estilo se acuerda por proyecto y se revisa tras el primer video. Si uno se repite, B-7 |
| R-8 | **Material pesado fuera de git** (videos, `Raw/`, renders) sin respaldo propio | Medio | GitHub no los admite (límite de 100 MB por archivo); respaldarlos en un disco o en Drive |
| R-9 | **La transcripción de YouTube depende de que YouTube no bloquee la IP.** Sin transcripción, el video no aporta estructura al digest | Bajo-medio | El CLI avisa del bloqueo; respaldo `YOUTUBE_COOKIES_FILE` (cookies de un navegador con sesión). Ver [RUNBOOK](RUNBOOK.md) |

## Decisiones abiertas (son tuyas)

Ninguna abierta por ahora.

## Backlog (por prioridad)

| ID | Qué | Esfuerzo | Por qué en ese orden |
|---|---|---|---|
| B-1 | **Grabar y editar el primer video del canal** y cerrar las apuestas 🟡 | — | Es la prueba de todo lo demás |
| B-2 | Primer commit de `Production/` (único repo: sistema + `Planning/`) y un remoto para él (solo texto) | Bajo | Hoy el repo no tiene commits |
| B-3 | Investigación modular: modos `verify` / `deep` / `fresh`, ventana de recencia, fuentes de negocio (filings, earnings) en vez de HN | Medio-alto | Se pide con el primer Case o News real |
| B-4 | Taxonomía de Notion `Content Type`: hoy `News / Tool Review / Workflow Walkthrough` → `Concept / Case / News` (y que `schema-builder` Fase 5 la use) | Bajo | `schema-builder` crea hoy con la taxonomía del canal anterior |
| B-5 | Probar el corte de audio puro (voice-only) con una grabación real | Bajo | Apuesta 🟡 sin evidencia |
| B-7 | Repoblar los Brand Kit (hoy en blanco): un `visual.md` por línea cuando un estilo se repita entre proyectos, y luego `audio.md`, `voice.md`, `motion.md` | Bajo | Se crean cuando un video muestre qué preferencias hacen falta; `edit-composer` ofrece subir el estilo acordado (solo con tu sí) |
| B-8 | Desacoplar ⑦ y ⑧: anclas desde `script.en.md`, precondiciones por pieza, "long-form primero" solo si hay reuso | Medio | Toca decisiones cerradas; solo si un video real lo exige |
| B-9 | Costura para Coverage (⑦ sin guion) | — | Reservar; construir con el primer caso real |
| B-10 | Formatos como configuración: `formats/<formato>.md` que las skills lean en su Fase 0 (hoy [FORMATS](FORMATS.md) es solo documentación) | Medio | Después de ver qué formatos se repiten |
| B-11 | Probar la búsqueda de X del CLI con una corrida real, de punta a punta | Bajo | Gasta saldo prepago por publicación devuelta (costo en [STAGE.md](../Planning/code/topic-deep-research/STAGE.md)); la parte de YouTube ya se probó con un tema real, la de X no |
