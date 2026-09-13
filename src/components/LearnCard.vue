<script setup lang="ts">
import { onMounted } from 'vue'
import { useTodayStore } from '@/stores/today'
import { useSettingsStore } from '@/stores/settings'
import type { Learn } from '@/types'

const props = defineProps<{ learn: Learn }>()

const today = useTodayStore()
const settings = useSettingsStore()

onMounted(() => settings.recordView('learn', props.learn.id))

function open() {
  window.open(props.learn.url, '_blank', 'noopener')
}

function toggleToday() {
  if (today.has('learn', props.learn.id))
    today.remove('learn', props.learn.id)
  else today.add('learn', props.learn.id)
}
</script>

<template>
  <article
    class="card-soft fade-up cursor-pointer p-4 active:scale-[0.99]"
    @click="open"
  >
    <div class="flex flex-wrap items-center gap-2">
      <span class="chip bg-learn-soft text-learn-deep">{{ learn.subject }}</span>
      <span class="chip bg-learn-soft text-learn-deep">
        {{ learn.resourceType }}
      </span>
      <span v-if="learn.grade" class="chip chip-off">{{ learn.grade }}</span>
    </div>

    <h3 class="mt-2 text-base font-bold leading-snug text-ink">
      {{ learn.title }}
    </h3>
    <p v-if="learn.source" class="mt-0.5 text-xs text-ink-muted">
      {{ learn.source }}
    </p>
    <p
      v-if="learn.description"
      class="mt-1.5 text-sm leading-relaxed text-ink-soft"
    >
      {{ learn.description }}
    </p>

    <div class="mt-3 flex items-center justify-between gap-2">
      <button
        class="btn h-10 gap-1.5 px-4 text-sm"
        :class="
          today.has('learn', learn.id)
            ? 'bg-ink text-cream'
            : 'bg-cream-200 text-ink-soft'
        "
        @click.stop="toggleToday"
      >
        <span>{{ today.has('learn', learn.id) ? '✓' : '⭐' }}</span>
        <span>{{ today.has('learn', learn.id) ? '已在今日' : '加入今日' }}</span>
      </button>

      <button
        class="btn h-10 gap-1 px-4 text-sm bg-learn-soft text-learn-deep"
        @click.stop="open"
      >
        <span>前往</span>
        <span>↗</span>
      </button>
    </div>
  </article>
</template>
