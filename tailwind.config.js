/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,ts,js}'],
  theme: {
    extend: {
      colors: {
        // 暖米白底 + 柔和模块色（亲子友好、防上瘾）
        cream: {
          DEFAULT: '#FBF7F0',
          50: '#FEFCF8',
          100: '#FBF7F0',
          200: '#F3EBDD',
        },
        ink: {
          DEFAULT: '#3D342B',
          soft: '#5C5046',
          muted: '#8A7F73',
        },
        eat: {
          DEFAULT: '#F08A4B',
          soft: '#FFE6CF',
          light: '#FFF1E3',
          deep: '#C4601F',
        },
        learn: {
          DEFAULT: '#4FAE87',
          soft: '#D9F0E4',
          light: '#EDF8F1',
          deep: '#357A5D',
        },
        story: {
          DEFAULT: '#8A7FE0',
          soft: '#E6E1FA',
          light: '#F1EEFC',
          deep: '#5B4FC0',
        },
        play: {
          DEFAULT: '#F5BF4A',
          soft: '#FCEFCE',
          light: '#FDF6E3',
          deep: '#C98F12',
        },
        coral: {
          DEFAULT: '#E76F51',
          soft: '#FADDD2',
          light: '#FDEDE8',
        },
      },
      fontFamily: {
        sans: [
          '"PingFang SC"',
          '"Noto Sans SC"',
          '"Source Han Sans SC"',
          '"Microsoft YaHei"',
          'system-ui',
          'sans-serif',
        ],
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        soft: '0 8px 24px -8px rgba(61, 52, 43, 0.12)',
        card: '0 12px 32px -12px rgba(61, 52, 43, 0.18)',
      },
      maxWidth: {
        phone: '480px',
      },
      transitionDuration: {
        '150': '150ms',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-up': 'fade-up 200ms ease-out both',
      },
    },
  },
  plugins: [],
}
