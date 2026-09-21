/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#07111F',
          secondary: '#0B1726',
          surface: '#102033',
          elevated: '#14273C',
        },
        border: {
          subtle: '#22364A',
          active: '#27C7E8',
        },
        accent: {
          info: '#27C7E8',
          ai: '#8B5CF6',
        },
        hazard: {
          normal: '#22C55E',
          watch: '#EAB308',
          warning: '#F97316',
          critical: '#EF4444',
          offline: '#64748B',
        },
        text: {
          primary: '#F1F5F9',
          secondary: '#9FB0C3',
          muted: '#64748B',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      borderRadius: {
        'sm': '6px',
        DEFAULT: '10px',
        'md': '10px',
        'lg': '14px',
      },
    },
  },
  plugins: [],
}
