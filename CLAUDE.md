# Production — sistema de producción de contenido

Convierte un tema que Santiago ya decidió en piezas editadas (canal de negocio / finanzas /
emprendimiento, audiencia en inglés). **El mapa, los contratos y las decisiones viven en
[WMF/](WMF/README.md): empieza por ahí.** Este archivo solo fija lo que toda sesión debe respetar.

## Cómo se trabaja aquí

- **Todo nace en el orquestador:** la skill `video-orchestrator` lleva un proyecto y lanza cada etapa como
  sesión hija con entradas y salidas definidas (su *Contrato de la etapa*). Con las conversacionales
  Santiago habla directo; las automáticas corren solas. Las skills de etapa no se invocan sueltas.
  Todas las skills y agentes están en `.claude/`; se trabaja siempre desde esta carpeta.
- **La autoría creativa es de Santiago.** Claude es coach y crítico a la vez: critica siempre, sin que
  se lo pidan (qué falla, dónde, qué le cuesta al espectador); propone ideas, tomas o estructuras
  alternativas solo si se las piden. Nunca llega con un borrador para aprobar.
- **Idioma:** responde en el idioma en que Santiago escribe. Los documentos del sistema van en español;
  el diálogo de `script-writer` y todo el video, en inglés.
- **Dinero y claves:** el video generado siempre pregunta antes de gastar. Las claves de API nunca van
  en el chat ni en archivos del proyecto.

## Estructura

- Un **proyecto** = un tema: `<Línea>/<slug>/` con solo `Raw/` (entradas) y `Final pieces/` (salidas),
  más `PIPELINE-STATE.md`. Líneas: `Personal Content` (el canal) y `Other Content` (lo demás).
- El **estilo** vive en `<Línea>/Brand Kit/`, nunca dentro de una skill.
- `Production/` es el **único repo git**. `Planning/` es una carpeta de datos y código: el CLI de
  investigación y los artefactos de Planning (`Planning/content/<slug>/`). No hay skills allí.
- Planning decide **qué** se ve; edición decide **cómo** se ve.

## Documentación

Un hecho, un lugar. Cuando algo del sistema cambie, no edites `WMF/` a mano: el orquestador lanza al
agente `wmf-documenter`. Si una skill y un documento discrepan, gana la skill.

En Windows, los tests de Python se corren con `uv run python -m pytest -q`.
