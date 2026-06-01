/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        obsidian:  "#030305",
        cyan:      "#00f2fe",
        amber:     "#ffb300",
        crimson:   "#ff0055",
        "cyan-dim": "#00a8b5",
        "panel-bg": "rgba(3,3,5,0.82)",
        "glass-border": "rgba(0,242,254,0.15)",
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "'Fira Code'", "monospace"],
        sans: ["'Inter'", "sans-serif"],
      },
      boxShadow: {
        "glow-cyan":  "0 0 16px rgba(0,242,254,0.35)",
        "glow-amber": "0 0 16px rgba(255,179,0,0.35)",
        "glow-red":   "0 0 16px rgba(255,0,85,0.45)",
      },
    },
  },
  plugins: [],
};