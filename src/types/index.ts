// 通用数据类型定义

export type ItemType = 'dish' | 'story' | 'game' | 'learn'

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
