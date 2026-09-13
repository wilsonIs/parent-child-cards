<script setup lang="ts">
import { useFavoritesStore } from '@/stores/favorites'
import { useTodayStore } from '@/stores/today'
import type { ItemType } from '@/types'

const props = defineProps<{
  type: ItemType
  id: string
}>()

const fav = useFavoritesStore()
const today = useTodayStore()

const isFav = () => fav.has(props.type, props.id)
const isToday = () => today.has(props.type, props.id)
</script>

<template>
  <div class="flex items-center gap-2">
    <button
      class="btn h-11 gap-1.5 px-4 text-base"
      :class="isFav() ? 'bg-coral text-white' : 'bg-cream-200 text-ink-soft'"
      @click.stop="fav.toggle(type, id)"
    >
      <span>{{ isFav() ? '❤️' : '🤍' }}</span>
      <span class="text-sm">{{ isFav() ? '已收藏' : '收藏' }}</span>
    </button>
    <button
      class="btn h-11 gap-1.5 px-4 text-base"
      :class="isToday() ? 'bg-ink text-cream' : 'btn-primary'"
      @click.stop="isToday() ? today.remove(type, id) : today.add(type, id)"
    >
      <span>{{ isToday() ? '✓' : '⭐' }}</span>
      <span class="text-sm">{{ isToday() ? '已在今日' : '加入今日' }}</span>
    </button>
  </div>
</template>
