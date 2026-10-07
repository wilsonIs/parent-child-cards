<script setup lang="ts">
import { useRouter } from 'vue-router'
import { colors } from '@/config/colors'

const props = defineProps<{
  title?: string
  showBack?: boolean
  colorClass?: string
}>()

const router = useRouter()
const c = colors(props.colorClass || 'cream')

function back() {
  if (history.state?.back) router.back()
  else router.push('/home')
}
</script>

<template>
  <header
    class="sticky top-0 z-20 flex items-center gap-2 px-4 py-3 bg-cream md:gap-4 md:px-8 md:py-5"
    style="padding-top: calc(var(--safe-top) + 0.75rem)"
  >
    <!-- 左侧：返回按钮 或 logo -->
    <button
      v-if="showBack"
      class="btn-ghost -ml-1 h-9 w-9 shrink-0 rounded-full px-0 md:h-12 md:w-12"
      aria-label="返回"
      @click="back"
    >
      <span class="text-lg md:text-2xl">←</span>
    </button>
    <img
      v-else
      src="/assets/icons/icon-192.jpg"
      alt="logo"
      class="h-9 w-9 shrink-0 rounded-xl object-cover shadow-soft md:h-14 md:w-14 md:rounded-2xl"
    />
    <h1
      class="flex-1 truncate text-center text-lg font-bold md:text-2xl"
      :class="c.textDeep"
    >
      {{ title || '神奇卡盒' }}
    </h1>
    <!-- 右侧：操作区 -->
    <div class="flex h-9 w-9 shrink-0 items-center justify-center md:h-12 md:w-12">
      <slot name="right" />
    </div>
  </header>
</template>
