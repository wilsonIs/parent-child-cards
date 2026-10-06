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
      includeAssets: ['manifest.json', 'assets/icons/icon-192.jpg', 'assets/icons/icon-512.jpg'],
      workbox: {
        // 预缓存：构建产物（JS/CSS/HTML）+ manifest + 图标
        // Workbox 会为每个文件计算 hash 作为 revision，内容变了 revision 变，SW 自动更新
        globPatterns: ['**/*.{js,css,html,json,svg,woff2}'],
        globIgnores: ['**/assets/audio/**'],
        // 新 SW 立即激活，不等旧 SW 退出
        skipWaiting: true,
        clientsClaim: true,
        cleanupOutdatedCaches: true,
        // 运行时缓存策略：StaleWhileRevalidate = 先用缓存，后台拉新版本
        runtimeCaching: [
          {
            // 图片：先用缓存快速显示，后台静默更新
            urlPattern: /\.(?:jpg|png|webp|gif)$/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'img-cache',
              expiration: { maxEntries: 300, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
          {
            // 音频：先播缓存，后台拉新版本
            urlPattern: /\.(?:mp3|wav|m4a)$/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'audio-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
        ],
      },
      manifest: {
        name: '神奇卡盒',
        short_name: '神奇卡盒',
        description: '抽一张卡片，发现吃、学、故事、玩的惊喜，简单、纯粹、不上瘾。',
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
