<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps<{
  src: string
  alt?: string
  rounded?: string
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
    { rootMargin: '300px' },
  )
  observer.observe(el.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <div ref="el" class="relative overflow-hidden bg-cream-200/60" :class="rounded">
    <img
      :src="actualSrc"
      :alt="alt"
      loading="lazy"
      class="h-full w-full object-cover transition-opacity duration-300"
      :class="loaded ? 'opacity-100' : 'opacity-0'"
      @load="loaded = true"
    />
    <!-- 加载中骨架 -->
    <div
      v-if="!loaded"
      class="absolute inset-0 animate-pulse bg-gradient-to-br from-cream-200/80 to-cream-300/40"
    ></div>
  </div>
</template>