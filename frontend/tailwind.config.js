/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: { extend: { keyframes: { slide: { '0%': { transform: 'translateX(-100%)' }, '100%': { transform: 'translateX(300%)' } } },
    fontFamily: { sans: ['Geist', 'ui-sans-serif', 'system-ui', 'sans-serif'], mono: ['Geist Mono', 'ui-monospace', 'monospace'] },
    colors: { ink: { 950: '#080c18', 900: '#0b1020', 800: '#111830', 700: '#18213f' }, indigo2: '#818cf8', cyan2: '#22d3ee' }
  } },
  plugins: []
}
