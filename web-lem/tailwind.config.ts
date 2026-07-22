import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        lem: {
          obsidian: "#0a0a0a",
          white: "#ffffff",
          silver: "#a1a1aa",
          "silver-muted": "#71717a",
        },
        background: "var(--background)",
        foreground: "var(--foreground)",
        muted: "var(--muted)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        tight: "-0.02em",
        tighter: "-0.04em",
      },
      borderRadius: {
        lem: "0", // Sharp edges
      },
    },
  },
  plugins: [],
};
export default config;
