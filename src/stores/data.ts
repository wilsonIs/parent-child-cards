import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Dish, Game, Learn, Poem, Story } from '@/types'

/**
 * 数据 store：应用启动时 fetch 四个静态 JSON，缓存到内存。
 * JSON 放在 src/data 下，构建时打包进站点（import 直接引入，无需 fetch 跨域问题）。
 */
export const useDataStore = defineStore('data', () => {
  const dishes = ref<Dish[]>([])
  const stories = ref<Story[]>([])
  const games = ref<Game[]>([])
  const learn = ref<Learn[]>([])
  const poems = ref<Poem[]>([])

  const loaded = ref(false)
  const loading = ref(false)

  async function loadAll() {
    if (loaded.value || loading.value) return
    loading.value = true
    try {
      // 直接 import 静态 JSON，Vite 会打包进产物，避免 file:// 与 CORS 问题
      const [d, s, g, l, p] = await Promise.all([
        import('@/data/dishes.json'),
        import('@/data/stories.json'),
        import('@/data/games.json'),
        import('@/data/learn.json'),
        import('@/data/poems.json'),
      ])
      dishes.value = d.default as Dish[]
      stories.value = s.default as Story[]
      games.value = g.default as Game[]
      learn.value = l.default as Learn[]
      poems.value = p.default as Poem[]
      loaded.value = true
    } catch (e) {
      console.error('数据加载失败', e)
    } finally {
      loading.value = false
    }
  }

  const dishById = (id: string) => dishes.value.find((x) => x.id === id)
  const storyById = (id: string) => stories.value.find((x) => x.id === id)
  const gameById = (id: string) => games.value.find((x) => x.id === id)
  const learnById = (id: string) => learn.value.find((x) => x.id === id)
  const poemById = (id: string) => poems.value.find((x) => x.id === id)

  /** 按 type 取对应集合（供收藏/今日清单回填展示） */
  const itemByType = (type: string, id: string) => {
    switch (type) {
      case 'dish':
        return dishById(id)
      case 'story':
        return storyById(id)
      case 'game':
        return gameById(id)
      case 'learn':
        return learnById(id)
      case 'poem':
        return poemById(id)
      default:
        return undefined
    }
  }

  return {
    dishes,
    stories,
    games,
    learn,
    poems,
    loaded,
    loading,
    loadAll,
    dishById,
    storyById,
    gameById,
    learnById,
    poemById,
    itemByType,
  }
})
