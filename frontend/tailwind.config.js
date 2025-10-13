/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f0f9f0',
          100: '#dcf2dc',
          200: '#bce5bc',
          300: '#8dd18d',
          400: '#5bb55b',
          500: '#2d5a2d',
          600: '#1a4a1a',
          700: '#0f3a0f',
          800: '#0a2a0a',
          900: '#051a05',
        },
        kiro: {
          50: '#f4e4bc',
          100: '#f0d9a8',
          200: '#ebc994',
          300: '#e6b980',
          400: '#e1a96c',
          500: '#dc9958',
          600: '#c8894e',
          700: '#b47944',
          800: '#a0693a',
          900: '#8c5930',
        },
        coral: {
          50: '#fff5f5',
          100: '#fed7d7',
          200: '#feb2b2',
          300: '#fc8181',
          400: '#f56565',
          500: '#e53e3e',
          600: '#c53030',
          700: '#9b2c2c',
          800: '#742a2a',
          900: '#4a1414',
        }
      },
      fontFamily: {
        'fredoka': ['Fredoka One', 'cursive'],
        'nunito': ['Nunito', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'twinkle': 'twinkle 3s ease-in-out infinite',
        'bounce-gentle': 'bounce-gentle 2s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        twinkle: {
          '0%, 100%': { opacity: '0.3', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.2)' },
        },
        'bounce-gentle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(244, 228, 188, 0.5)' },
          '100%': { boxShadow: '0 0 40px rgba(244, 228, 188, 0.8)' },
        }
      }
    },
  },
  plugins: [],
}