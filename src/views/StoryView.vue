<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import AppHeader from '@/components/AppHeader.vue'
import { SERIES_META } from '@/config/modules'
import type { Story } from '@/types'

const router = useRouter()
const data = useDataStore()

/** 卡片：系列卡 或 单篇卡 */
type Card =
  | { kind: 'series'; key: string; icon: string; title: string; desc: string; count: number }
  | { kind: 'story'; story: Story }

const category = ref('全部')
const CATEGORIES = ['全部', '系列', '成语', '寓言', '神话', '童话', '民间', '名著', '历史', '睡前', '科普', '英语']

const allCards = computed<Card[]>(() => {
  const cards: Card[] = []
  const bySeries = new Map<string, Story[]>()
  const singles: Story[] = []
  for (const st of data.stories) {
    if (st.series) {
      const list = bySeries.get(st.series) ?? []
      list.push(st)
      bySeries.set(st.series, list)
    } else {
      singles.push(st)
    }
  }
  // 系列卡
  for (const [key, list] of bySeries) {
    const meta = SERIES_META[key]
    cards.push({
      kind: 'series',
      key,
      icon: meta?.icon ?? '📚',
      title: key,
      desc: meta?.desc ?? `${list.length} 个故事`,
      count: list.length,
    })
  }
  // 单篇卡
  for (const st of singles) cards.push({ kind: 'story', story: st })
  return cards
})

/** 按分类过滤后的卡片池 */
const pool = computed(() => {
  const cat = category.value
  if (cat === '全部') return allCards.value
  if (cat === '系列') return allCards.value.filter((c) => c.kind === 'series')
  return allCards.value.filter((c) => c.kind === 'story' && c.story.category.includes(cat))
})

/** 随机打乱后的播放顺序 */
const deck = ref<Card[]>([])

function shuffle() {
  const arr = [...pool.value]
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  deck.value = arr
  idx.value = 0
  offsetY.value = 0
}

const idx = ref(0)
const offsetY = ref(0)
const dragging = ref(false)
const cooldown = ref(0)

function cardStyle(i: number) {
  const dy = (i - idx.value) * 100
  const drag = i === idx.value ? offsetY.value : 0
  return { transform: `translateY(${dy + drag}%)` }
}

function go(delta: number) {
  const next = Math.min(Math.max(idx.value + delta, 0), deck.value.length - 1)
  idx.value = next
}

function openCard(card: Card) {
  if (card.kind === 'series') {
    router.push(`/series/${encodeURIComponent(card.key)}`)
  } else {
    router.push(`/story/${card.story.id}`)
  }
}

// ---- 触摸手势 ----
let startY = 0
let startOffset = 0

function onTouchStart(e: TouchEvent) {
  dragging.value = true
  startY = e.touches[0].clientY
  startOffset = offsetY.value
}
function onTouchMove(e: TouchEvent) {
  if (!dragging.value) return
  const dy = e.touches[0].clientY - startY
  const max = 45
  const damped = Math.max(-max, Math.min(max, dy * 0.5))
  offsetY.value = startOffset + damped
}
function onTouchEnd() {
  if (!dragging.value) return
  dragging.value = false
  if (offsetY.value < -35) go(1)
  else if (offsetY.value > 35) go(-1)
  offsetY.value = 0
}

// ---- 滚轮 ----
function onWheel(e: WheelEvent) {
  const now = Date.now()
  if (now - cooldown.value < 350) return
  cooldown.value = now
  if (e.deltaY > 20) go(1)
  else if (e.deltaY < -20) go(-1)
}

// 数据异步加载完成后初始化播放顺序；分类切换/换一批也会重新洗牌
watch(pool, shuffle, { immediate: true })
const brief = (text: string) => (text.length > 70 ? text.slice(0, 70) + '……' : text)
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="故事 · 上滑换下一个" show-back color-class="story" />

    <!-- 分类 chips（横向滚动） -->
    <div class="scrollbar-none flex gap-2 overflow-x-auto px-4 py-2">
      <button
        v-for="c in CATEGORIES"
        :key="c"
        class="chip shrink-0"
        :class="category === c ? 'chip-on' : 'chip-off'"
        @click="category = c"
      >
        {{ c }}
      </button>
    </div>

    <!-- 上滑卡片流 -->
    <div
      class="relative flex-1 overflow-hidden px-3 pb-3"
      @touchstart.passive="onTouchStart"
      @touchmove.passive="onTouchMove"
      @touchend="onTouchEnd"
      @wheel="onWheel"
    >
      <div
        v-for="(card, i) in deck"
        :key="card.kind === 'series' ? 's:' + card.key : 't:' + card.story.id"
        class="absolute inset-0 transition-transform duration-300"
        :class="dragging ? '!transition-none' : ''"
        :style="cardStyle(i)"
      >
        <!-- 系列卡 -->
        <button
          v-if="card.kind === 'series'"
          type="button"
          class="card-soft fade-up flex h-full w-full flex-col items-center justify-center gap-4 bg-gradient-to-br from-story to-story-soft p-6 text-center"
          @click="openCard(card)"
        >
          <span class="text-8xl drop-shadow-sm">{{ card.icon }}</span>
          <h2 class="text-3xl font-bold text-white drop-shadow-sm">{{ card.title }}</h2>
          <p class="max-w-xs text-sm text-white/85">{{ card.desc }}</p>
          <span class="chip bg-white/25 text-white">共 {{ card.count }} 个故事</span>
          <span
            class="mt-2 flex items-center gap-2 rounded-full bg-white px-6 py-3 font-bold text-story-deep shadow-soft"
          >
            进入系列 ▸
          </span>
        </button>

        <!-- 单篇卡 -->
        <button
          v-else
          type="button"
          class="card-soft fade-up flex h-full w-full flex-col items-center justify-center gap-4 bg-gradient-to-br from-cream-100 to-cream-200 p-6 text-center"
          @click="openCard(card)"
        >
          <span class="text-8xl drop-shadow-sm">{{ card.story.icon }}</span>
          <h2 class="text-3xl font-bold text-ink">{{ card.story.title }}</h2>
          <div class="flex flex-wrap justify-center gap-1">
            <span v-for="c in card.story.category" :key="c" class="chip chip-on">{{
              c
            }}</span>
          </div>
          <p class="max-w-sm text-sm leading-relaxed text-ink-soft">
            {{ brief(card.story.text) }}
          </p>
          <div class="flex items-center gap-3 text-sm text-ink-muted">
            <span>{{ card.story.age }}</span>
            <span>·</span>
            <span>{{ card.story.duration }}</span>
          </div>
          <span
            class="mt-1 flex items-center gap-2 rounded-full bg-story px-6 py-3 font-bold text-white shadow-soft"
          >
            {{ card.story.audio ? '▶ 开始听' : '📖 开始读' }}
          </span>
        </button>
      </div>

      <!-- 空态 -->
      <div
        v-if="deck.length === 0"
        class="flex h-full items-center justify-center text-ink-muted"
      >
        该分类下暂无故事
      </div>
    </div>

    <!-- 底部控制条 -->
    <div
      v-if="deck.length > 0"
      class="flex items-center justify-between gap-3 px-4 pb-4 pt-1"
    >
      <button
        class="flex h-11 w-11 items-center justify-center rounded-full bg-cream-100 text-lg text-ink shadow-soft active:scale-95"
        aria-label="上一个"
        :disabled="idx === 0"
        @click="go(-1)"
      >
        ↑
      </button>
      <div class="text-center text-xs text-ink-muted">
        {{ idx + 1 }} / {{ deck.length }}
        <span v-if="category !== '全部'"> · {{ category }}</span>
      </div>
      <button
        class="flex h-11 w-11 items-center justify-center rounded-full bg-cream-100 text-lg text-ink shadow-soft active:scale-95"
        aria-label="下一个"
        :disabled="idx === deck.length - 1"
        @click="go(1)"
      >
        ↓
      </button>
      <button
        class="flex h-11 items-center justify-center gap-1 rounded-full bg-coral px-5 text-sm font-bold text-white shadow-soft active:scale-95"
        @click="shuffle"
      >
        🎲 换一批
      </button>
    </div>
  </div>
</template>
