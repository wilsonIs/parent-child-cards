<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import FilterBar from '@/components/FilterBar.vue'
import DishCard from '@/components/DishCard.vue'
import { useDataStore } from '@/stores/data'
import { DISH_MEALS, DISH_TYPES } from '@/config/modules'
import type { Dish } from '@/types'

const data = useDataStore()
const meal = ref('全部')
const dishType = ref('全部')

/** 过滤后的卡片池 */
const pool = computed(() =>
  data.dishes.filter((d) => {
    const okMeal = meal.value === '全部' || d.meal.includes(meal.value)
    const okType = dishType.value === '全部' || d.tags.includes(dishType.value)
    return okMeal && okType
  }),
)

/** 随机打乱后的播放顺序 */
const deck = ref<Dish[]>([])
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

// ---- 触摸手势（touch-action:none 交给 JS，避免 Safari 橡皮筋）----
let startY = 0
let startOffset = 0

function onTouchStart(e: TouchEvent) {
  dragging.value = true
  startY = e.touches[0].clientY
  startOffset = offsetY.value
}
function onTouchMove(e: TouchEvent) {
  if (!dragging.value) return
  // 拖动卡片流时阻止浏览器默认手势（避免 Safari 上拉下提的橡皮筋弹性）
  e.preventDefault()
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

// 数据异步加载完成后初始化；分类切换/换一批也会重新洗牌
watch(pool, shuffle, { immediate: true })
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="吃 · 今天吃什么" show-back color-class="eat" />

    <!-- 筛选 chips -->
    <div class="shrink-0">
      <FilterBar v-model="meal" :options="DISH_MEALS" />
      <FilterBar v-model="dishType" :options="DISH_TYPES" />
    </div>

    <!-- 上滑卡片流 -->
    <div
      class="relative flex-1 overflow-hidden px-3 pb-3"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
      @wheel="onWheel"
    >
      <div
        v-for="(d, i) in deck"
        :key="d.id"
        class="absolute inset-0 transition-transform duration-300"
        :class="dragging ? '!transition-none' : ''"
        :style="cardStyle(i)"
      >
        <DishCard :dish="d" />
      </div>

      <!-- 空态 -->
      <div
        v-if="deck.length === 0"
        class="flex h-full items-center justify-center text-ink-muted"
      >
        🍽️ 没有符合条件的菜谱，换个筛选试试
      </div>
    </div>

    <!-- 底部控制条 -->
    <div
      v-if="deck.length > 0"
      class="flex shrink-0 items-center justify-between gap-3 px-4 pb-4 pt-1"
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
        <span v-if="meal !== '全部' || dishType !== '全部'"> · 已筛选</span>
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
