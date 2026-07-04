/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        vayu: {
          navy: '#0B132B',
          charcoal: '#1C2541',
          blue: '#2E75B6',
          amber: '#B8651A',
          green: '#28A745',
          yellow: '#FFC107',
          orange: '#FD7E14',
          red: '#DC3545',
          maroon: '#721C24'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
