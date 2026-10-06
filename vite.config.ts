import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['manifest.json', 'assets/icons/favicon.jpg'],
      workbox: {
        // 预缓存：构建产物（JS/CSS/HTML）+ manifest
        globPatterns: ['**/*.{js,css,html,json,svg,woff2}'],
        globIgnores: ['**/assets/audio/**', '**/assets/covers/**'],
        // 图片运行时缓存（CacheFirst：优先用缓存）
        runtimeCaching: [
          {
            urlPattern: /\.(?:jpg|png|webp|gif)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'img-cache',
              expiration: { maxEntries: 300, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
          {
            urlPattern: /\.(?:mp3|wav|m4a)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'audio-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
          // 其他静态资源
          {
            urlPattern: /^https?.*\/assets\//,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'static-cache',
              expiration: { maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 * 7 },
            },
          },
        ],
      },
      manifest: {
        name: '亲子卡片箱',
        short_name: '卡片箱',
        description: '把吃、学、故事、玩做成卡片，简单、纯粹、不上瘾的亲子生活工具。',
        theme_color: '#FBF7F0',
        background_color: '#FBF7F0',
        display: 'standalone',
        start_url: './',
        icons: [
          {
            src: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🎎</text></svg>',
            sizes: 'any',
            type: 'image/svg+xml',
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,
  },
})
