<script setup lang="ts">
import { computed } from 'vue'
import { useSharedAudio } from '@/composables/useSharedAudio'
import type { Poem } from '@/types'

const props = defineProps<{ poem: Poem }>()

const { activeId, playing, loading, toggle } = useSharedAudio()

const isActive = computed(() => activeId.value === props.poem.id)
const isPlaying = computed(() => isActive.value && playing.value)
const isLoading = computed(() => isActive.value && loading.value)

function onPlay() {
  if (props.poem.audio) toggle(props.poem.id, props.poem.audio)
}
</script>

<template>
  <article
    class="card-soft fade-up flex flex-col gap-3 p-4"
    :class="poem.category === '蒙学' ? 'bg-gradient-to-br from-learn-soft/60 to-cream-100' : ''"
  >
    <div class="flex flex-wrap items-center gap-2">
      <span
        class="chip"
        :class="
          poem.category === '蒙学'
            ? 'bg-learn-soft text-learn-deep'
            : poem.category === '宋词'
              ? 'bg-play-soft text-play-deep'
              : 'bg-coral-soft text-coral-deep'
        "
      >
        {{
          poem.category === '蒙学'
            ? '📜 蒙学'
            : poem.category === '诗经'
              ? '🌾 诗经'
              : poem.category === '宋词'
                ? '🎼 宋词'
                : poem.category === '楚辞'
                  ? '🍃 楚辞'
                  : '🪶 唐诗'
        }}
      </span>
      <span v-if="poem.grade" class="chip chip-off">{{ poem.grade }}</span>
      <span v-if="poem.author" class="chip chip-off">{{ poem.author }}</span>
    </div>

    <h3 class="text-lg font-bold leading-snug text-ink">{{ poem.title }}</h3>

    <div class="space-y-1 text-base leading-relaxed text-ink-soft">
      <p
        v-for="(line, i) in poem.paragraphs"
        :key="i"
        :class="poem.category === '蒙学' ? '' : 'text-center'"
      >
        {{ line }}
      </p>
    </div>

    <!-- 朗读（诗名 + 朝代 + 诗人 + 正文） -->
    <button
      v-if="poem.audio"
      type="button"
      class="flex w-full items-center justify-center gap-2 rounded-full bg-learn py-2.5 text-sm font-bold text-white shadow-soft transition-transform active:scale-95"
      @click="onPlay"
    >
      <span v-if="isLoading" class="animate-spin">⏳</span>
      <template v-else>
        <span>{{ isPlaying ? '⏸' : '▶' }}</span>
        <span>{{ isPlaying ? '暂停' : '朗读' }}</span>
      </template>
    </button>

    <div class="mt-1 flex items-center gap-2 border-t border-cream-200 pt-3">
      <span class="text-xs text-ink-muted">
        {{ poem.source }} · {{ poem.license }}
      </span>
    </div>
  </article>
</template>