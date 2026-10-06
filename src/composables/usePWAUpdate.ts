import { ref } from 'vue'
import { registerSW } from 'virtual:pwa-register'

/**
 * PWA 更新检测：
 * - 检测到新版本时显示「发现新内容」提示
 * - 用户点击后刷新页面加载新版本
 * - 每 10 分钟自动检查一次更新
 */
export function usePWAUpdate() {
  const needRefresh = ref(false)
  const offlineReady = ref(false)

  const updateSW = registerSW({
    onNeedRefresh() {
      // SW 检测到新版本
      needRefresh.value = true
    },
    onOfflineReady() {
      // 首次缓存完成，可以离线使用
      offlineReady.value = true
      // 3 秒后自动隐藏
      setTimeout(() => (offlineReady.value = false), 3000)
    },
    onRegistered(registration) {
      // 每 10 分钟检查一次 SW 更新
      if (registration) {
        setInterval(async () => {
          try {
            await registration.update()
          } catch {
            // 离线或网络错误，静默忽略
          }
        }, 10 * 60 * 1000)
      }
    },
  })

  function update() {
    updateSW(true)
    needRefresh.value = false
  }

  function close() {
    needRefresh.value = false
  }

  return { needRefresh, offlineReady, update, close }
}
