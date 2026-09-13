import type { ModuleMeta } from '@/types'

/** 模块颜色字面量映射（确保 Tailwind JIT 能扫描到完整类名） */
export interface ColorSet {
  /** 顶部栏/底色 */
  bg: string
  bgSoft: string
  /** 主题文字色 */
  text: string
  textDeep: string
  /** 渐变起止 */
  gradFrom: string
  gradTo: string
  /** 描边 */
  border: string
}

export const COLOR_MAP: Record<string, ColorSet> = {
  eat: {
    bg: 'bg-eat-soft',
    bgSoft: 'bg-eat-soft',
    text: 'text-eat',
    textDeep: 'text-eat-deep',
    gradFrom: 'from-eat',
    gradTo: 'to-eat-soft',
    border: 'border-eat',
  },
  learn: {
    bg: 'bg-learn-soft',
    bgSoft: 'bg-learn-soft',
    text: 'text-learn',
    textDeep: 'text-learn-deep',
    gradFrom: 'from-learn',
    gradTo: 'to-learn-soft',
    border: 'border-learn',
  },
  story: {
    bg: 'bg-story-soft',
    bgSoft: 'bg-story-soft',
    text: 'text-story',
    textDeep: 'text-story-deep',
    gradFrom: 'from-story',
    gradTo: 'to-story-soft',
    border: 'border-story',
  },
  play: {
    bg: 'bg-play-soft',
    bgSoft: 'bg-play-soft',
    text: 'text-play',
    textDeep: 'text-play-deep',
    gradFrom: 'from-play',
    gradTo: 'to-play-soft',
    border: 'border-play',
  },
  coral: {
    bg: 'bg-coral-soft',
    bgSoft: 'bg-coral-soft',
    text: 'text-coral',
    textDeep: 'text-coral',
    gradFrom: 'from-coral',
    gradTo: 'to-coral-soft',
    border: 'border-coral',
  },
  cream: {
    bg: 'bg-cream-200',
    bgSoft: 'bg-cream-200',
    text: 'text-ink',
    textDeep: 'text-ink',
    gradFrom: 'from-cream-200',
    gradTo: 'to-cream',
    border: 'border-cream-200',
  },
}

export function colors(key: string): ColorSet {
  return COLOR_MAP[key] || COLOR_MAP.cream
}

export type { ModuleMeta }
