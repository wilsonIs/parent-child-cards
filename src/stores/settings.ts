import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { readJSON, removeKey, writeJSON } from '@/utils/storage'
import type { HistoryItem, Settings } from '@/types'

const SETTINGS_KEY = 'pcards_settings'
const HISTORY_KEY = 'pcards_history'
const HISTORY_MAX = 50

const DEFAULT_SETTINGS: Settings = {
  playbackRate: 1,
  fontSize: 'normal',
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<Settings>(
    readJSON<Settings>(SETTINGS_KEY, { ...DEFAULT_SETTINGS }),
  )
  const history = ref<HistoryItem[]>(readJSON<HistoryItem[]>(HISTORY_KEY, []))

  // 应用字体大小到根元素（用户习惯可视化）
  const fontPx = computed(() => (settings.value.fontSize === 'large' ? 18 : 16))

  function applyFontSize() {
    if (typeof document === 'undefined') return
    document.documentElement.style.setProperty(
      '--app-font-size',
      `${fontPx.value}px`,
    )
  }

  function setPlaybackRate(rate: number) {
    settings.value.playbackRate = Number(rate.toFixed(2))
  }

  function setFontSize(size: Settings['fontSize']) {
    settings.value.fontSize = size
    applyFontSize()
  }

  function recordView(type: HistoryItem['type'], id: string) {
    const idx = history.value.findIndex(
      (x) => x.type === type && x.id === id,
    )
    if (idx >= 0) history.value.splice(idx, 1)
    history.value.unshift({ type, id, viewedAt: Date.now() })
    if (history.value.length > HISTORY_MAX)
      history.value = history.value.slice(0, HISTORY_MAX)
  }

  /** 清空所有用户数据（收藏/今日/习惯），设置恢复默认 */
  function clearAllUserData() {
    removeKey(SETTINGS_KEY)
    removeKey(HISTORY_KEY)
    settings.value = { ...DEFAULT_SETTINGS }
    history.value = []
    applyFontSize()
  }

  // 持久化
  watch(
    settings,
    (v) => {
      writeJSON(SETTINGS_KEY, v)
    },
    { deep: true },
  )
  watch(history, (v) => writeJSON(HISTORY_KEY, v), { deep: true })

  return {
    settings,
    history,
    fontPx,
    applyFontSize,
    setPlaybackRate,
    setFontSize,
    recordView,
    clearAllUserData,
  }
})
