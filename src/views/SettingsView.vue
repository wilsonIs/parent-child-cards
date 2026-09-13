<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import { useSettingsStore } from '@/stores/settings'
import { useFavoritesStore } from '@/stores/favorites'
import { useTodayStore } from '@/stores/today'
import { POEM_GRADES } from '@/config/modules'

const settings = useSettingsStore()
const fav = useFavoritesStore()
const today = useTodayStore()

const PLAYBACK_RATES = [0.75, 1, 1.25]

function clearFav() {
  if (window.confirm('确定清空全部收藏吗？')) fav.clear()
}
function clearToday() {
  if (window.confirm('确定清空今日清单吗？')) today.clear()
}
function clearAll() {
  if (
    window.confirm(
      '确定清空全部数据（收藏 / 今日 / 浏览习惯 / 设置）吗？此操作不可撤销。',
    )
  ) {
    settings.clearAllUserData()
    fav.clear()
    today.clear()
  }
}
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="设置" show-back />
    <div class="flex-1 overflow-y-auto space-y-4 p-4">
      <!-- 1. 故事语速 -->
      <section class="card-soft space-y-3 p-4">
        <div>
          <h3 class="font-bold text-ink">故事语速</h3>
          <p class="text-xs text-ink-muted">听故事时的朗读速度</p>
        </div>
        <div class="flex gap-2">
          <button
            v-for="r in PLAYBACK_RATES"
            :key="r"
            class="btn flex-1"
            :class="
              settings.settings.playbackRate === r ? 'btn-primary' : 'btn-ghost'
            "
            @click="settings.setPlaybackRate(r)"
          >
            {{ r }}×
          </button>
        </div>
      </section>

      <!-- 1.5 自动连播 -->
      <section class="card-soft space-y-3 p-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-bold text-ink">自动听下一个</h3>
            <p class="text-xs text-ink-muted">
              故事播完后自动切换到下一个（同系列优先，系列播完随机）
            </p>
          </div>
          <button
            class="relative h-7 w-12 shrink-0 rounded-full transition-colors"
            :class="
              settings.settings.autoPlay ? 'bg-story' : 'bg-cream-300'
            "
            role="switch"
            :aria-checked="settings.settings.autoPlay"
            @click="settings.toggleAutoPlay()"
          >
            <span
              class="absolute top-1 h-5 w-5 rounded-full bg-white shadow-soft transition-all"
              :class="
                settings.settings.autoPlay ? 'left-6' : 'left-1'
              "
            ></span>
          </button>
        </div>
      </section>

      <!-- 2. 孩子年级 -->
      <section class="card-soft space-y-3 p-4">
        <div>
          <h3 class="font-bold text-ink">孩子年级</h3>
          <p class="text-xs text-ink-muted">古诗蒙学等内容默认按此过滤</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="g in POEM_GRADES"
            :key="g"
            class="chip"
            :class="
              settings.settings.childGrade === g ? 'chip-on' : 'chip-off'
            "
            @click="settings.setChildGrade(g)"
          >
            {{ g }}
          </button>
        </div>
      </section>

      <!-- 3. 字体大小 -->
      <section class="card-soft space-y-3 p-4">
        <div>
          <h3 class="font-bold text-ink">字体大小</h3>
          <p class="text-xs text-ink-muted">适合家长的阅读大小</p>
        </div>
        <div class="flex gap-2">
          <button
            class="btn flex-1"
            :class="
              settings.settings.fontSize === 'normal' ? 'btn-primary' : 'btn-ghost'
            "
            @click="settings.setFontSize('normal')"
          >
            标准
          </button>
          <button
            class="btn flex-1"
            :class="
              settings.settings.fontSize === 'large' ? 'btn-primary' : 'btn-ghost'
            "
            @click="settings.setFontSize('large')"
          >
            大号
          </button>
        </div>
      </section>

      <!-- 3. 数据管理 -->
      <section class="card-soft space-y-3 p-4">
        <div>
          <h3 class="font-bold text-ink">数据管理</h3>
          <p class="text-xs text-ink-muted">
            收藏 {{ fav.count }} 条 · 今日 {{ today.count }} 条
          </p>
        </div>
        <div class="space-y-2">
          <button class="btn btn-ghost w-full" @click="clearFav">清空收藏</button>
          <button class="btn btn-ghost w-full" @click="clearToday">
            清空今日
          </button>
          <button class="btn btn-primary w-full" @click="clearAll">
            清空全部数据
          </button>
        </div>
      </section>

      <!-- 4. 关于 -->
      <section class="card-soft space-y-2 p-4">
        <h3 class="text-lg font-bold text-ink">亲子卡片箱</h3>
        <p class="text-sm text-ink-soft">
          和孩子一起，每天简单做点事。
        </p>
        <p class="text-xs text-ink-muted">
          无广告 · 无 VIP · 无内购 · 无推送 · 无积分 · 无排行榜
        </p>
        <p class="text-xs text-ink-muted">数据本地存储，不上传</p>
      </section>
    </div>
  </div>
</template>
