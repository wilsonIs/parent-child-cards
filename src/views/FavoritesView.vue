<script setup lang="ts">
import { computed } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import { useFavoritesStore } from '@/stores/favorites'
import { useDataStore } from '@/stores/data'
import type { ItemType } from '@/types'

const fav = useFavoritesStore()
const data = useDataStore()

const TYPE_META: Record<ItemType, { label: string; icon: string }> = {
  dish: { label: '吃', icon: '🍚' },
  learn: { label: '学', icon: '📚' },
  story: { label: '故事', icon: '📖' },
  game: { label: '玩', icon: '🎲' },
  poem: { label: '古诗', icon: '🪶' },
}
const ORDER: ItemType[] = ['dish', 'learn', 'poem', 'story', 'game']

/** 解析条目标题与图标；数据未加载时回退 id 占位 */
function resolve(type: ItemType, id: string) {
  const item = data.itemByType(type, id)
  if (!item) return { title: id, icon: TYPE_META[type].icon }
  if ('name' in item) return { title: item.name, icon: item.icon }
  if ('subject' in item) return { title: item.title, icon: TYPE_META[type].icon }
  if ('paragraphs' in item) return { title: item.title, icon: TYPE_META[type].icon }
  return { title: item.title, icon: item.icon }
}

const groups = computed(() =>
  ORDER.map((type) => ({
    type,
    meta: TYPE_META[type],
    items: fav.items
      .filter((i) => i.type === type)
      .map((i) => ({ id: i.id, ...resolve(type, i.id) })),
  })).filter((g) => g.items.length > 0),
)

function confirmClear() {
  if (window.confirm('确定清空全部收藏吗？')) fav.clear()
}
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="收藏" />
    <div class="flex-1 overflow-y-auto p-4">
      <EmptyState
        v-if="fav.count === 0"
        icon="❤️"
        text="还没有收藏"
        hint="看到喜欢的菜谱、故事、游戏，点 🤍 收起来"
      />
      <template v-else>
        <div class="mb-4 flex items-center justify-between">
          <span class="text-sm text-ink-soft">共 {{ fav.count }} 条</span>
          <button class="btn-ghost text-sm" @click="confirmClear">
            清空收藏
          </button>
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
                  @click="fav.remove(g.type, it.id)"
                >
                  取消收藏
                </button>
              </li>
            </ul>
          </section>
        </div>
      </template>
    </div>
  </div>
</template>
