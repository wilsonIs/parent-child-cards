<script setup lang="ts">
defineProps<{
  icon?: string
  text?: string
  hint?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3 px-8 py-16 text-center">
    <img
      src="/assets/icons/scenes/empty.jpg"
      alt="空"
      class="float-soft h-24 w-24 object-contain"
    />
    <p class="text-lg font-bold text-ink">{{ text || '还没有内容' }}</p>
    <p v-if="hint" class="text-sm text-ink-muted">{{ hint }}</p>
  </div>
</template>
