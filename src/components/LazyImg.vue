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
  <div ref="el" class="relative overflow-hidden" :class="rounded">
    <img
      :src="actualSrc"
      :alt="alt"
      loading="lazy"
      class="h-full w-full object-cover transition-opacity duration-300"
      :class="loaded ? 'opacity-100' : 'opacity-0'"
      @load="loaded = true"
    />
    <!-- 加载中：暖色骨架 + 滑动光泽 -->
    <div
      v-if="!loaded"
      class="absolute inset-0 bg-gradient-to-br from-coral/20 via-sunlight/30 to-teal/20"
    >
      <!-- 滑动光泽 -->
      <div class="shimmer absolute inset-0"></div>
    </div>
  </div>
</template>

<style scoped>
.shimmer {
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.45) 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: shimmer-slide 1.5s ease-in-out infinite;
}

@keyframes shimmer-slide {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
