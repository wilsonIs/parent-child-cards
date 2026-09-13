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
          DEFAULT: '#F5A061',
          soft: '#FBE3D0',
          deep: '#D97A2E',
        },
        learn: {
          DEFAULT: '#5BA88A',
          soft: '#D6EAD9',
          deep: '#3E8164',
        },
        story: {
          DEFAULT: '#7B8FD4',
          soft: '#DDE3F4',
          deep: '#5567B5',
        },
        play: {
          DEFAULT: '#F2C14E',
          soft: '#FAEBC4',
          deep: '#D29A1E',
        },
        coral: {
          DEFAULT: '#E76F51',
          soft: '#F8D8CF',
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
