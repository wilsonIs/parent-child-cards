import { ref } from 'vue'
import { registerSW } from 'virtual:pwa-register'

/**
 * PWA 更新检测：
 * - 检测到新版本时显示「发现新内容」提示
 * - 用户点击后刷新页面加载新版本
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
