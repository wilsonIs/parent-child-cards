<script setup lang="ts">
defineProps<{
  icon?: string
  text?: string
  hint?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3 px-8 py-16 text-center">
    <div class="text-6xl">{{ icon || '📭' }}</div>
    <p class="text-lg font-medium text-ink-soft">{{ text || '还没有内容' }}</p>
    <p v-if="hint" class="text-sm text-ink-muted">{{ hint }}</p>
  </div>
</template>
