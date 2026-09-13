import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { readJSON, writeJSON } from '@/utils/storage'
import type { SavedItem } from '@/types'

const KEY = 'pcards_favorites'

export const useFavoritesStore = defineStore('favorites', () => {
  const items = ref<SavedItem[]>(readJSON<SavedItem[]>(KEY, []))

  function persist() {
    writeJSON(KEY, items.value)
  }

  const count = computed(() => items.value.length)

  function has(type: string, id: string) {
    return items.value.some((x) => x.type === type && x.id === id)
  }

  function toggle(type: SavedItem['type'], id: string) {
    const idx = items.value.findIndex(
      (x) => x.type === type && x.id === id,
    )
    if (idx >= 0) {
      items.value.splice(idx, 1)
    } else {
      items.value.push({ type, id, addedAt: Date.now() })
    }
    persist()
  }

  function remove(type: string, id: string) {
    items.value = items.value.filter(
      (x) => !(x.type === type && x.id === id),
    )
    persist()
  }

  function clear() {
    items.value = []
    persist()
  }

  return { items, count, has, toggle, remove, clear }
})
