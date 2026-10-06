<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const tabs = [
  { to: '/home', icon: '/assets/icons/home.jpg', label: '首页' },
  { to: '/today', icon: '/assets/icons/star.jpg', label: '今日清单' },
  { to: '/favorites', icon: '/assets/icons/heart.jpg', label: '收藏' },
  { to: '/settings', icon: '/assets/icons/settings.jpg', label: '设置' },
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
      class="flex flex-1 flex-col items-center gap-0.5 py-2"
      :class="activeTo === t.to ? 'opacity-100' : 'opacity-45'"
    >
      <span
        class="flex h-7 w-12 items-center justify-center rounded-full transition-all duration-150"
        :class="
          activeTo === t.to
            ? 'bg-gradient-to-b from-coral-soft to-coral-light shadow-soft'
            : 'bg-transparent'
        "
        ><img
          :src="t.icon"
          :alt="t.label"
          class="h-6 w-6 rounded-full object-cover"
        /></span
      >
      <span
        class="text-xs"
        :class="activeTo === t.to ? 'font-bold text-coral' : 'text-ink-soft'"
        >{{ t.label }}</span
      >
    </RouterLink>
  </nav>
</template>
