<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { MODULES } from '@/config/modules'
import { colors } from '@/config/colors'
import { useSettingsStore } from '@/stores/settings'
import { useDataStore } from '@/stores/data'

const settings = useSettingsStore()
const data = useDataStore()
const BASE_URL = import.meta.env.BASE_URL

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
    <AppHeader title="神奇卡盒">
      <template #right>
        <RouterLink
          to="/settings"
          class="flex h-9 w-9 items-center justify-center rounded-full bg-cream-200/70 transition-colors active:bg-cream-200 md:h-12 md:w-12"
          aria-label="设置"
        >
          <img
            src="/assets/icons/settings.jpg"
            alt="设置"
            class="h-6 w-6 rounded-full object-cover md:h-8 md:w-8"
          />
        </RouterLink>
      </template>
    </AppHeader>
    <main class="flex-1 overflow-y-auto">
      <!-- 欢迎区 -->
      <section
        class="fade-up relative mx-4 mt-4 overflow-hidden rounded-4xl shadow-card md:mx-6 md:mt-6 lg:mx-8 lg:mt-8"
      >
        <img
          :src="`${BASE_URL}assets/covers/welcome.jpg`"
          alt=""
          loading="lazy"
          class="absolute inset-0 h-full w-full object-cover"
        />
        <div class="relative flex items-center justify-between gap-3 p-6 md:p-8 lg:p-10">
          <div>
            <h2 class="text-3xl font-bold leading-snug text-ink md:text-4xl lg:text-5xl">今天玩什么？</h2>
            <p class="mt-1 text-sm text-ink-soft md:text-base lg:text-lg">选一个，开始吧</p>
          </div>
          <span class="float-soft text-5xl md:text-6xl lg:text-7xl">🎈</span>
        </div>
      </section>

      <!-- 最近听过 -->
      <section v-if="recentStories.length" class="px-4 pt-4 md:px-6 md:pt-6 lg:px-8 lg:pt-8">
        <div class="mb-2 flex items-center justify-between">
          <h3 class="text-sm font-bold text-ink md:text-base lg:text-lg">最近听过</h3>
          <RouterLink to="/story" class="text-xs text-coral md:text-sm lg:text-base">去故事 ›</RouterLink>
        </div>
        <div class="scrollbar-none flex gap-3 overflow-x-auto pb-1 md:gap-4">
          <RouterLink
            v-for="st in recentStories"
            :key="st.id"
            :to="`/story/${st.id}`"
            class="flex w-24 shrink-0 flex-col items-center gap-1 rounded-2xl border border-cream-200 bg-white/80 p-3 text-center shadow-soft transition-transform active:scale-90 md:w-32 md:p-4 lg:w-36"
          >
            <span
              class="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-story-soft to-story-light text-3xl md:h-16 md:w-16 md:text-4xl lg:h-20 lg:w-20 lg:text-5xl"
              >{{ st.icon }}</span
            >
            <span class="line-clamp-1 w-full text-xs font-bold text-ink md:text-sm lg:text-base">{{
              st.title
            }}</span>
            <span class="text-[10px] text-ink-muted md:text-xs lg:text-sm">{{ st.duration }}</span>
          </RouterLink>
        </div>
      </section>

      <!-- 模块卡片网格 -->
      <section class="grid grid-cols-2 gap-3 p-4 md:gap-4 md:p-6 md:grid-cols-3 lg:grid-cols-4 lg:p-8">
        <RouterLink
          v-for="({ m, c }, i) in cards"
          :key="m.key"
          :to="m.to"
          class="block transition-transform duration-150 active:scale-95"
          :style="{ animationDelay: `${i * 80}ms` }"
        >
          <div
            class="card-soft fade-up relative flex flex-col items-start gap-1 overflow-hidden p-5 md:p-6 lg:p-7"
            :class="[m.image ? 'aspect-[4/3] md:aspect-square lg:aspect-[5/6]' : ['min-h-[7rem] md:min-h-[9rem] lg:min-h-[11rem]', c.gradFrom, c.gradTo]]"
          >
            <!-- 模块背景图（有图时铺满） -->
            <img
              v-if="m.image"
              :src="m.image"
              :alt="m.title"
              loading="lazy"
              class="absolute inset-0 h-full w-full object-cover"
            />
            <!-- 无图时的 emoji 水印 -->
            <span
              v-if="!m.image"
              class="pointer-events-none absolute -bottom-3 -right-3 select-none text-8xl opacity-25 md:text-9xl lg:text-[10rem]"
              aria-hidden="true"
              >{{ m.icon }}</span
            >
            <span v-if="!m.image" class="text-5xl leading-none drop-shadow-sm md:text-6xl lg:text-7xl">{{
              m.icon
            }}</span>
            <h3 class="relative mt-1 text-xl font-bold text-white drop-shadow-md md:text-2xl lg:text-3xl">
              {{ m.title }}
            </h3>
            <p class="relative text-xs font-medium text-white/95 drop-shadow-sm md:text-sm lg:text-base">{{
              m.subtitle
            }}</p>
          </div>
        </RouterLink>
      </section>
    </main>
  </div>
</template>
