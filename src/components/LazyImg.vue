<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps<{
  src: string
  alt?: string
  placeholder?: string
}>()

const loaded = ref(false)
const el = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null
const actualSrc = ref('')

onMounted(() => {
  if (!el.value) return
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          actualSrc.value = props.src
          observer?.disconnect()
          observer = null
        }
      }
    },
    { rootMargin: '200px' },
  )
  observer.observe(el.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <img
    ref="el"
    :src="actualSrc"
    :alt="alt"
    loading="lazy"
    @load="loaded = true"
  />
</template>