<script setup lang="ts">
import { computed, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import FilterBar from '@/components/FilterBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import LearnCard from '@/components/LearnCard.vue'
import { useDataStore } from '@/stores/data'
import { LEARN_GRADES, LEARN_SUBJECTS } from '@/config/modules'

const data = useDataStore()

const subject = ref('全部')
const grade = ref('全部')

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
    <AppHeader title="学 · 今天学什么" color-class="learn" />

    <div class="bg-learn-soft/60">
      <FilterBar v-model="subject" :options="LEARN_SUBJECTS" />
      <FilterBar v-model="grade" :options="LEARN_GRADES" />
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
