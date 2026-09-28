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
          primary: '#020B0B',
          secondary: '#051F20',
          surface: '#0B2B26',
          elevated: '#163832',
        },
        border: {
          subtle: 'rgba(142, 182, 155, 0.18)',
          active: '#8EB69B',
        },
        accent: {
          info: '#8EB69B',
          ai: '#A9D6B5',
        },
        hazard: {
          normal: '#22C55E',
          watch: '#EAB308',
          warning: '#F97316',
          critical: '#EF4444',
          offline: '#64748B',
        },
        text: {
          primary: '#DAF1DE',
          secondary: '#A9D6B5',
          muted: '#6F9981',
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
