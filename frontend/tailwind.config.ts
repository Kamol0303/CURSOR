import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        naqsh: {
          primary: "var(--color-naqsh-primary)",
          accent: "var(--color-naqsh-accent)",
          terracotta: "var(--color-naqsh-terracotta)",
        },
      },
    },
  },
  plugins: [],
};

export default config;
