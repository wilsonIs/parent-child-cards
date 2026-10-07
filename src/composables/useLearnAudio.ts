import { ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'

/**
 * 「学什么」卡片朗读控制。
 * 模块级单例音频：所有 LearnCard 共享同一个 <audio>，保证同一时刻只有一条在播，
 * 点另一张卡会自动打断当前这张。点同一张卡则在播放/暂停间切换。
 */
const audioEl =
  typeof Audio !== 'undefined' ? new Audio() : (null as HTMLAudioElement | null)

/** 当前绑定音频的卡片 id */
const activeId = ref<string | null>(null)
const playing = ref(false)
const loading = ref(false)

let wired = false

function wire() {
  if (!audioEl || wired) return
  wired = true
  audioEl.addEventListener('play', () => (playing.value = true))
  audioEl.addEventListener('pause', () => (playing.value = false))
  audioEl.addEventListener('ended', () => {
    playing.value = false
    activeId.value = null
  })
  audioEl.addEventListener('waiting', () => (loading.value = true))
  audioEl.addEventListener('canplay', () => (loading.value = false))
  audioEl.addEventListener('playing', () => (loading.value = false))
  audioEl.addEventListener('error', () => {
    loading.value = false
    playing.value = false
  })
}

export function useLearnAudio() {
  wire()
  const settings = useSettingsStore()

  function play(id: string, src: string) {
    if (!audioEl) return
    // 切到新卡片时重置音源与进度；同一张卡片暂停后继续则保留进度
    if (audioEl.dataset.learnId !== id) {
      audioEl.dataset.learnId = id
      audioEl.src = src
      audioEl.currentTime = 0
    }
    audioEl.playbackRate = settings.settings.playbackRate
    activeId.value = id
    loading.value = true
    audioEl.play().catch(() => (loading.value = false))
  }

  function toggle(id: string, src: string) {
    if (!audioEl) return
    if (activeId.value === id && playing.value) audioEl.pause()
    else play(id, src)
  }

  function stop() {
    if (!audioEl) return
    audioEl.pause()
    audioEl.currentTime = 0
    activeId.value = null
    playing.value = false
    loading.value = false
  }

  return { activeId, playing, loading, toggle, stop }
}