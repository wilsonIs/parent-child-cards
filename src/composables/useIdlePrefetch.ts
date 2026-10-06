import { onMounted, onBeforeUnmount } from 'vue'
import { useDataStore } from '@/stores/data'
import { useSettingsStore } from '@/stores/settings'

/**
 * 空闲时预缓存音频文件：
 * - 优先缓存用户最近听过的故事
 * - 然后按顺序缓存全库
 * - 使用 requestIdleCallback，浏览器空闲时才执行
 * - 每次只下载一个，不抢带宽
 * - 用户交互时自动暂停
 */

const AUDIO_CACHE = 'audio-cache'
const MAX_CACHE = 100

export function useIdlePrefetch() {
  const data = useDataStore()
  const settings = useSettingsStore()
  let prefetching = false
  let cancelled = false

  async function cacheAudio(url: string): Promise<boolean> {
    try {
      const cache = await caches.open(AUDIO_CACHE)
      // 已缓存则跳过
      const cached = await cache.match(url)
      if (cached) return true
      // 检查缓存数量，超限则清理最旧的
      const keys = await cache.keys()
      if (keys.length >= MAX_CACHE) {
        // 删除最早缓存的条目
        await cache.delete(keys[0])
      }
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
      // 有空闲时间且未在交互
      if (deadline.timeRemaining() > 0 && !prefetching) {
        prefetching = true
        const url = queue[index]
        cacheAudio(url).finally(() => {
          prefetching = false
          if (!cancelled) {
            // 下载完一个，继续下一个
            requestIdleCallback(() => prefetchNext(queue, index + 1), { timeout: 5000 })
          }
        })
      } else {
        // 没有空闲时间，稍后重试
        requestIdleCallback(() => prefetchNext(queue, index), { timeout: 5000 })
      }
    }

    requestIdleCallback(run, { timeout: 5000 })
  }

  onMounted(() => {
    // 等数据加载完成
    if (data.stories.length === 0) {
      setTimeout(() => startPrefetch(), 3000)
      return
    }
    startPrefetch()
  })

  function startPrefetch() {
    if (cancelled) return
    // 构建预缓存队列：最近听过的优先，然后全库
    const recent = settings.history
      .filter((h) => h.type === 'story')
      .map((h) => data.storyById(h.id))
      .filter((s) => s?.audio)
      .map((s) => s!.audio!) as string[]

    const allAudio = data.stories
      .filter((s) => s.audio)
      .map((s) => s.audio!) as string[]

    // 去重：最近听过的在前
    const queue = [...new Set([...recent, ...allAudio])]
    if (queue.length === 0) return

    // 延迟 5 秒开始，确保不影响首次加载
    setTimeout(() => {
      if (!cancelled) prefetchNext(queue, 0)
    }, 5000)
  }

  onBeforeUnmount(() => {
    cancelled = true
  })
}
