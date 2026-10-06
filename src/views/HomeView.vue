<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { MODULES } from '@/config/modules'
import { colors } from '@/config/colors'
import { useTodayStore } from '@/stores/today'
import { useSettingsStore } from '@/stores/settings'
import { useDataStore } from '@/stores/data'

const today = useTodayStore()
const settings = useSettingsStore()
const data = useDataStore()

const cards = computed(() =>
  MODULES.map((m) => ({ m, c: colors(m.colorClass) })),
)

/** 最近听过的故事（取最近 5 个） */
const recentStories = computed(() =>
  settings.history
    .filter((h) => h.type === 'story')
    .slice(0, 5)
    .map((h) => data.storyById(h.id))
    .filter((s): s is NonNullable<typeof s> => Boolean(s)),
)
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="亲子卡片箱" />
    <main class="flex-1 overflow-y-auto">
      <!-- 欢迎区 -->
      <section
        class="fade-up relative mx-4 mt-4 overflow-hidden rounded-4xl shadow-card"
      >
        <img
          src="/assets/covers/welcome.jpg"
          alt=""
          class="absolute inset-0 h-full w-full object-cover"
        />
        <div class="relative flex items-center justify-between gap-3 p-6">
          <div>
            <h2 class="text-2xl font-bold leading-snug text-ink">
              今天，和孩子做点什么呢？
            </h2>
            <p class="mt-1 text-sm text-ink-soft">简单 · 纯粹 · 不上瘾</p>
          </div>
          <RouterLink
            v-if="today.count > 0"
            to="/today"
            class="chip shrink-0 bg-white text-coral shadow-soft"
          >
            今日 {{ today.count }}
          </RouterLink>
        </div>
      </section>

      <!-- 最近听过 -->
      <section v-if="recentStories.length" class="px-4 pt-4">
        <div class="mb-2 flex items-center justify-between">
          <h3 class="text-sm font-bold text-ink">最近听过</h3>
          <RouterLink to="/story" class="text-xs text-coral">去故事 ›</RouterLink>
        </div>
        <div class="scrollbar-none flex gap-3 overflow-x-auto pb-1">
          <RouterLink
            v-for="st in recentStories"
            :key="st.id"
            :to="`/story/${st.id}`"
            class="flex w-24 shrink-0 flex-col items-center gap-1 rounded-2xl border border-cream-200 bg-white/80 p-3 text-center shadow-soft transition-transform active:scale-95"
          >
            <span
              class="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-story-soft to-story-light text-3xl"
              >{{ st.icon }}</span
            >
            <span class="line-clamp-1 w-full text-xs font-bold text-ink">{{
              st.title
            }}</span>
            <span class="text-[10px] text-ink-muted">{{ st.duration }}</span>
          </RouterLink>
        </div>
      </section>

      <!-- 模块卡片网格 -->
      <section class="grid grid-cols-2 gap-3 p-4">
        <RouterLink
          v-for="{ m, c } in cards"
          :key="m.key"
          :to="m.to"
          class="block transition-transform active:scale-[0.97]"
        >
          <div
            class="card-soft relative flex flex-col items-start gap-1 overflow-hidden p-5"
            :class="[m.image ? 'aspect-[4/3]' : ['min-h-[7rem]', c.gradFrom, c.gradTo]]"
          >
            <!-- 模块背景图（有图时铺满） -->
            <img
              v-if="m.image"
              :src="m.image"
              :alt="m.title"
              class="absolute inset-0 h-full w-full object-cover"
            />
            <!-- 无图时的 emoji 水印 -->
            <span
              v-if="!m.image"
              class="pointer-events-none absolute -bottom-3 -right-3 select-none text-8xl opacity-25"
              aria-hidden="true"
              >{{ m.icon }}</span
            >
            <span v-if="!m.image" class="text-5xl leading-none drop-shadow-sm">{{
              m.icon
            }}</span>
            <h3 class="relative mt-1 text-xl font-bold text-white drop-shadow-md">
              {{ m.title }}
            </h3>
            <p class="relative text-xs font-medium text-white/95 drop-shadow-sm">{{
              m.subtitle
            }}</p>
          </div>
        </RouterLink>
      </section>

      <p class="px-4 pb-6 text-center text-xs text-ink-muted">
        无广告 · 无 VIP · 无推送 · 无积分
      </p>
    </main>
  </div>
</template>
