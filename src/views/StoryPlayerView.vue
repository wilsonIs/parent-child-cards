<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useDataStore } from '@/stores/data'
import { useSettingsStore } from '@/stores/settings'
import { useAudio, fmtTime } from '@/composables/useAudio'
import AppHeader from '@/components/AppHeader.vue'
import ActionButtons from '@/components/ActionButtons.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const data = useDataStore()
const settings = useSettingsStore()
const { settings: prefs } = storeToRefs(settings)

const id = computed(() => String(route.params.id))
const story = computed(() => data.storyById(id.value))

const audioRef = ref<HTMLAudioElement | null>(null)
const { playing, current, duration, ended, bind, unbind, toggle, seek, applyRate } =
  useAudio()

const noAudio = computed(() => !story.value?.audio)
const rates = [0.75, 1, 1.25]

function setRate(r: number) {
  settings.setPlaybackRate(r)
  applyRate()
}

onMounted(() => {
  settings.recordView('story', id.value)
  if (audioRef.value) bind(audioRef.value)
})

onBeforeUnmount(() => {
  unbind()
})
</script>

<template>
  <div v-if="story" class="flex h-full flex-col">
    <AppHeader :title="story.title" showBack colorClass="story" />
    <div class="flex-1 overflow-y-auto">
      <!-- 封面区 -->
      <div
        class="flex flex-col items-center gap-3 bg-gradient-to-br from-story to-story-soft px-6 py-8 text-center"
      >
        <div class="text-8xl">{{ story.icon }}</div>
        <h2 class="text-xl font-bold text-story-deep">{{ story.title }}</h2>
        <div class="flex flex-wrap justify-center gap-1">
          <span v-for="c in story.category" :key="c" class="chip chip-on">{{
            c
          }}</span>
        </div>
        <div class="flex items-center gap-3 text-sm text-ink-soft">
          <span>{{ story.age }}</span>
          <span>·</span>
          <span>{{ story.duration }}</span>
        </div>
      </div>

      <!-- 文本区 -->
      <div class="px-5 py-5">
        <p class="text-base leading-relaxed text-ink">{{ story.text }}</p>
      </div>

      <!-- 播放器 -->
      <div class="mx-4 mb-4 rounded-3xl bg-cream-100 p-4">
        <div
          v-if="noAudio"
          class="mb-3 rounded-2xl bg-cream-200 px-3 py-2 text-center text-sm text-ink-muted"
        >
          该故事暂无音频，可阅读文本
        </div>
        <div class="flex items-center gap-3">
          <button
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-story text-xl text-white shadow-soft transition-transform active:scale-95 disabled:opacity-40"
            :disabled="noAudio"
            @click="toggle"
          >
            <span>{{ playing ? '⏸' : '▶' }}</span>
          </button>
          <div class="flex-1">
            <input
              type="range"
              class="w-full accent-story"
              :min="0"
              :max="duration || 0"
              :step="0.1"
              :value="current"
              :disabled="noAudio"
              @input="seek(Number(($event.target as HTMLInputElement).value))"
            />
            <div class="flex justify-between text-xs text-ink-muted">
              <span>{{ fmtTime(current) }}</span>
              <span>{{ fmtTime(duration) }}</span>
            </div>
          </div>
        </div>

        <!-- 语速 -->
        <div class="mt-3 flex items-center justify-center gap-2">
          <button
            v-for="r in rates"
            :key="r"
            class="chip"
            :class="prefs.playbackRate === r ? 'chip-on' : 'chip-off'"
            @click="setRate(r)"
            >{{ r }}x</button
          >
        </div>

        <p
          v-if="ended"
          class="mt-3 text-center text-sm text-story-deep"
        >
          播完啦，不自动播放下一个
        </p>
      </div>

      <!-- 操作按钮 -->
      <div class="flex justify-center px-4 pb-6">
        <ActionButtons type="story" :id="story.id" />
      </div>
    </div>

    <audio ref="audioRef" :src="story.audio || undefined" />
  </div>
  <div v-else class="flex h-full flex-col">
    <AppHeader title="故事" showBack colorClass="story" />
    <EmptyState icon="📖" text="没有这个故事" />
  </div>
</template>
