<script setup lang="ts">
import type { Story } from '@/types'

defineProps<{ story: Story }>()
const emit = defineEmits<{ (e: 'open', id: string): void }>()

function open(id: string) {
  emit('open', id)
}
</script>

<template>
  <button
    type="button"
    class="card-soft fade-up relative flex w-full flex-col overflow-hidden text-left transition-transform duration-150 active:scale-[0.98]"
    @click="open(story.id)"
  >
    <div
      class="relative flex h-28 items-center justify-center overflow-hidden bg-gradient-to-br from-story to-story-deep"
    >
      <img
        v-if="story.cover"
        :src="story.cover"
        :alt="story.title"
        class="h-full w-full object-cover"
      />
      <template v-else>
        <!-- 装饰圆点，让纯色渐变不那么呆 -->
        <span
          class="pointer-events-none absolute -left-4 -top-6 h-20 w-20 rounded-full bg-white/15"
          aria-hidden="true"
        ></span>
        <span
          class="pointer-events-none absolute -bottom-8 -right-3 h-24 w-24 rounded-full bg-white/10"
          aria-hidden="true"
        ></span>
        <span class="text-6xl drop-shadow-md">{{ story.icon }}</span>
      </template>
    </div>
    <div class="flex flex-1 flex-col gap-2 p-3">
      <h3 class="text-base font-bold leading-snug text-ink">{{ story.title }}</h3>
      <div class="flex flex-wrap gap-1">
        <span
          v-for="c in story.category.slice(0, 2)"
          :key="c"
          class="chip chip-off !px-2 !py-0.5 !text-xs"
          >{{ c }}</span
        >
      </div>
      <div class="mt-auto flex items-center gap-2 pr-11 text-xs text-ink-muted">
        <span>{{ story.age }}</span>
        <span>·</span>
        <span>{{ story.duration }}</span>
      </div>
    </div>
    <span
      v-if="story.audio"
      class="pointer-events-none absolute bottom-3 right-3 flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-story to-story-deep text-sm text-white shadow-[0_4px_12px_-2px_rgba(91,79,192,0.5)]"
      aria-hidden="true"
      >▶</span
    >
    <span
      v-else
      class="pointer-events-none absolute bottom-3 right-3 flex h-9 w-9 items-center justify-center rounded-full bg-cream-200 text-sm text-ink-muted"
      aria-hidden="true"
      >📖</span
    >
  </button>
</template>
