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
      includeAssets: [
        'manifest.json',
        'assets/icons/icon-192.jpg',
        'assets/icons/icon-512.jpg',
      ],
      manifest: false,
      workbox: {
        // 预缓存：构建产物（JS/CSS/HTML）+ manifest + 图标
        // Workbox 会为每个文件计算 hash 作为 revision，内容变了 revision 变，SW 自动更新
        globPatterns: ['**/*.{js,css,html,json,svg,woff2,jpg,png,webp,gif}'],
        globIgnores: ['**/assets/audio/**'],
        // 新 SW 立即激活，不等旧 SW 退出
        skipWaiting: true,
        clientsClaim: true,
        cleanupOutdatedCaches: true,
        // 用 hash 路由，不需要 SPA 导航 fallback；静态资源直接命中文件
        navigateFallback: null,
        // 运行时缓存策略：StaleWhileRevalidate = 先用缓存，后台拉新版本
        runtimeCaching: [
          {
            // 图片：先用缓存快速显示，后台静默更新
            urlPattern: /\.(?:jpg|png|webp|gif)$/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'img-cache',
              expiration: { maxEntries: 500, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
          {
            // 音频：先播缓存，后台拉新版本；网络失败时静默降级，不抛 no-response
            urlPattern: /\.(?:mp3|wav|m4a)$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'audio-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
              networkTimeoutSeconds: 10,
            },
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
