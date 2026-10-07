<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useSharedAudio } from '@/composables/useSharedAudio'
import type { Learn } from '@/types'

const props = defineProps<{ learn: Learn }>()

const settings = useSettingsStore()
const expand = ref(false)

const { activeId, playing, loading, toggle } = useSharedAudio()

const isActive = computed(() => activeId.value === props.learn.id)
const isPlaying = computed(() => isActive.value && playing.value)
const isLoading = computed(() => isActive.value && loading.value)

onMounted(() => settings.recordView('learn', props.learn.id))

function toggleExpand() {
  expand.value = !expand.value
  if (expand.value) settings.recordView('learn', props.learn.id)
}

function onPlay() {
  if (props.learn.audio) toggle(props.learn.id, props.learn.audio)
}
</script>

<template>
  <article class="card-soft fade-up overflow-hidden p-0" @click="toggleExpand">
    <!-- 封面图（有图时显示） -->
    <div
      v-if="learn.image"
      class="flex aspect-[16/9] items-center justify-center overflow-hidden"
    >
      <img
        :src="learn.image"
        :alt="learn.title"
        loading="lazy"
        class="h-full w-full object-cover"
      />
    </div>

    <div class="p-4">
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

      <!-- 朗读（标题+内容） -->
      <button
        v-if="learn.audio"
        type="button"
        class="mt-3 flex w-full items-center justify-center gap-2 rounded-full bg-learn py-2.5 text-sm font-bold text-white shadow-soft transition-transform active:scale-95"
        @click.stop="onPlay"
      >
        <span v-if="isLoading" class="animate-spin">⏳</span>
        <template v-else>
          <span>{{ isPlaying ? '⏸' : '▶' }}</span>
          <span>{{ isPlaying ? '暂停' : '听一听' }}</span>
        </template>
      </button>
      <div v-else class="mt-3 flex items-center gap-2">
        <span class="text-xs text-ink-muted">📖 本地知识 · 可直接阅读</span>
      </div>
    </div>
  </article>
</template>