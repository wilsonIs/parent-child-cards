<script setup lang="ts">
import { computed, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import FilterBar from '@/components/FilterBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import PoemCard from '@/components/PoemCard.vue'
import { useDataStore } from '@/stores/data'

const data = useDataStore()

const category = ref('全部')
const CATEGORIES = ['全部', '唐诗', '蒙学']

const filtered = computed(() =>
  category.value === '全部'
    ? data.poems
    : data.poems.filter((p) => p.category === category.value),
)
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="学 · 古诗蒙学" color-class="learn" />

    <div class="bg-learn-soft/60">
      <FilterBar v-model="category" :options="CATEGORIES" />
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="filtered.length" class="flex flex-col gap-3 p-4">
        <p class="text-xs text-ink-muted">
          共 {{ filtered.length }} 篇 · 由 chinese-poetry 开源数据集自动同步（MIT 许可 · 古籍公版）
        </p>
        <PoemCard v-for="p in filtered" :key="p.id" :poem="p" />
      </div>
      <EmptyState
        v-else
        icon="🪶"
        text="没有符合条件的诗文"
        hint="换个分类试试"
      />
    </div>
  </div>
</template>
