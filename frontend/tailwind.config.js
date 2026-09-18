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
        background: '#090a0f',
        surface: '#0f111a',
        'surface-raised': '#161926',
        'surface-border': '#222738',
        'surface-hover': '#1c2030',
        accent: {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          light: '#818cf8',
          glow: 'rgba(99, 102, 241, 0.15)',
        },
        cyan: {
          glow: 'rgba(6, 182, 212, 0.15)',
        },
        emerald: {
          glow: 'rgba(16, 185, 129, 0.15)',
        },
        amber: {
          glow: 'rgba(245, 158, 11, 0.15)',
        },
        rose: {
          glow: 'rgba(244, 63, 94, 0.15)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        display: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'glow-accent': '0 0 25px -5px rgba(99, 102, 241, 0.25)',
        'glow-cyan': '0 0 25px -5px rgba(6, 182, 212, 0.25)',
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.4)',
        'elevated': '0 10px 30px -5px rgba(0, 0, 0, 0.6)',
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scanline': 'scanline 8s linear infinite',
      },
      keyframes: {
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(1000%)' },
        }
      }
    },
  },
  plugins: [],
}
