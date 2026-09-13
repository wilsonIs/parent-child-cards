<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const tabs = [
  { to: '/home', icon: '🏠', label: '首页' },
  { to: '/today', icon: '⭐', label: '今日清单' },
  { to: '/favorites', icon: '❤️', label: '收藏' },
  { to: '/settings', icon: '⚙️', label: '设置' },
]

const activeTo = computed(() => route.path)
</script>

<template>
  <nav
    class="fixed bottom-0 left-1/2 z-20 flex w-full max-w-phone -translate-x-1/2 items-stretch justify-around border-t border-cream-200 bg-cream-50/95 backdrop-blur-md"
    style="padding-bottom: var(--safe-bottom)"
  >
    <RouterLink
      v-for="t in tabs"
      :key="t.to"
      :to="t.to"
      class="flex flex-1 flex-col items-center gap-0.5 py-2 text-2xl transition-opacity"
      :class="activeTo === t.to ? 'opacity-100' : 'opacity-50'"
    >
      <span>{{ t.icon }}</span>
      <span class="text-xs text-ink-soft">{{ t.label }}</span>
    </RouterLink>
  </nav>
</template>
