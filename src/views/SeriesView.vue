<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import AppHeader from '@/components/AppHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { SERIES_META } from '@/config/modules'

const route = useRoute()
const router = useRouter()
const data = useDataStore()

const name = computed(() => String(route.params.name))
const meta = computed(() => SERIES_META[name.value] ?? {})
const stories = computed(() =>
  data.stories.filter((s) => s.series === name.value),
)

function open(id: string) {
  router.push(`/story/${id}`)
}
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader :title="name" show-back color-class="story" />

    <div class="flex-1 overflow-y-auto">
      <!-- 系列头图 -->
      <div
        class="flex flex-col items-center gap-3 bg-gradient-to-br from-story to-story-soft px-6 py-8 text-center"
      >
        <span class="text-8xl drop-shadow-sm">{{ meta.icon ?? '📚' }}</span>
        <h2 class="text-2xl font-bold text-white drop-shadow-sm">{{ name }}</h2>
        <p class="max-w-xs text-sm text-white/85">{{ meta.desc }}</p>
        <span class="chip bg-white/25 text-white">共 {{ stories.length }} 个故事</span>
      </div>

      <!-- 故事列表 -->
      <div v-if="stories.length" class="flex flex-col gap-3 p-4">
        <button
          v-for="(st, i) in stories"
          :key="st.id"
          type="button"
          class="card-soft flex items-center gap-4 p-4 text-left transition-transform active:scale-[0.98]"
          @click="open(st.id)"
        >
          <span class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-story-soft text-3xl">
            {{ st.icon }}
          </span>
          <div class="min-w-0 flex-1">
            <div class="flex items-baseline gap-2">
              <span class="text-xs font-bold text-story-deep">{{ i + 1 }}</span>
              <h3 class="truncate font-bold text-ink">{{ st.title }}</h3>
            </div>
            <p class="mt-0.5 text-xs text-ink-muted">
              {{ st.age }} · {{ st.duration }}
            </p>
          </div>
          <span class="shrink-0 text-lg text-ink-muted">▸</span>
        </button>
      </div>
      <EmptyState v-else icon="📚" text="该系列暂无故事" />
    </div>
  </div>
</template>
