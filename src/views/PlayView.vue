<script setup lang="ts">
import { useRouter } from 'vue-router'
import { PLAY_SCENES } from '@/config/modules'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()

function go(key: string) {
  router.push(`/play/${encodeURIComponent(key)}`)
}
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="玩 · 今天玩什么" show-back colorClass="play" />
    <p class="px-4 pt-3 text-center text-sm text-ink-muted">
      选个场景，看看能玩什么
    </p>
    <div class="grid grid-cols-3 gap-3 p-4 content-start flex-1 overflow-y-auto md:gap-4 md:p-6 md:grid-cols-4 lg:grid-cols-5">
      <button
        v-for="s in PLAY_SCENES"
        :key="s.key"
        class="card-soft flex flex-col items-center justify-center gap-1 p-4 transition-all duration-150 active:scale-95 md:gap-2 md:p-6"
        @click="go(s.key)"
      >
        <img
          v-if="s.image"
          :src="s.image"
          :alt="s.key"
          class="h-16 w-16 rounded-2xl object-cover md:h-20 md:w-20"
        />
        <span v-else class="text-4xl md:text-5xl">{{ s.icon }}</span>
        <span class="text-base font-semibold text-ink md:text-lg">{{ s.key }}</span>
        <span class="text-center text-xs text-ink-muted md:text-sm">{{ s.desc }}</span>
      </button>
    </div>
  </div>
</template>
