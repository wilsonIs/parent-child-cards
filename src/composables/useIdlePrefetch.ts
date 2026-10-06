import { onMounted, onBeforeUnmount } from 'vue'
import { useDataStore } from '@/stores/data'
import { useSettingsStore } from '@/stores/settings'

/**
 * 空闲时预缓存音频文件：
 * - 优先缓存用户最近听过的故事
 * - 然后按顺序缓存全库
 * - 使用 requestIdleCallback，浏览器空闲时才执行
 * - 每次只下载一个，不抢带宽
 * - 图片已走 precache，不需要空闲预缓存
 */

const AUDIO_CACHE = 'audio-cache'
const MAX_CACHE = 100

export function useIdlePrefetch() {
  const data = useDataStore()
  const settings = useSettingsStore()
  let prefetching = false
  let cancelled = false
  const BASE = import.meta.env.BASE_URL

  async function cacheAudio(url: string): Promise<boolean> {
    try {
      const cache = await caches.open(AUDIO_CACHE)
      if (await cache.match(url)) return true
      const keys = await cache.keys()
      if (keys.length >= MAX_CACHE) await cache.delete(keys[0])
      const res = await fetch(url)
      if (!res.ok) return false
      await cache.put(url, res.clone())
      return true
    } catch {
      return false
    }
  }

  function prefetchNext(queue: string[], index: number) {
    if (cancelled || index >= queue.length) return

    const run = (deadline: IdleDeadline) => {
      if (cancelled) return
      if (deadline.timeRemaining() > 0 && !prefetching) {
        prefetching = true
        cacheAudio(queue[index]).finally(() => {
          prefetching = false
          if (!cancelled) {
            requestIdleCallback(() => prefetchNext(queue, index + 1), { timeout: 5000 })
          }
        })
      } else {
        requestIdleCallback(() => prefetchNext(queue, index), { timeout: 5000 })
      }
    }

    requestIdleCallback(run, { timeout: 5000 })
  }

  onMounted(() => {
    if (data.stories.length === 0) {
      setTimeout(() => startPrefetch(), 3000)
      return
    }
    startPrefetch()
  })

  function startPrefetch() {
    if (cancelled) return
    const recent = settings.history
      .filter((h) => h.type === 'story')
      .map((h) => data.storyById(h.id))
      .filter((s) => s?.audio)
      .map((s) => s!.audio!) as string[]

    const allAudio = data.stories
      .filter((s) => s.audio)
      .map((s) => s.audio!) as string[]

    const queue = [...new Set([...recent, ...allAudio])].map((a) => `${BASE}${a}`)
    if (queue.length === 0) return

    setTimeout(() => {
      if (!cancelled) prefetchNext(queue, 0)
    }, 5000)
  }

  onBeforeUnmount(() => {
    cancelled = true
  })
}
