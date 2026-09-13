<script setup lang="ts">
import { computed, ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import FilterBar from '@/components/FilterBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import DishCard from '@/components/DishCard.vue'
import { useDataStore } from '@/stores/data'
import { DISH_MEALS, DISH_TYPES } from '@/config/modules'

const data = useDataStore()
const meal = ref('全部')
const dishType = ref('全部')

const list = computed(() =>
  data.dishes.filter((d) => {
    const okMeal = meal.value === '全部' || d.meal.includes(meal.value)
    const okType = dishType.value === '全部' || d.tags.includes(dishType.value)
    return okMeal && okType
  }),
)
</script>

<template>
  <div class="flex h-full flex-col">
    <AppHeader title="吃 · 今天吃什么" show-back color-class="eat" />
    <FilterBar :options="DISH_MEALS" v-model="meal" />
    <FilterBar :options="DISH_TYPES" v-model="dishType" />
    <div class="feed flex-1">
      <DishCard v-for="d in list" :key="d.id" :dish="d" />
      <EmptyState
        v-if="list.length === 0"
        icon="🍽️"
        text="没有符合条件的菜谱"
      />
    </div>
  </div>
</template>
