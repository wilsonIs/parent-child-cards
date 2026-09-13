<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useTodayStore } from '@/stores/today'
import { useSettingsStore } from '@/stores/settings'
import type { Learn } from '@/types'

const props = defineProps<{ learn: Learn }>()

const today = useTodayStore()
const settings = useSettingsStore()
const expand = ref(false)

onMounted(() => settings.recordView('learn', props.learn.id))

function toggleExpand() {
  expand.value = !expand.value
  if (expand.value) settings.recordView('learn', props.learn.id)
}

function toggleToday() {
  if (today.has('learn', props.learn.id))
    today.remove('learn', props.learn.id)
  else today.add('learn', props.learn.id)
}
</script>

<template>
  <article class="card-soft fade-up p-4" @click="toggleExpand">
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

    <!-- 本地知识全文（默认 3 行，点击展开） -->
    <p
      class="mt-2 text-sm leading-relaxed text-ink-soft"
      :class="expand ? '' : 'line-clamp-3'"
    >
      {{ learn.content }}
    </p>
    <span class="mt-1 inline-block text-xs text-learn-deep">
      {{ expand ? '收起 ▲' : '展开阅读 ▼' }}
    </span>

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

      <span class="text-xs text-ink-muted">📖 本地知识 · 可直接阅读</span>
    </div>
  </article>
</template>
