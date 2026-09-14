<script setup lang="ts">
import { ref } from 'vue'
import type { Dish } from '@/types'
import ActionButtons from '@/components/ActionButtons.vue'
import { useSettingsStore } from '@/stores/settings'

const props = defineProps<{ dish: Dish }>()

const settings = useSettingsStore()
const expand = ref(false)

function toggleExpand() {
  expand.value = !expand.value
  if (expand.value) settings.recordView('dish', props.dish.id)
}
</script>

<template>
  <article class="snap-card card-soft h-full flex flex-col overflow-hidden">
    <!-- 点击切换展开 -->
    <div
      class="flex min-h-0 flex-1 cursor-pointer flex-col"
      @click="toggleExpand"
    >
      <!-- 封面 -->
      <div
        class="relative flex min-h-0 flex-1 items-center justify-center overflow-hidden bg-gradient-to-br from-eat to-eat-deep"
      >
        <img
          v-if="dish.image"
          :src="dish.image"
          :alt="dish.name"
          class="h-full w-full object-cover"
        />
        <template v-else>
          <span class="pointer-events-none absolute -left-6 -top-8 h-28 w-28 rounded-full bg-white/15" aria-hidden="true"></span>
          <span class="pointer-events-none absolute -bottom-10 -right-4 h-32 w-32 rounded-full bg-white/10" aria-hidden="true"></span>
          <span class="select-none text-9xl drop-shadow-lg">{{ dish.icon }}</span>
        </template>
      </div>

      <!-- 标题信息 -->
      <div class="shrink-0 px-5 pt-4">
        <h2 class="text-2xl font-bold text-eat-deep">{{ dish.name }}</h2>
        <div class="mt-2 flex flex-wrap gap-1.5">
          <span
            v-for="t in dish.tags"
            :key="t"
            class="chip bg-eat-soft text-eat-deep"
            >{{ t }}</span
          >
        </div>
        <div class="mt-2 flex flex-wrap items-center gap-2 text-sm text-ink-muted">
          <span>👶 {{ dish.age }}</span>
          <span aria-hidden="true">·</span>
          <span>{{ dish.meal.join(' / ') }}</span>
          <span class="ml-auto text-eat">{{ expand ? '收起 ▲' : '展开 ▼' }}</span>
        </div>
      </div>
    </div>

    <!-- 展开内容 -->
    <div
      class="overflow-hidden px-5 transition-all duration-200 ease-out"
      :style="
        expand
          ? { maxHeight: '60vh', opacity: 1 }
          : { maxHeight: '0', opacity: 0 }
      "
    >
      <div class="max-h-[55vh] overflow-y-auto pb-2 pt-4">
        <section class="mb-3">
          <h3 class="mb-1 text-sm font-semibold text-ink-soft">食材</h3>
          <ul class="flex flex-wrap gap-1.5">
            <li
              v-for="(i, idx) in dish.ingredients"
              :key="idx"
              class="chip chip-off"
            >
              {{ i }}
            </li>
          </ul>
        </section>
        <section class="mb-3">
          <h3 class="mb-1 text-sm font-semibold text-ink-soft">做法</h3>
          <ol class="space-y-1.5 text-sm text-ink-soft">
            <li
              v-for="(s, idx) in dish.steps"
              :key="idx"
              class="flex gap-2"
            >
              <span class="shrink-0 text-eat">{{ idx + 1 }}.</span>
              <span>{{ s }}</span>
            </li>
          </ol>
        </section>
        <section v-if="dish.tips" class="mb-1">
          <h3 class="mb-1 text-sm font-semibold text-ink-soft">小贴士</h3>
          <p class="rounded-2xl bg-cream-200 px-3 py-2 text-sm text-ink-soft">
            {{ dish.tips }}
          </p>
        </section>
      </div>
    </div>

    <!-- 底部操作 -->
    <footer class="shrink-0 border-t border-cream-200 px-5 py-3">
      <ActionButtons type="dish" :id="dish.id" />
    </footer>
  </article>
</template>
