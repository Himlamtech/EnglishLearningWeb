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
    },
  },
  plugins: [],
} 