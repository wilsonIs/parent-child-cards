<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useDataStore } from '@/stores/data'
import { STORY_CATEGORIES } from '@/config/modules'
import AppHeader from '@/components/AppHeader.vue'
import FilterBar from '@/components/FilterBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import StoryCard from '@/components/StoryCard.vue'

const router = useRouter()
const data = useDataStore()
const { stories } = storeToRefs(data)

const category = ref('全部')

const filtered = computed(() =>
  category.value === '全部'
    ? stories.value
    : stories.value.filter((s) => s.category.includes(category.value)),
)

function open(id: string) {
  router.push(`/story/${id}`)
}

onMounted(() => {
  if (!data.loaded) data.loadAll()
})
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="故事 · 今天听什么" show-back color-class="story" />
    <FilterBar :options="STORY_CATEGORIES" v-model="category" />
    <div class="flex-1 overflow-y-auto">
      <div v-if="filtered.length" class="grid grid-cols-2 gap-3 p-4">
        <StoryCard
          v-for="s in filtered"
          :key="s.id"
          :story="s"
          @open="open"
        />
      </div>
      <EmptyState v-else icon="📖" text="没有这个故事分类" />
    </div>
  </div>
</template>
