// Round 2: same font (Space Grotesk + Inter) and grid-paper language across all 4 —
// varying only background/accent tone. No network mesh, no glow, no circuit icon.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";

const base = readFileSync(new URL("./base2.template.html", import.meta.url), "utf8");

function gridSvg(lineColor) {
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='96' height='96'>
    <g stroke='${lineColor}' stroke-width='1'>
      <line x1='0' y1='0' x2='0' y2='96'/><line x1='0' y1='0' x2='96' y2='0'/>
    </g>
  </svg>`;
  return `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`;
}

const themes = {
  "e-slate": {
    label: "E — Slate (grafito frío, azul apagado)",
    bg: "#1B1E22", bgAlt: "#23262B", ink: "#F2F3F5", inkSoft: "rgba(242,243,245,0.6)",
    accent: "#5B8DEF", accentDeep: "#3A63C4", gridLine: "rgba(242,243,245,0.09)",
  },
  "f-graphite": {
    label: "F — Graphite cálido (terracota)",
    bg: "#201C19", bgAlt: "#2A2521", ink: "#F5EFE8", inkSoft: "rgba(245,239,232,0.6)",
    accent: "#E0793B", accentDeep: "#A6501F", gridLine: "rgba(245,239,232,0.09)",
  },
  "g-olive": {
    label: "G — Olive oscuro (mostaza)",
    bg: "#1B1F1B", bgAlt: "#232823", ink: "#F1F2ED", inkSoft: "rgba(241,242,237,0.6)",
    accent: "#C9A227", accentDeep: "#8F7215", gridLine: "rgba(241,242,237,0.09)",
  },
  "h-plum": {
    label: "H — Plum oscuro (rosa polvo)",
    bg: "#201820", bgAlt: "#2A202A", ink: "#F4EDF2", inkSoft: "rgba(244,237,242,0.6)",
    accent: "#D97BA0", accentDeep: "#A6486F", gridLine: "rgba(244,237,242,0.09)",
  },
  "i-black": {
    label: "I — Negro puro (azul limpio)",
    bg: "#0A0A0A", bgAlt: "#161616", ink: "#F5F5F5", inkSoft: "rgba(245,245,245,0.6)",
    accent: "#4C7FE5", accentDeep: "#2F55AE", gridLine: "rgba(245,245,245,0.08)",
  },
  "j-gray": {
    label: "J — Gris oscuro neutro (coral)",
    bg: "#1E1E1E", bgAlt: "#292929", ink: "#F4F4F4", inkSoft: "rgba(244,244,244,0.6)",
    accent: "#D9634F", accentDeep: "#A6402F", gridLine: "rgba(244,244,244,0.08)",
  },
  "k-navy": {
    label: "K — Azul marino oscuro (dorado)",
    bg: "#10162B", bgAlt: "#1A2138", ink: "#F2F4F8", inkSoft: "rgba(242,244,248,0.6)",
    accent: "#E0A83D", accentDeep: "#A67A22", gridLine: "rgba(242,244,248,0.08)",
  },
};

mkdirSync(new URL("./variants2", import.meta.url), { recursive: true });

for (const [key, t] of Object.entries(themes)) {
  const html = base
    .replaceAll("{{THEME_LABEL}}", t.label)
    .replaceAll("{{BG}}", t.bg)
    .replaceAll("{{BG_ALT}}", t.bgAlt)
    .replaceAll("{{INK}}", t.ink)
    .replaceAll("{{INK_SOFT}}", t.inkSoft)
    .replaceAll("{{ACCENT}}", t.accent)
    .replaceAll("{{ACCENT_DEEP}}", t.accentDeep)
    .replaceAll("{{GRID_URL}}", gridSvg(t.gridLine));

  writeFileSync(new URL(`./variants2/${key}.html`, import.meta.url), html, "utf8");
  console.log(`wrote variants2/${key}.html — ${t.label}`);
}
