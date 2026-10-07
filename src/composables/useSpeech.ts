import { ref } from 'vue'

/**
 * 实时朗读（浏览器 Web Speech API，无需预生成 mp3）。
 * 适合短文本（如菜名），进入页面即可即时朗读，不占用存储。
 * 面向儿童：自动选中文（优先女声）、语速略慢。
 */
const supported =
  typeof window !== 'undefined' && 'speechSynthesis' in window

const voices = ref<SpeechSynthesisVoice[]>([])
const ready = ref(false)

function refreshVoices() {
  if (!supported) return
  voices.value = speechSynthesis.getVoices()
  if (voices.value.length) ready.value = true
}

if (supported) {
  refreshVoices()
  // 语音列表是异步加载的，第一次 getVoices() 常为空
  speechSynthesis.onvoiceschanged = refreshVoices
}

function pickVoice(): SpeechSynthesisVoice | undefined {
  const vs = voices.value
  if (!vs.length) return undefined
  return (
    // 优先中文女声（iOS 婷婷 / 安卓小晓 / 桌面 XiaoXiao 等）
    vs.find(
      (v) => v.lang === 'zh-CN' && /xiaoxiao|tingting|huihui|female/i.test(v.name),
    ) ||
    vs.find((v) => v.lang === 'zh-CN') ||
    vs.find((v) => v.lang.startsWith('zh'))
  )
}

// 保留对当前 utterance 的引用，避免 Chrome 下被 GC 导致不发声
let current: SpeechSynthesisUtterance | null = null

export function useSpeech() {
  function speak(text: string, rate = 0.9) {
    if (!supported || !text) return
    speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    const v = pickVoice()
    if (v) u.voice = v
    u.lang = v?.lang || 'zh-CN'
    u.rate = rate
    u.pitch = 1
    u.onend = () => {
      if (current === u) current = null
    }
    current = u
    speechSynthesis.speak(u)
  }

  function stop() {
    if (!supported) return
    speechSynthesis.cancel()
    current = null
  }

  return { speak, stop, supported, ready, voices }
}