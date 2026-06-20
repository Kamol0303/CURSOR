import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        naqsh: {
          primary: 'var(--color-naqsh-primary)',
          accent: 'var(--color-naqsh-accent)',
          terracotta: 'var(--color-naqsh-terracotta)',
          line: 'var(--color-naqsh-line)',
        },
      },
    },
  },
  plugins: [],
};

export default config;
