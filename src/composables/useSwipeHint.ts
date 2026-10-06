import { onMounted, ref } from 'vue'

/**
 * 上滑引导：仅首次进入卡片流页时显示，用户首次上滑/点击后永久隐藏
 * @param key localStorage 存储键
 */
export function useSwipeHint(key: string) {
  const STORAGE_KEY = `swipe-hint-${key}`
  const showHint = ref(false)

  function dismiss() {
    showHint.value = false
    try {
      localStorage.setItem(STORAGE_KEY, '1')
    } catch {
      /* ignore */
    }
  }

  onMounted(() => {
    try {
      showHint.value = !localStorage.getItem(STORAGE_KEY)
    } catch {
      showHint.value = true
    }
  })

  return { showHint, dismiss }
}
