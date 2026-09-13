import type { ModuleMeta } from '@/types'

/** 首页四大模块元信息 */
export const MODULES: ModuleMeta[] = [
  {
    key: 'eat',
    title: '吃',
    subtitle: '今天吃什么',
    icon: '🍚',
    to: '/eat',
    colorClass: 'eat',
  },
  {
    key: 'learn',
    title: '学',
    subtitle: '今天学什么',
    icon: '📚',
    to: '/learn',
    colorClass: 'learn',
  },
  {
    key: 'story',
    title: '故事',
    subtitle: '今天听什么',
    icon: '📖',
    to: '/story',
    colorClass: 'story',
  },
  {
    key: 'play',
    title: '玩',
    subtitle: '今天玩什么',
    icon: '🎲',
    to: '/play',
    colorClass: 'play',
  },
]

/** 玩模块 9 个场景 */
export const PLAY_SCENES = [
  { key: '家里', icon: '🏠', desc: '宅家也能玩' },
  { key: '户外', icon: '🌳', desc: '出去放电' },
  { key: '旅途', icon: '🚗', desc: '车上不无聊' },
  { key: '等待', icon: '⏳', desc: '排队等餐' },
  { key: '睡前', icon: '🛏', desc: '安静助眠' },
  { key: '聚会', icon: '👨‍👩‍👧', desc: '多人热闹' },
  { key: '公共场合', icon: '🛒', desc: '不大声' },
  { key: '雨天/室内', icon: '🌧', desc: '出不了门' },
  { key: '纯语言', icon: '🗣', desc: '动嘴不动手' },
]

/** 故事分类 */
export const STORY_CATEGORIES = [
  '全部',
  '成语',
  '寓言',
  '神话',
  '童话',
  '科普',
  '睡前',
  '名著',
  '英语',
  '历史',
  '民间',
]

/** 吃模块筛选 */
export const DISH_MEALS = ['全部', '早餐', '午餐', '晚餐', '加餐']
export const DISH_TYPES = ['全部', '快手', '汤', '主食', '荤菜', '素菜']

/** 学模块筛选 */
export const LEARN_SUBJECTS = [
  '全部',
  '语文',
  '数学',
  '英语',
  '科学',
  '古诗',
  '阅读',
]
export const LEARN_GRADES = [
  '全部',
  '一年级',
  '二年级',
  '三年级',
  '四年级',
  '五年级',
  '六年级',
]

/** 古诗年级筛选（含学龄前；与设置里的孩子年级一致） */
export const POEM_GRADES = [
  '全部',
  '学龄前',
  '一年级',
  '二年级',
  '三年级',
  '四年级',
  '五年级',
  '六年级',
]

/** 年级 → 数字（用于「起读年级 <= 用户年级」过滤；拓展按六年级计） */
export const GRADE_LEVEL: Record<string, number> = {
  学龄前: 0,
  一年级: 1,
  二年级: 2,
  三年级: 3,
  四年级: 4,
  五年级: 5,
  六年级: 6,
  拓展: 6,
}

/** 故事系列元数据（icon 与一句话简介） */
export const SERIES_META: Record<string, { icon: string; desc: string }> = {
  西游记: { icon: '🐒', desc: '取经路上降妖除魔的经典故事' },
  三国演义: { icon: '⚔️', desc: '群雄逐鹿的智慧与忠义' },
  一千零一夜: { icon: '🧞', desc: '阿拉伯的奇妙夜谭' },
  格林童话: { icon: '👸', desc: '德国经典童话集' },
  安徒生童话: { icon: '🦢', desc: '丹麦童话大师的经典作品' },
  伊索寓言: { icon: '🦊', desc: '小动物讲出的大道理' },
  成语故事: { icon: '📖', desc: '一条成语，一段来历' },
  中国神话: { icon: '🌌', desc: '盘古开天到夸父逐日' },
  民间传说: { icon: '🏮', desc: '流传千年的民间故事' },
}
