<script setup lang="ts">
import { useIdlePrefetch } from '@/composables/useIdlePrefetch'
import { usePWAUpdate } from '@/composables/usePWAUpdate'

// 空闲时预缓存音频
useIdlePrefetch()

// PWA 更新检测
const { needRefresh, offlineReady, update, close } = usePWAUpdate()
</script>

<template>
  <div class="flex h-full flex-col pb-2">
    <RouterView v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </RouterView>

    <!-- 离线就绪提示（3秒自动消失）-->
    <Transition name="toast">
      <div
        v-if="offlineReady"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 rounded-full bg-ink/90 px-5 py-2.5 text-sm text-white shadow-lg"
      >
        ✅ 已可离线使用
      </div>
    </Transition>

    <!-- 发现新版本提示 -->
    <Transition name="toast">
      <div
        v-if="needRefresh"
        class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 rounded-2xl bg-white px-4 py-3 shadow-xl"
      >
        <span class="text-sm font-semibold text-ink">🎉 发现新内容</span>
        <button
          class="rounded-full bg-coral px-4 py-1.5 text-sm font-bold text-white active:scale-95"
          @click="update"
        >
          更新
        </button>
        <button class="text-sm text-ink-muted" @click="close">稍后</button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}
</style>
