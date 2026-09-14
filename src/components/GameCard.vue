<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { Game } from '@/types'
import { useSettingsStore } from '@/stores/settings'
import ActionButtons from './ActionButtons.vue'

const props = defineProps<{ game: Game }>()
const settings = useSettingsStore()
const expand = ref(false)

function toggle() {
  expand.value = !expand.value
}

onMounted(() => {
  settings.recordView('game', props.game.id)
})
</script>

<template>
  <article class="snap-card flex h-full flex-col p-4">
    <div
      class="card-soft flex flex-1 flex-col overflow-y-auto"
      @click="toggle"
    >
      <div
        class="flex aspect-[5/3] items-center justify-center bg-gradient-to-b from-play to-play-deep"
      >
        <span class="text-8xl drop-shadow-sm">{{ game.icon }}</span>
      </div>

      <div class="flex flex-1 flex-col gap-3 p-5">
        <h2 class="text-2xl font-bold text-play-deep">{{ game.title }}</h2>

        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="s in game.scenes"
            :key="s"
            class="chip bg-play-soft text-play-deep"
          >{{ s }}</span>
        </div>

        <div class="flex flex-wrap gap-x-4 gap-y-1 text-sm text-ink-soft">
          <span>⏱ {{ game.time }}</span>
          <span>👥 {{ game.people }}</span>
          <span>🎯 {{ game.age }}</span>
        </div>

        <div class="flex flex-wrap gap-1.5">
          <span
            v-for="t in game.types"
            :key="t"
            class="chip chip-off"
          >{{ t }}</span>
        </div>

        <p class="mt-auto text-sm text-ink-muted">
          {{ expand ? '轻点收起 ▴' : '轻点查看规则 ▾' }}
        </p>

        <div
          v-if="expand"
          class="fade-up flex flex-col gap-4 border-t border-cream-200 pt-4"
        >
          <section>
            <h3 class="mb-2 font-semibold text-ink">玩法规则</h3>
            <ol class="list-decimal space-y-1.5 pl-5 text-sm text-ink-soft marker:text-play-deep">
              <li v-for="(r, i) in game.rules" :key="i">{{ r }}</li>
            </ol>
          </section>
          <section>
            <h3 class="mb-1 font-semibold text-ink">材料</h3>
            <p class="text-sm text-ink-soft">
              {{ game.materials.length ? game.materials.join('、') : '无需材料' }}
            </p>
          </section>
          <section v-if="game.tips">
            <h3 class="mb-1 font-semibold text-ink">小贴士</h3>
            <p class="text-sm text-ink-soft">{{ game.tips }}</p>
          </section>
        </div>
      </div>
    </div>

    <div class="flex justify-center py-3">
      <ActionButtons type="game" :id="game.id" />
    </div>
  </article>
</template>
