import type {Config} from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: '#F7F7F5',
        ink: '#16231D',
        primary: '#1B4D3E',
        accent: '#C8932A',
        terracotta: '#A6552E'
      },
      boxShadow: {
        card: '0 18px 48px rgba(15, 30, 24, 0.12)'
      }
    }
  },
  plugins: []
};

export default config;
