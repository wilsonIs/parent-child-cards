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
      class="flex h-28 items-center justify-center bg-gradient-to-br from-story to-story-soft"
    >
      <img
        v-if="story.cover"
        :src="story.cover"
        :alt="story.title"
        class="h-full w-full object-cover"
      />
      <span v-else class="text-6xl">{{ story.icon }}</span>
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
      class="pointer-events-none absolute bottom-3 right-3 flex h-9 w-9 items-center justify-center rounded-full bg-story text-sm text-white shadow-soft"
      aria-hidden="true"
      >▶</span
    >
  </button>
</template>
