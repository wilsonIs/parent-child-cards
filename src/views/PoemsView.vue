<script setup lang="ts">
import { computed, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import FilterBar from '@/components/FilterBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import PoemCard from '@/components/PoemCard.vue'
import { useDataStore } from '@/stores/data'
import { useSettingsStore } from '@/stores/settings'
import { GRADE_LEVEL } from '@/config/modules'

const data = useDataStore()
const settings = useSettingsStore()

const category = ref('全部')
const CATEGORIES = ['全部', '唐诗', '蒙学', '诗经']

/** 用户设置的孩子年级（数字等级；'全部' = 不过滤） */
const gradeLevel = computed(() =>
  settings.settings.childGrade === '全部'
    ? null
    : GRADE_LEVEL[settings.settings.childGrade] ?? null,
)

/** 按「起读年级 <= 用户年级」过滤，未设置时全部展示 */
const filtered = computed(() => {
  const g = gradeLevel.value
  const byCat =
    category.value === '全部'
      ? data.poems
      : data.poems.filter((p) => p.category === category.value)
  if (g === null) return byCat
  return byCat.filter((p) => (GRADE_LEVEL[p.grade] ?? 6) <= g)
})

const filteredNote = computed(() => {
  if (gradeLevel.value === null) return ''
  return `已按「${settings.settings.childGrade}」筛选（${filtered.value.length} 篇）· 可在设置中修改`
})
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="学 · 古诗蒙学" show-back color-class="learn" />

    <div class="bg-learn-soft/60">
      <FilterBar v-model="category" :options="CATEGORIES" />
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="filtered.length" class="flex flex-col gap-3 p-4">
        <p class="text-xs text-ink-muted">
          {{
            filteredNote ||
            `共 ${filtered.length} 篇 · 由 chinese-poetry 开源数据集自动同步（MIT 许可 · 古籍公版）`
          }}
        </p>
        <PoemCard v-for="p in filtered" :key="p.id" :poem="p" />
      </div>
      <EmptyState
        v-else
        icon="🪶"
        text="没有符合条件的诗文"
        hint="换个分类，或到设置里调整孩子年级"
      />
    </div>
  </div>
</template>
