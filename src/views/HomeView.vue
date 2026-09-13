<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { MODULES } from '@/config/modules'
import { colors } from '@/config/colors'
import { useTodayStore } from '@/stores/today'

const today = useTodayStore()

const cards = computed(() =>
  MODULES.map((m) => ({ m, c: colors(m.colorClass) })),
)
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="亲子卡片箱" />
    <main class="flex-1 overflow-y-auto">
      <!-- 欢迎区 -->
      <section
        class="fade-up mx-4 mt-4 rounded-4xl bg-gradient-to-br from-coral-soft to-cream-100 p-6 shadow-card"
      >
        <div class="flex items-center justify-between gap-3">
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

      <!-- 模块卡片网格 -->
      <section class="grid grid-cols-2 gap-3 p-4">
        <RouterLink
          v-for="{ m, c } in cards"
          :key="m.key"
          :to="m.to"
          class="block transition-transform active:scale-[0.97]"
        >
          <div
            class="card-soft flex flex-col items-start gap-1 bg-gradient-to-br p-5"
            :class="[c.gradFrom, c.gradTo]"
          >
            <span class="text-6xl leading-none">{{ m.icon }}</span>
            <h3 class="mt-1 text-xl font-bold" :class="c.textDeep">
              {{ m.title }}
            </h3>
            <p class="text-xs text-ink-soft">{{ m.subtitle }}</p>
          </div>
        </RouterLink>
      </section>

      <p class="px-4 pb-6 text-center text-xs text-ink-muted">
        无广告 · 无 VIP · 无推送 · 无积分
      </p>
    </main>
  </div>
</template>
