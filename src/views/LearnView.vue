<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import FilterBar from '@/components/FilterBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import LearnCard from '@/components/LearnCard.vue'
import { useDataStore } from '@/stores/data'
import { useSettingsStore } from '@/stores/settings'
import { LEARN_GRADES, LEARN_SUBJECTS } from '@/config/modules'

const data = useDataStore()
const settings = useSettingsStore()

const subject = ref('全部')
// 默认按设置里的孩子年级过滤（学龄前→一年级；未设置→全部），用户可手动切换
const grade = ref(
  settings.settings.childGrade === '学龄前'
    ? '一年级'
    : settings.settings.childGrade || '全部',
)

const filtered = computed(() =>
  data.learn.filter((l) => {
    const subjectOk = subject.value === '全部' || l.subject === subject.value
    const gradeOk =
      grade.value === '全部' ||
      l.grade === grade.value ||
      l.grade === '全年级'
    return subjectOk && gradeOk
  }),
)
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="学 · 今天学什么" show-back color-class="learn" />

    <div class="bg-learn-soft/60">
      <FilterBar v-model="subject" :options="LEARN_SUBJECTS" />
      <FilterBar v-model="grade" :options="LEARN_GRADES" />
    </div>

    <div class="px-4 pt-3">
      <RouterLink
        to="/poems"
        class="card-soft flex items-center justify-between gap-2 bg-gradient-to-br from-learn-soft/70 to-cream-100 p-4 transition-transform active:scale-[0.98]"
      >
        <div class="flex items-center gap-3">
          <span class="text-4xl">🪶</span>
          <div>
            <h3 class="font-bold text-ink">古诗 · 蒙学</h3>
            <p class="text-xs text-ink-muted">
              唐诗三百首 · 三字经 · 百家姓 · 千字文 · 弟子规 · 声律启蒙
            </p>
          </div>
        </div>
        <span class="text-ink-muted">›</span>
      </RouterLink>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="filtered.length" class="flex flex-col gap-3 p-4">
        <LearnCard v-for="l in filtered" :key="l.id" :learn="l" />
      </div>
      <EmptyState
        v-else
        icon="📚"
        text="没有符合条件的资源"
        hint="换个学科或年级试试"
      />
    </div>
  </div>
</template>
