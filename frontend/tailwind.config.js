module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
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
        },
        accent: {
          purple: '#8b5cf6',
          pink: '#ec4899',
          green: '#10b981',
          yellow: '#f59e0b',
          orange: '#f97316',
        }
      },
      gradientColorStops: {
        'blue-start': '#60a5fa',
        'blue-mid': '#3b82f6',
        'blue-end': '#2563eb',
        'purple-start': '#8b5cf6',
        'purple-mid': '#7c3aed',
        'purple-end': '#6d28d9',
      },
      backgroundImage: {
        'gradient-blue': 'linear-gradient(to right, var(--tw-gradient-stops))',
        'gradient-purple': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'gradient-sunset': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)',
        'gradient-ocean': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      },
      backgroundSize: {
        '300%': '300%',
      },
      animation: {
        'gradient': 'gradient 3s ease infinite',
        'float': 'float 3s ease-in-out infinite',
        'bounce-in': 'bounce-in 0.6s ease-out',
        'slide-in-up': 'slide-in-up 0.5s ease-out',
        'slide-in-right': 'slide-in-right 0.5s ease-out',
        'fade-in-scale': 'fade-in-scale 0.4s ease-out',
        'shimmer': 'shimmer 2s infinite',
        'pulse-ring': 'pulse-ring 1.25s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite',
        'pulse-dot': 'pulse-dot 1.25s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite',
      },
      keyframes: {
        gradient: {
          '0%': { 'background-position': '0% 50%' },
          '50%': { 'background-position': '100% 50%' },
          '100%': { 'background-position': '0% 50%' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'bounce-in': {
          '0%': { transform: 'scale(0.3) rotate(-10deg)', opacity: '0' },
          '50%': { transform: 'scale(1.05) rotate(5deg)' },
          '70%': { transform: 'scale(0.9) rotate(-2deg)' },
          '100%': { transform: 'scale(1) rotate(0deg)', opacity: '1' },
        },
        'slide-in-up': {
          '0%': { transform: 'translateY(100px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(100px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'fade-in-scale': {
          '0%': { transform: 'scale(0.8)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        shimmer: {
          '0%': { left: '-100%' },
          '100%': { left: '100%' },
        },
        'pulse-ring': {
          '0%': { transform: 'scale(0.33)' },
          '80%, 100%': { opacity: '0' },
        },
        'pulse-dot': {
          '0%': { transform: 'scale(0.8)' },
          '50%': { transform: 'scale(1)' },
          '100%': { transform: 'scale(0.8)' },
        },
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
    },
  },
  plugins: [],
}