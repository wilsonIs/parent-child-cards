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
    class="sticky top-0 z-20 flex items-center gap-2 px-4 py-3 bg-cream"
    style="padding-top: calc(var(--safe-top) + 0.75rem)"
  >
    <!-- 左侧：返回按钮 或 logo -->
    <button
      v-if="showBack"
      class="btn-ghost -ml-1 h-9 w-9 shrink-0 rounded-full px-0"
      aria-label="返回"
      @click="back"
    >
      <span class="text-lg">←</span>
    </button>
    <img
      v-else
      src="/assets/icons/icon-192.jpg"
      alt="logo"
      class="h-9 w-9 shrink-0 rounded-xl object-cover shadow-soft"
    />
    <h1
      class="flex-1 truncate text-center text-lg font-bold"
      :class="c.textDeep"
    >
      {{ title || '神奇卡盒' }}
    </h1>
    <!-- 右侧：操作区 -->
    <div class="flex h-9 w-9 shrink-0 items-center justify-center">
      <slot name="right" />
    </div>
  </header>
</template>
