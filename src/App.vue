<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TabBar from '@/components/TabBar.vue'

const route = useRoute()
// 顶部模块页（吃/学/故事/玩及详情）不显示底部 tabbar，仅首页与今日/收藏/设置显示
const showTabBar = computed(() => {
  return ['/home', '/today', '/favorites', '/settings'].includes(
    route.path,
  )
})

// 列表页留底部 tabbar 空间
const padBottom = computed(() => (showTabBar.value ? 'pb-16' : 'pb-2'))
</script>

<template>
  <div class="flex h-full flex-col" :class="padBottom">
    <RouterView v-slot="{ Component }">
      <component :is="Component" />
    </RouterView>
    <TabBar v-if="showTabBar" />
  </div>
</template>
