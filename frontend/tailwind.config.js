/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Design System Colors
        primary: "#004ac6",
        "primary-container": "#2563eb",
        "on-primary-container": "#eeefff",
        "primary-fixed": "#dbe1ff",
        "primary-fixed-dim": "#b4c5ff",
        "on-primary-fixed": "#00174b",
        "on-primary-fixed-variant": "#003ea8",
        
        secondary: "#505f76",
        "secondary-container": "#d0e1fb",
        "on-secondary-container": "#54647a",
        "secondary-fixed": "#d3e4fe",
        "secondary-fixed-dim": "#b7c8e1",
        "on-secondary-fixed": "#0b1c30",
        
        tertiary: "#943700",
        "tertiary-container": "#bc4800",
        "on-tertiary-container": "#ffede6",
        "tertiary-fixed": "#ffdbcd",
        "tertiary-fixed-dim": "#ffb596",
        "on-tertiary-fixed": "#360f00",
        
        background: "#f7f9fb",
        surface: "#f7f9fb",
        "surface-bright": "#f7f9fb",
        "surface-dim": "#d8dadc",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f2f4f6",
        "surface-container": "#eceef0",
        "surface-container-high": "#e6e8ea",
        "surface-container-highest": "#e0e3e5",
        
        "on-surface": "#191c1e",
        "on-surface-variant": "#434655",
        "on-background": "#191c1e",
        
        outline: "#737686",
        "outline-variant": "#c3c6d7",
        
        error: "#ba1a1a",
        "error-container": "#ffdad6",
        "on-error-container": "#93000a",
        "on-error": "#ffffff",
        
        // Legacy vayu colors mapped/kept for compatibility
        vayu: {
          navy: '#0B132B',
          charcoal: '#1C2541',
          blue: '#004ac6',
          amber: '#943700',
          green: '#28A745',
          yellow: '#FFC107',
          orange: '#FD7E14',
          red: '#ba1a1a',
          maroon: '#721C24'
        }
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "2xl": "1rem",
        "full": "9999px"
      },
      spacing: {
        "xs": "4px",
        "sidebar-width": "240px",
        "sm": "8px",
        "base": "4px",
        "md": "16px",
        "lg": "24px",
        "container-max": "1440px",
        "2xl": "48px",
        "xl": "32px"
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      }
    },
  },
  plugins: [],
}
