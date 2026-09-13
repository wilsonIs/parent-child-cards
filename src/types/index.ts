// 通用数据类型定义

export type ItemType = 'dish' | 'story' | 'game' | 'learn' | 'poem'

/** 吃 - 菜谱 */
export interface Dish {
  id: string
  type: 'dish'
  name: string
  image?: string
  icon: string
  tags: string[]
  age: string
  meal: string[]
  ingredients: string[]
  steps: string[]
  tips?: string
  source?: string
  license?: string
}

/** 故事 */
export interface Story {
  id: string
  type: 'story'
  title: string
  cover?: string
  icon: string
  category: string[]
  age: string
  duration: string
  text: string
  audio?: string
  source?: string
  license?: string
  /** 所属系列（如 西游记/格林童话）；无则为单篇 */
  series?: string
}

/** 玩 - 亲子游戏 */
export interface Game {
  id: string
  type: 'game'
  title: string
  icon: string
  scenes: string[]
  types: string[]
  age: string
  people: string
  time: string
  materials: string[]
  rules: string[]
  tips?: string
  source?: string
  license?: string
}

/** 学 - 学习资源 */
export interface Learn {
  id: string
  type: 'learn'
  title: string
  subject: string
  grade: string
  resourceType: string
  url: string
  source?: string
  license?: string
  description?: string
}

/** 学 - 古诗 / 蒙学（chinese-poetry 开源数据集自动同步） */
export interface Poem {
  id: string
  type: 'poem'
  title: string
  author: string
  category: '唐诗' | '宋词' | '诗经' | '楚辞' | '蒙学'
  grade: string // 学龄前 / 一年级…六年级 / 拓展
  paragraphs: string[]
  source?: string
  license?: string
}

/** 收藏 / 今日清单条目 */
export interface SavedItem {
  type: ItemType
  id: string
  addedAt: number
}

/** 用户偏好 */
export interface Settings {
  playbackRate: number // 故事语速 0.5~1.5
  fontSize: 'normal' | 'large'
  /** 孩子年级（用于古诗等内容的默认过滤）：全部/学龄前/一年级…六年级 */
  childGrade: string
}

/** 浏览习惯记录 */
export interface HistoryItem {
  type: ItemType
  id: string
  viewedAt: number
}

/** 模块元信息 */
export interface ModuleMeta {
  key: string
  title: string
  subtitle: string
  icon: string
  to: string
  colorClass: string
}
