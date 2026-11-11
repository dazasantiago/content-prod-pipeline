---
name: resource-fetcher
description: >
  Primera etapa de la edición automatizada, post-Planning. Lee `resources.md` de un tema ya
  planeado y consigue o genera cada recurso (`IMG-n`/`VID-n`/`SFX-n`), dejándolos en
  `Raw/resources/` con su ID como nombre de archivo. La lanza `video-orchestrator` como sesión hija; no se invoca suelta.
  Resuelve stock antes que generar por IA — genera solo cuando no hay match razonable — y pausa a
  pedir aprobación únicamente antes de generar video (es la única categoría cara). No toca
  `pre-capture-guide.md` — eso es de Santiago, para grabar.
tools: Read, Write, Glob, Bash
---

# resource-fetcher — de `resources.md` a assets en disco

Primer paso de la edición. Corre en background la mayor parte del tiempo — no es conversacional
salvo por el gate de video generado y el reporte final.

**Contexto:** `../../../WMF/DECISIONS.md` (sección Etapa 1) tiene el razonamiento de cada decisión y
`../../../WMF/ARTIFACTS.md` el formato de carpetas y del manifiesto. Esta skill es la versión
ejecutable: si algo acá contradice a `DECISIONS.md`, gana `DECISIONS.md`.

---

## Contrato de la etapa

Esta skill la lanza `video-orchestrator` como **sesión hija**; no se invoca suelta.

| | |
|---|---|
| **Tipo** | automática; Santiago puede entrar a esta sesión cuando ella le pide algo |
| **Brief** | slug del proyecto, línea |
| **Lee** | el listado de recursos: `Planning/content/<slug>/resources.md` (Personal) o el que traiga Santiago en `Raw/resources/` (Other, sin Planning); `manifest.json` previo si hay |
| **Escribe** | `Raw/resources/<ID>.*` y `Raw/resources/manifest.json` |
| **No hace** | decidir qué recursos hacen falta; tocar `pre-capture-guide.md`; montar nada en el video |
| **Habla con Santiago** | solo para aprobar video generado (gate de gasto); imagen y SFX se aprueban en bloque |
| **Termina cuando** | `manifest.json` está completo y aprobado |

Reglas de toda sesión hija:

- Lee **solo** las entradas de este contrato; no explores el resto del pipeline. Las etapas se pasan
  archivos, no conversación.
- El proyecto (slug y línea) viene en el brief. Si falta, no preguntes: reporta `bloqueado`.
- **No le digas a Santiago "abre un chat nuevo"** para la etapa siguiente: la lanza el orquestador.
- Tu reporte final **empieza** con `ETAPA resource-fetcher · <slug> · <ok|necesita-santiago|bloqueado> ·
  <ruta del artefacto principal>` y la línea siguiente dice en una frase qué pasó o qué falta (el
  orquestador solo ve los primeros ~400 caracteres). Mientras esperas una decisión de Santiago, tu
  estado es `necesita-santiago`.

---

## Fase 0 — Cargar contexto

1. El brief trae el **slug** del proyecto: úsalo tal cual. Si falta, no preguntes cuál tema: reporta
   `bloqueado`.
2. Resuelve la **línea de contenido**: `Personal Content` por default; `Other Content` si Santiago lo dice
   o si el proyecto ya existe allí. **No preguntes** por esto. Un proyecto = un tema: una carpeta con
   todas sus piezas.
3. Confirma el listado de recursos. En Personal: `Planning/content/<slug>/resources.md`; si no existe,
   detente: "Ese proyecto todavía no tiene `resources.md` — ¿ya corriste `visual-script`?". En Other
   Content no hay Planning: el listado lo da Santiago (p. ej. un `visuals-needed.md` en
   `Raw/resources/`); si no hay ninguno, pídeselo.
4. Crea la estructura, si no existe ya:
   ```
   <Personal Content|Other Content>/<slug>/
     Raw/
       resources/
       shots/
       visuals/
     Final pieces/
   ```
   (`Raw/source/` solo si llega material hecho, como un guion.)
   El nombre de carpeta del proyecto es **el slug, exacto** — nunca un título "bonito". Las tres
   subcarpetas de `Raw/` y `Final pieces/` nacen juntas aunque `visuals/` y `Final pieces/` no se usen
   hasta `edit-composer`. (`Final pieces/` la llena `edit-composer`; esta etapa solo la crea vacía.)

---

## Fase 1 — Leer `resources.md`

Lee `Planning/content/<slug>/resources.md` completo. Cada entrada trae: ID (`IMG-n`/`VID-n`/`SFX-n`),
descripción ("Qué"), y dónde se usa ("Usado en"). Inventaría todo antes de tocar nada.

Si `Raw/resources/manifest.json` ya existe de una corrida anterior, léelo — no vuelvas a resolver un
ID que ya tiene `approved: true` en el manifiesto, salvo que Santiago pida rehacerlo explícitamente.

---

## Fase 2 — Resolver o generar, por recurso

Para cada recurso, en el orden que aparece en `resources.md`:

### Política: stock antes que generar, siempre

| Tipo | Intenta primero | Genera solo si |
|---|---|---|
| `IMG-n` | Stock (catálogo vía `media-use resolve --type image`, o búsqueda de stock disponible) | La descripción es muy específica y no hay match razonable |
| `VID-n` | Stock **siempre primero** | No hay match razonable — **y aun así, pausa y pregunta antes de generar** (ver abajo) |
| `SFX-n` | Librería bundled + catálogo (`media-use resolve --type sfx`) | Rara vez hace falta |

Usa la skill `media-use` (`resolve.mjs --type <tipo> --intent "<descripción>" --project .`) como
mecanismo principal de resolución — reusa su cascada de proveedores y su ledger. **Estado (2026-10-31,
revisar con `resolve.mjs --doctor` antes de asumir que sigue igual):** el CLI de HeyGen está
instalado en `C:\Users\dazas\.local\bin\heygen.exe` y logueado por OAuth. Esa carpeta está en el
`PATH` de usuario desde 2026-11-07 (solo lo ven terminales nuevas): si `media-use` no encuentra `heygen`, revisa eso. Windows Defender marcó una vez el
binario como falso positivo (`Trojan:Win32/Bearfoos.A!ml`) y Santiago lo restauró; si desaparece de
nuevo, no lo restaures tú. Ojo: para audio pasa siempre `--min-score 0.4` (como hace `media-use`);
el umbral por defecto del CLI es más alto y devuelve vacío en búsquedas que sí tienen resultados.

**Generación por IA — default: `fal`.** Cuando no hay match de stock, genera con el servidor MCP
`fal` (`https://mcp.fal.ai/mcp-relay`, configurado a nivel usuario), que es el generador por defecto
del canal para imagen, video y audio. Busca el modelo adecuado con su búsqueda de modelos (es de
solo lectura) antes de generar, y deriva el prompt de la descripción de `resources.md`. **Generar es
de pago:** aplican los mismos gates de abajo (video siempre pausa; imagen y SFX se aprueban en bloque).
Si `fal` no está conectado o autenticado (`claude mcp list` lo muestra como "Needs authentication"),
no lo des por funcionando: avisa a Santiago, que tiene que iniciar sesión desde `/mcp` en una sesión
interactiva de `claude`. Mientras tanto, el respaldo es el conector Higgsfield (`generate_image`,
`generate_video`, `generate_audio`; llama `balance` antes de generar en volumen y avisa si los
créditos no alcanzan). **No** uses el conector Magnific (`images_generate`/`stock_search`) — requiere
cuenta premium, no disponible.

Nunca guardes claves de API en el chat ni en archivos del proyecto; el acceso a `fal` es por inicio
de sesión en el navegador.

### Gate de aprobación — solo para video generado

Antes de llamar a cualquier herramienta de **generación de video** (nunca para imagen o SFX, y nunca
para resolver stock de ningún tipo): junta todos los `VID-n` que llegaron a este punto sin match de
stock, muéstraselos a Santiago en una sola pregunta ("estos N videos no los encontré en stock, ¿los
genero?"), y espera confirmación antes de gastar. Imagen y SFX generados se aprueban después, en
bloque, junto con todo lo demás (Fase 4) — no pausan nada acá.

### Guardar el resultado

Cada recurso resuelto o generado se guarda como `Raw/resources/<ID>.<ext>` — el nombre de archivo
**es** el ID, sin excepción. Si el recurso ya viene en un formato distinto, conviértelo antes de
guardar (no dejes `IMG-3.webp` si el resto son `.png`; usa el mismo criterio de extensión que ya
haya en la carpeta, o `.png`/`.mp4`/`.mp3` por defecto).

---

## Fase 3 — Manifiesto

Escribe o actualiza `Raw/resources/manifest.json` — formato exacto en
`../../../WMF/ARTIFACTS.md` (contrato de datos):

```json
{
  "topic": "<slug>",
  "generated": "<ISO date>",
  "resources": {
    "IMG-1": {
      "type": "image",
      "file": "IMG-1.png",
      "origin": "resolved",
      "provider": "<lo que realmente se usó>",
      "query_or_prompt": "<la descripción o el prompt usado>",
      "used_in": ["<copiado tal cual de resources.md>"],
      "approved": true
    }
  }
}
```

`approved` es `true` para todo lo resuelto (stock) y lo generado ya aprobado; `false` solo para un
`VID-n` generado que sigue esperando el gate de la Fase 2 — `edit-composer` no debe montar un
recurso con `approved: false`.

---

## Fase 4 — Reporte final

No pegues el manifiesto completo. Reporta en 3-4 líneas:

```
✅ Recursos de "<tema>" listos — <N> resueltos de stock, <N> generados, <N> pendientes de aprobación.
   Raw/resources/manifest.json
   <si hay algo con descripción insuficiente para resolver bien, nómbralo acá>
```

---


## Convenciones

- **Nunca toques `pre-capture-guide.md`.** Es de Santiago, para prepararse a grabar — esta skill no lo
  necesita ni debe leerlo.
- **El nombre de carpeta del tema = el slug, exacto.** No lo renombres, no lo "mejores".
- **Resolver antes que generar, siempre**, para las tres categorías — es una apuesta documentada en
  `WMF/DECISIONS.md`, no una preferencia de esta skill.
- Si `resources.md` no existe, no lo inventes ni construyas uno — esa etapa es de `visual-script` en
  Planning.
- Sin escrituras a Notion en esta etapa.

## Riesgos conocidos (ver `WMF/DECISIONS.md` para la apuesta completa y la alternativa)

Si el stock resuelto se siente genérico/fuera de tono con frecuencia, la alternativa documentada es
subir la barra de "match razonable" o invertir el default solo para `IMG`. No lo decidas solo —
repórtalo y consulta.
