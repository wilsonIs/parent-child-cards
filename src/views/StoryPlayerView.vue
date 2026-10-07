<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useDataStore } from '@/stores/data'
import { useSettingsStore } from '@/stores/settings'
import { useAudio, fmtTime } from '@/composables/useAudio'
import AppHeader from '@/components/AppHeader.vue'
import EmptyState from '@/components/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const data = useDataStore()
const settings = useSettingsStore()
const { settings: prefs } = storeToRefs(settings)

const id = computed(() => String(route.params.id))
const story = computed(() => data.storyById(id.value))

const audioRef = ref<HTMLAudioElement | null>(null)
const { playing, loading, current, duration, ended, bind, unbind, toggle, seek, applyRate, play, reset } =
  useAudio()

const noAudio = computed(() => !story.value?.audio)
const rates = [0.75, 1, 1.25]
const autoAdvancing = ref(false)

/** 绑定音频后自动播放（进入播放页由用户点击触发，具备用户手势） */
function bindAndPlay(el: HTMLAudioElement | null) {
  if (!el) return
  bind(el)
  if (!noAudio.value) play()
}

function setRate(r: number) {
  settings.setPlaybackRate(r)
  applyRate()
}

/** 下一个故事：同系列按顺序播，系列播完或单篇则在全库随机（排除当前） */
function nextStory() {
  const cur = story.value
  if (!cur) return
  const all = data.stories
  let next
  if (cur.series) {
    const list = all.filter((s) => s.series === cur.series)
    const idx = list.findIndex((s) => s.id === cur.id)
    if (idx >= 0 && idx < list.length - 1) next = list[idx + 1]
  }
  if (!next) {
    const others = all.filter((s) => s.id !== cur.id)
    if (others.length)
      next = others[Math.floor(Math.random() * others.length)]
  }
  if (next && next.id !== cur.id) {
    autoAdvancing.value = true
    router.replace({ path: `/story/${next.id}` })
  }
}

// 播完自动听下一个
watch(ended, (v) => {
  if (v && prefs.value.autoPlay) nextStory()
})

// 路由 id 变化（自动连播或手动进入其他故事）：重置播放状态并自动播放
watch(
  () => route.params.id,
  () => {
    settings.recordView('story', id.value)
    reset()
    if (autoAdvancing.value) autoAdvancing.value = false
    nextTick(() => {
      if (!noAudio.value) play()
    })
  },
)

onMounted(() => {
  settings.recordView('story', id.value)
  if (audioRef.value) bindAndPlay(audioRef.value)
})

// 故事数据异步加载、audio 元素渲染后再绑定播放器（首次进入时 onMounted 可能拿不到元素）
watch(audioRef, (el) => {
  if (el) bindAndPlay(el)
})

onBeforeUnmount(() => {
  unbind()
})

// 预加载封面图（进入播放页时立即触发）
watch(story, (s) => {
  if (s?.cover) {
    const img = new Image()
    img.src = s.cover
  }
})
</script>

<template>
  <div v-if="story" class="flex h-full flex-col">
    <AppHeader :title="story.title" showBack colorClass="story" />
    <div class="flex-1 overflow-y-auto">
      <!-- 封面区：封面图作为整张封面区背景铺满 -->
      <div class="relative flex min-h-[16rem] flex-col overflow-hidden md:min-h-[20rem] lg:min-h-[24rem]">
        <!-- 背景图：充满整个封面区 -->
        <img
          v-if="story.cover"
          :src="story.cover"
          :alt="story.title"
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
          <div v-if="!story.cover" class="text-7xl md:text-8xl">{{ story.icon }}</div>
          <h2 class="text-2xl font-bold text-white drop-shadow-md md:text-3xl lg:text-4xl">{{ story.title }}</h2>
          <div class="flex flex-wrap justify-center gap-1">
            <span
              v-for="c in story.category"
              :key="c"
              class="chip bg-white/25 text-white backdrop-blur-sm"
              >{{ c }}</span
            >
          </div>
          <div class="flex items-center gap-3 text-sm text-white/90 drop-shadow-sm md:text-base lg:text-lg">
            <span>{{ story.age }}</span>
            <span>·</span>
            <span>{{ story.duration }}</span>
          </div>
        </div>
      </div>

      <!-- 文本区（平板下居中限宽，避免横屏每行文字过长影响阅读） -->
      <div class="px-5 py-5 md:mx-auto md:max-w-3xl md:px-6 md:py-8 lg:max-w-4xl">
        <p class="text-base leading-relaxed text-ink md:text-lg md:leading-loose">{{ story.text }}</p>
      </div>

    </div>

    <!-- 吸底播放器：长故事滚动时播放控件始终可见 -->
    <div class="shrink-0 border-t border-cream-300/50 bg-cream-100 px-4 py-3">
      <div
        v-if="noAudio"
        class="mb-2 rounded-2xl bg-cream-200 px-3 py-1.5 text-center text-sm text-ink-muted"
      >
        该故事暂无音频，可阅读文本
      </div>
      <div class="flex items-center gap-3">
        <button
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-story text-xl text-white shadow-soft transition-transform active:scale-95 disabled:opacity-40"
          :disabled="noAudio"
          @click="toggle"
        >
          <span v-if="loading" class="inline-block animate-spin">⏳</span>
          <span v-else>{{ playing ? '⏸' : '▶' }}</span>
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

      <div class="mt-2 flex items-center justify-between gap-3">
        <!-- 语速 -->
        <div class="flex items-center gap-1.5">
          <button
            v-for="r in rates"
            :key="r"
            class="chip"
            :class="prefs.playbackRate === r ? 'chip-on' : 'chip-off'"
            @click="setRate(r)"
            >{{ r }}x</button
          >
        </div>
        <!-- 自动连播 -->
        <div class="flex items-center gap-2">
          <span class="text-xs text-ink-soft">自动听下一个</span>
          <button
            class="relative h-6 w-11 rounded-full transition-colors"
            :class="prefs.autoPlay ? 'bg-story' : 'bg-cream-300'"
            role="switch"
            :aria-checked="prefs.autoPlay"
            @click="settings.toggleAutoPlay()"
          >
            <span
              class="absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-soft transition-all"
              :class="prefs.autoPlay ? 'left-[22px]' : 'left-0.5'"
            ></span>
          </button>
        </div>
      </div>

      <p
        v-if="ended"
        class="mt-1.5 text-center text-xs"
        :class="prefs.autoPlay ? 'text-story-deep' : 'text-ink-muted'"
      >
        {{
          prefs.autoPlay
            ? '正在自动切换到下一个故事…'
            : '播完啦，点播放可再听一遍'
        }}
      </p>
    </div>

    <audio ref="audioRef" :src="story.audio || undefined" />
  </div>
  <div v-else class="flex h-full flex-col">
    <AppHeader title="故事" showBack colorClass="story" />
    <EmptyState icon="📖" text="没有这个故事" />
  </div>
</template>
