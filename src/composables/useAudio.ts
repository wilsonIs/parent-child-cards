import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSettingsStore } from '@/stores/settings'

/**
 * 故事播放控制 composable。
 * 防上瘾：点击播放、ended 仅停止、不自动下一首、不循环；语速可调。
 */
export function useAudio() {
  const audioEl = ref<HTMLAudioElement | null>(null)
  const playing = ref(false)
  const current = ref(0) // 当前秒
  const duration = ref(0)
  const ended = ref(false)

  const settings = useSettingsStore()
  const { settings: prefs } = storeToRefs(settings)

  function bind(el: HTMLAudioElement | null) {
    audioEl.value = el
    if (!el) return
    el.preload = 'none'
    el.loop = false
    el.playbackRate = prefs.value.playbackRate
    el.addEventListener('timeupdate', onTime)
    el.addEventListener('loadedmetadata', onMeta)
    el.addEventListener('ended', onEnded)
    el.addEventListener('play', () => (playing.value = true))
    el.addEventListener('pause', () => (playing.value = false))
  }

  function unbind() {
    const el = audioEl.value
    if (!el) return
    el.removeEventListener('timeupdate', onTime)
    el.removeEventListener('loadedmetadata', onMeta)
    el.removeEventListener('ended', onEnded)
    el.pause()
    audioEl.value = null
    playing.value = false
  }

  function onTime() {
    const el = audioEl.value
    if (!el) return
    current.value = el.currentTime
  }
  function onMeta() {
    const el = audioEl.value
    if (!el) return
    duration.value = isFinite(el.duration) ? el.duration : 0
  }
  function onEnded() {
    // 播完即停，不自动下一首
    playing.value = false
    ended.value = true
    const el = audioEl.value
    if (el) el.currentTime = 0
  }

  function applyRate() {
    if (audioEl.value)
      audioEl.value.playbackRate = prefs.value.playbackRate
  }

  async function play() {
    const el = audioEl.value
    if (!el) return
    ended.value = false
    applyRate()
    try {
      await el.play()
    } catch (e) {
      console.warn('播放失败', e)
    }
  }

  function pause() {
    audioEl.value?.pause()
  }

  function toggle() {
    if (playing.value) pause()
    else play()
  }

  function seek(sec: number) {
    const el = audioEl.value
    if (!el) return
    el.currentTime = sec
    current.value = sec
  }

  function reset() {
    const el = audioEl.value
    if (el) {
      el.pause()
      el.currentTime = 0
    }
    playing.value = false
    ended.value = false
    current.value = 0
  }

  return {
    audioEl,
    playing,
    current,
    duration,
    ended,
    bind,
    unbind,
    play,
    pause,
    toggle,
    seek,
    reset,
    applyRate,
  }
}

/** 格式化秒为 m:ss */
export function fmtTime(sec: number): string {
  if (!isFinite(sec) || sec < 0) sec = 0
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}
