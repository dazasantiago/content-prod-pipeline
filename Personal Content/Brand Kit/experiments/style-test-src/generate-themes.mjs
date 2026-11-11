// Generates 4 themed variants of the same demo composition (base.template.html)
// by substituting {{TOKEN}} placeholders. Run: node generate-themes.mjs
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";

const base = readFileSync(new URL("./base.template.html", import.meta.url), "utf8");

// Reusable inline SVG "constellation" mesh (nodes + connecting lines), color-parameterized.
function meshSvg(lineColor, nodeColor) {
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='480' height='480'>
    <g stroke='${lineColor}' stroke-width='1' fill='none'>
      <path d='M20 40 L140 90 L260 30 L400 110 L460 60'/>
      <path d='M140 90 L120 220 L260 30'/>
      <path d='M120 220 L40 340 L260 30'/>
      <path d='M120 220 L280 260 L400 110'/>
      <path d='M280 260 L200 400 L40 340'/>
      <path d='M280 260 L440 380 L460 60'/>
    </g>
    <g fill='${nodeColor}'>
      <circle cx='20' cy='40' r='3'/><circle cx='140' cy='90' r='4'/><circle cx='260' cy='30' r='3'/>
      <circle cx='400' cy='110' r='3'/><circle cx='460' cy='60' r='3'/><circle cx='120' cy='220' r='4'/>
      <circle cx='40' cy='340' r='3'/><circle cx='280' cy='260' r='4'/><circle cx='200' cy='400' r='3'/>
      <circle cx='440' cy='380' r='3'/>
    </g>
  </svg>`;
  return `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
}

// Reusable inline SVG grid (axis-aligned), color-parameterized.
function gridSvg(lineColor) {
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'>
    <g stroke='${lineColor}' stroke-width='1'>
      <line x1='0' y1='0' x2='0' y2='120'/><line x1='60' y1='0' x2='60' y2='120'/><line x1='120' y1='0' x2='120' y2='120'/>
      <line x1='0' y1='0' x2='120' y2='0'/><line x1='0' y1='60' x2='120' y2='60'/><line x1='0' y1='120' x2='120' y2='120'/>
    </g>
  </svg>`;
  return `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
}

const themes = {
  "a-brand": {
    label: "A — Brand (banner real: oscuro, ámbar único, malla de nodos)",
    bg: "#120D0A", bgAlt: "#1A130F", ink: "#FFFFFF", inkSoft: "rgba(240,234,227,0.72)",
    accent: "#E8823D", accentDeep: "#C85A1E",
    fontDisplay: "'Sora', sans-serif", fontDisplayWeight: 800,
    fontBody: "'Inter', sans-serif",
    radius: "18px", border: "none",
    cardShadow: "0 30px 80px -20px rgba(0,0,0,0.6)",
    glowCore: "#D9793D", glowOpacity: "0.35",
    bgPatternUrl: (m, g) => meshSvg("rgba(217,121,61,0.16)", "rgba(232,130,61,0.55)"),
    bgPatternSize: "480px 480px",
    fontLinks: `<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Sora:wght@800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">`,
  },
  "b-cobalt": {
    label: "B — Cobalt (frío, modernista, grid de risografía)",
    bg: "#F2EFE9", bgAlt: "#E8E3D8", ink: "#141414", inkSoft: "rgba(20,20,20,0.62)",
    accent: "#1E2BFA", accentDeep: "#12189E",
    fontDisplay: "'Space Grotesk', sans-serif", fontDisplayWeight: 700,
    fontBody: "'Inter', sans-serif",
    radius: "0px", border: "2px solid #141414",
    cardShadow: "none",
    glowCore: "#1E2BFA", glowOpacity: "0.06",
    bgPatternUrl: () => gridSvg("rgba(20,20,20,0.08)"),
    bgPatternSize: "120px 120px",
    fontLinks: `<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">`,
  },
  "c-editorial": {
    label: "C — Editorial (cálido, papel, serif, sin patrón tech)",
    bg: "#F1E9DD", bgAlt: "#E9DFCF", ink: "#241A12", inkSoft: "rgba(36,26,18,0.62)",
    accent: "#CC785C", accentDeep: "#9C4E36",
    fontDisplay: "'EB Garamond', serif", fontDisplayWeight: 600,
    fontBody: "'Inter', sans-serif",
    radius: "4px", border: "1px solid rgba(36,26,18,0.18)",
    cardShadow: "0 1px 0 rgba(36,26,18,0.18)",
    glowCore: "#CC785C", glowOpacity: "0.10",
    bgPatternUrl: () => null,
    bgPatternSize: "auto",
    fontLinks: `<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">`,
  },
  "d-neobrutal": {
    label: "D — Neobrutalist (oscuro, un acento verde-lima, bordes duros)",
    bg: "#0A0A0A", bgAlt: "#141414", ink: "#FFFFFF", inkSoft: "rgba(255,255,255,0.7)",
    accent: "#C6F135", accentDeep: "#8FB01A",
    fontDisplay: "'Archivo Black', sans-serif", fontDisplayWeight: 400,
    fontBody: "'Inter', sans-serif",
    radius: "0px", border: "4px solid #FFFFFF",
    cardShadow: "10px 10px 0 #C6F135",
    glowCore: "#C6F135", glowOpacity: "0.12",
    bgPatternUrl: () => meshSvg("rgba(198,241,53,0.14)", "rgba(198,241,53,0.5)"),
    bgPatternSize: "480px 480px",
    fontLinks: `<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;500;600;800&display=swap" rel="stylesheet">`,
  },
};

mkdirSync(new URL("./variants", import.meta.url), { recursive: true });

for (const [key, t] of Object.entries(themes)) {
  const patternUrl = t.bgPatternUrl();
  const bgPatternCss = patternUrl
    ? `background-image: url('${patternUrl}'); background-size: ${t.bgPatternSize}; background-repeat: repeat;`
    : `background-image: none;`;

  let html = base
    .replaceAll("{{THEME_LABEL}}", t.label)
    .replaceAll("{{FONT_LINKS}}", t.fontLinks)
    .replaceAll("{{BG}}", t.bg)
    .replaceAll("{{BG_ALT}}", t.bgAlt)
    .replaceAll("{{INK}}", t.ink)
    .replaceAll("{{INK_SOFT}}", t.inkSoft)
    .replaceAll("{{ACCENT}}", t.accent)
    .replaceAll("{{ACCENT_DEEP}}", t.accentDeep)
    .replaceAll("{{FONT_DISPLAY}}", t.fontDisplay)
    .replaceAll("{{FONT_DISPLAY_WEIGHT}}", String(t.fontDisplayWeight))
    .replaceAll("{{FONT_BODY}}", t.fontBody)
    .replaceAll("{{RADIUS}}", t.radius)
    .replaceAll("{{BORDER}}", t.border)
    .replaceAll("{{CARD_SHADOW}}", t.cardShadow)
    .replaceAll("{{GLOW_CORE}}", t.glowCore)
    .replaceAll("{{GLOW_OPACITY}}", t.glowOpacity)
    .replaceAll("{{BG_PATTERN_CSS}}", bgPatternCss);

  writeFileSync(new URL(`./variants/${key}.html`, import.meta.url), html, "utf8");
  console.log(`wrote variants/${key}.html — ${t.label}`);
}
