module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#60a5fa', // light blue
          DEFAULT: '#3b82f6', // blue
          dark: '#2563eb', // dark blue
          darker: '#1d4ed8', // darker blue
        },
        secondary: {
          light: '#93c5fd', // lighter blue
          DEFAULT: '#60a5fa', // light blue
          dark: '#3b82f6', // blue
        },
        background: {
          light: '#f0f9ff', // lightest blue background
          DEFAULT: '#e0f2fe', // very light blue background
          dark: '#bae6fd', // light blue background
        }
      },
      gradientColorStops: {
        'blue-start': '#60a5fa',
        'blue-mid': '#3b82f6',
        'blue-end': '#2563eb',
      },
      backgroundImage: {
        'gradient-blue': 'linear-gradient(to right, var(--tw-gradient-stops))',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        bounce: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
      animation: {
        fadeIn: 'fadeIn 0.5s ease-in-out',
        slideInRight: 'slideInRight 0.5s ease-in-out',
        slideInUp: 'slideInUp 0.5s ease-in-out',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        bounce: 'bounce 1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}