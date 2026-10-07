<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import AppHeader from '@/components/AppHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import LazyImg from '@/components/LazyImg.vue'
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
      <!-- 系列头图：封面图作为整个头图区背景铺满 -->
      <div class="relative flex min-h-[16rem] flex-col overflow-hidden md:min-h-[20rem] lg:min-h-[24rem]">
        <!-- 背景图：充满整个头图区 -->
        <img
          v-if="meta.cover"
          :src="meta.cover"
          :alt="name"
          loading="lazy"
          class="absolute inset-0 h-full w-full object-cover"
        />
        <!-- 无封面时的渐变底 -->
        <div
          v-else
          class="absolute inset-0 bg-gradient-to-br from-story to-story-soft"
        ></div>
        <!-- 暗色渐变遮罩：保证文字在任何封面上都可读 -->
        <div
          class="absolute inset-0 bg-gradient-to-b from-ink/30 via-ink/20 to-ink/75"
        ></div>
        <!-- 内容覆盖在背景图上 -->
        <div
          class="relative flex flex-1 flex-col items-center justify-end gap-3 px-6 pb-8 pt-6 text-center"
        >
          <span v-if="!meta.cover" class="text-7xl drop-shadow-sm md:text-8xl">{{ meta.icon ?? '📚' }}</span>
          <h2 class="text-2xl font-bold text-white drop-shadow-sm md:text-3xl lg:text-4xl">{{ name }}</h2>
          <p class="max-w-xs text-sm text-white/90 drop-shadow-sm md:max-w-sm md:text-base lg:text-lg">{{ meta.desc }}</p>
          <span class="chip bg-white/25 text-white backdrop-blur-sm">共 {{ stories.length }} 个故事</span>
        </div>
      </div>

      <!-- 故事列表 -->
      <div v-if="stories.length" class="grid grid-cols-1 gap-3 p-4 md:grid-cols-2 md:gap-4 md:p-6 lg:grid-cols-3 lg:gap-5 lg:p-8">
        <button
          v-for="(st, i) in stories"
          :key="st.id"
          type="button"
          class="card-soft flex items-center gap-4 p-4 text-left transition-transform active:scale-[0.98]"
          @click="open(st.id)"
        >
          <LazyImg
            v-if="st.cover"
            :src="st.cover"
            :alt="st.title"
            rounded="rounded-2xl"
            class="h-12 w-12 shrink-0"
          />
          <span
            v-else
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-story-soft text-3xl"
          >
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