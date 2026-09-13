import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { readJSON, writeJSON } from '@/utils/storage'
import type { SavedItem } from '@/types'

const KEY = 'pcards_today'

export const useTodayStore = defineStore('today', () => {
  const items = ref<SavedItem[]>(readJSON<SavedItem[]>(KEY, []))

  function persist() {
    writeJSON(KEY, items.value)
  }

  const count = computed(() => items.value.length)

  function has(type: string, id: string) {
    return items.value.some((x) => x.type === type && x.id === id)
  }

  function add(type: SavedItem['type'], id: string) {
    if (has(type, id)) return
    items.value.push({ type, id, addedAt: Date.now() })
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

  return { items, count, has, add, remove, clear }
})
