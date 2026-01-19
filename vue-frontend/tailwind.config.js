/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'poe-dark': '#1a1a1a',
        'poe-gold': '#af6025',
        'poe-blue': '#4169e1',
      }
    },
  },
  plugins: [],
}
