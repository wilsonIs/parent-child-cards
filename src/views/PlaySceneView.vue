<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useDataStore } from '@/stores/data'
import AppHeader from '@/components/AppHeader.vue'
import FilterBar from '@/components/FilterBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import GameCard from '@/components/GameCard.vue'

const route = useRoute()
const data = useDataStore()

const scene = computed(() => decodeURIComponent(String(route.params.scene)))
const filter = ref('全部')
const options = ['全部', '安静', '放电', '动手', '动脑', '多人', '无需材料', '5分钟']

const filtered = computed(() => {
  const s = scene.value
  return data.games
    .filter((g) => g.scenes.includes(s))
    .filter((g) => (filter.value === '全部' ? true : g.types.includes(filter.value)))
})

const feedRef = ref<HTMLElement | null>(null)

function randomPick() {
  const list = filtered.value
  if (list.length === 0) return
  const i = Math.floor(Math.random() * list.length)
  const feed = feedRef.value
  if (!feed) return
  const card = feed.querySelectorAll<HTMLElement>('.snap-card')[i]
  card?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader :title="scene + ' · 玩什么'" show-back color-class="play" />
    <div class="px-4 py-2">
      <button class="btn-primary w-full" @click="randomPick">🎲 随机抽一张</button>
    </div>
    <FilterBar :options="options" v-model="filter" />
    <div ref="feedRef" class="feed flex-1">
      <GameCard v-for="g in filtered" :key="g.id" :game="g" />
      <EmptyState
        v-if="filtered.length === 0"
        icon="🎲"
        text="这个场景还没有游戏"
      />
    </div>
  </div>
</template>
