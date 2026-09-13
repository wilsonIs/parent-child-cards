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
    <AppHeader title="玩 · 今天玩什么" colorClass="play" />
    <p class="px-4 pt-3 text-center text-sm text-ink-muted">
      选个场景，看看能玩什么
    </p>
    <div class="grid grid-cols-3 gap-3 p-4 content-start flex-1 overflow-y-auto">
      <button
        v-for="s in PLAY_SCENES"
        :key="s.key"
        class="card-soft flex flex-col items-center justify-center gap-1 p-4 transition-all duration-150 active:scale-[0.97]"
        @click="go(s.key)"
      >
        <span class="text-4xl">{{ s.icon }}</span>
        <span class="text-base font-semibold text-ink">{{ s.key }}</span>
        <span class="text-center text-xs text-ink-muted">{{ s.desc }}</span>
      </button>
    </div>
  </div>
</template>
