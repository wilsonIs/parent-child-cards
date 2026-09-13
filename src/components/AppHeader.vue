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
    class="sticky top-0 z-20 flex items-center gap-2 px-4 py-3 backdrop-blur-md bg-cream-50/85 border-b border-cream-200"
    style="padding-top: calc(var(--safe-top) + 0.75rem)"
  >
    <button
      v-if="showBack"
      class="btn-ghost -ml-1 h-9 w-9 rounded-full px-0"
      aria-label="返回"
      @click="back"
    >
      <span class="text-lg">←</span>
    </button>
    <h1
      class="flex-1 truncate text-center text-lg font-bold"
      :class="c.textDeep"
    >
      {{ title || '亲子卡片箱' }}
    </h1>
    <span class="h-9 w-9" v-if="showBack"></span>
  </header>
</template>
