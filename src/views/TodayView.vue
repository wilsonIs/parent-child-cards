<script setup lang="ts">
import { computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { useTodayStore } from '@/stores/today'
import { useDataStore } from '@/stores/data'
import type { ItemType } from '@/types'

const today = useTodayStore()
const data = useDataStore()

const TYPE_META: Record<ItemType, { label: string; icon: string }> = {
  dish: { label: '吃', icon: '🍚' },
  learn: { label: '学', icon: '📚' },
  story: { label: '故事', icon: '📖' },
  game: { label: '玩', icon: '🎲' },
}
const ORDER: ItemType[] = ['dish', 'learn', 'story', 'game']

/** 解析条目标题与图标；数据未加载时回退 id 占位 */
function resolve(type: ItemType, id: string) {
  const item = data.itemByType(type, id)
  if (!item) return { title: id, icon: TYPE_META[type].icon }
  if ('name' in item) return { title: item.name, icon: item.icon }
  if ('subject' in item) return { title: item.title, icon: TYPE_META[type].icon }
  return { title: item.title, icon: item.icon }
}

const groups = computed(() =>
  ORDER.map((type) => ({
    type,
    meta: TYPE_META[type],
    items: today.items
      .filter((i) => i.type === type)
      .map((i) => ({ id: i.id, ...resolve(type, i.id) })),
  })).filter((g) => g.items.length > 0),
)

function confirmClear() {
  if (window.confirm('确定清空今日清单吗？')) today.clear()
}
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="今日清单" />
    <div class="flex-1 overflow-y-auto p-4">
      <EmptyState
        v-if="today.count === 0"
        icon="⭐"
        text="今日清单是空的"
        hint="去吃/学/故事/玩里，把想做的加进来吧"
      />
      <template v-else>
        <div class="mb-4 flex items-center justify-between">
          <span class="text-sm text-ink-soft">共 {{ today.count }} 项</span>
          <button class="btn-ghost text-sm" @click="confirmClear">清空</button>
        </div>

        <div class="space-y-5">
          <section v-for="g in groups" :key="g.type">
            <h3
              class="mb-2 flex items-center gap-2 text-sm font-bold text-ink-soft"
            >
              <span>{{ g.meta.icon }}</span>
              <span>{{ g.meta.label }}</span>
              <span class="text-ink-muted">{{ g.items.length }}</span>
            </h3>
            <ul class="space-y-2">
              <li
                v-for="it in g.items"
                :key="it.id"
                class="card-soft flex items-center gap-3 p-3"
              >
                <span class="text-2xl">{{ it.icon }}</span>
                <span class="flex-1 truncate text-ink">{{ it.title }}</span>
                <button
                  class="btn-ghost px-3 text-sm"
                  @click="today.remove(g.type, it.id)"
                >
                  移除
                </button>
              </li>
            </ul>
          </section>
        </div>
      </template>
    </div>
  </div>
</template>
