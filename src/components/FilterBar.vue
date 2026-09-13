<script setup lang="ts">
defineProps<{
  options: string[]
  modelValue: string
}>()
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()

function pick(v: string) {
  emit('update:modelValue', v)
}
</script>

<template>
  <div class="no-scrollbar flex gap-2 overflow-x-auto px-4 py-2">
    <button
      v-for="opt in options"
      :key="opt"
      class="chip"
      :class="modelValue === opt ? 'chip-on' : 'chip-off'"
      @click="pick(opt)"
    >
      {{ opt }}
    </button>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  scrollbar-width: none;
}
</style>
