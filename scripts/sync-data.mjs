#!/usr/bin/env node
/**
 * 亲子卡片箱 · 数据同步脚本
 *
 * 数据源：chinese-poetry 开源数据集（MIT 许可，古籍原文均为公共领域）
 *   https://github.com/chinese-poetry/chinese-poetry
 *   蒙学目录：唐诗三百首 + 三字经 / 百家姓 / 千字文 / 弟子规 / 声律启蒙
 *
 * 职责：
 *  1. 拉取唐诗三百首与蒙学经典 → 简繁转换 → 生成 src/data/poems.json
 *  2. 校验现有四份数据（dishes / stories / games / learn）：
 *     id 唯一、必填字段、故事音频文件存在
 *  3. 输出校验报告；发现问题时非零退出（供 CI 拦截）
 *
 * 用法：node scripts/sync-data.mjs
 */

import { readFile, writeFile, access } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import * as OpenCC from 'opencc-js'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const DATA_DIR = path.join(ROOT, 'src', 'data')

const RAW_BASE =
  'https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master/蒙学'
const RAW_SHIJING =
  'https://raw.githubusercontent.com/chinese-poetry/chinese-poetry/master/诗经/shijing.json'

const MENGXUE_LIST = [
  { file: 'sanzijing-new.json', title: '三字经', author: '王应麟' },
  { file: 'baijiaxing.json', title: '百家姓', author: '佚名' },
  { file: 'qianziwen.json', title: '千字文', author: '周兴嗣' },
  { file: 'dizigui.json', title: '弟子规', author: '李毓秀' },
  { file: 'shenglvqimeng.json', title: '声律启蒙', author: '车万育' },
]

/**
 * 小学必背古诗年级映射（对照部编版教材，仅收录唐诗三百首中存在的篇目）。
 * 未收录的唐诗默认为「拓展」；蒙学经典为「学龄前」；诗经为「拓展」。
 */
const TANG_GRADE = {
  静夜思: '一年级',
  悯农: '一年级',
  古朗月行: '一年级',
  风: '一年级',
  登鹳雀楼: '二年级',
  咏柳: '二年级',
  赋得古原草送别: '二年级',
  绝句: '二年级',
  山行: '三年级',
  望天门山: '三年级',
  早发白帝城: '三年级',
  九月九日忆山东兄弟: '三年级',
  清明: '三年级',
  滁州西涧: '三年级',
  大林寺桃花: '三年级',
  鹿柴: '四年级',
  暮江吟: '四年级',
  嫦娥: '四年级',
  出塞: '四年级',
  凉州词: '四年级',
  别董大: '四年级',
  芙蓉楼送辛渐: '四年级',
  塞下曲: '四年级',
  枫桥夜泊: '五年级',
  山居秋暝: '五年级',
  鸟鸣涧: '五年级',
  游子吟: '五年级',
  从军行: '五年级',
  黄鹤楼送孟浩然之广陵: '五年级',
  春夜喜雨: '六年级',
  马诗: '六年级',
  早春呈水部张十八员外: '六年级',
}

/** 简体转换（源为繁体） */
const converter = OpenCC.Converter({ from: 't', to: 'cn' })
const t = (s) => (typeof s === 'string' ? converter(s) : s)

let errors = 0
const fail = (msg) => {
  errors++
  console.error('  ✗', msg)
}

async function fetchJSON(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'parent-child-cards-sync/1.0' },
  })
  if (!res.ok) throw new Error(`HTTP ${res.status} ${url}`)
  return res.json()
}

/** 按体裁推定年级：五绝→三年级、七绝→四年级、五律→五年级、七律→六年级、乐府→拓展 */
function gradeByType(type) {
  const tt = t(type)
  if (tt.includes('五言绝句')) return '三年级'
  if (tt.includes('七言绝句')) return '四年级'
  if (tt.includes('五言律诗')) return '五年级'
  if (tt.includes('七言律诗')) return '六年级'
  return '拓展'
}

/** 1. 拉取并生成 poems.json（幂等，全量重写） */
async function syncPoems() {
  const poems = []
  let seq = 0

  const tang = await fetchJSON(`${RAW_BASE}/tangshisanbaishou.json`)
  for (const section of tang.content || []) {
    for (const p of section.content || []) {
      seq++
      const title = t(p.chapter) || '无题'
      poems.push({
        id: `poem_${String(seq).padStart(3, '0')}`,
        type: 'poem',
        title,
        author: t(p.author) || '佚名',
        category: '唐诗',
        grade: TANG_GRADE[title] || gradeByType(section.type),
        paragraphs: (p.paragraphs || []).map(t),
        source: 'chinese-poetry 开源数据集（古籍公共领域）',
        license: 'MIT 数据集 · 古籍公版',
      })
    }
  }

  for (const m of MENGXUE_LIST) {
    const j = await fetchJSON(`${RAW_BASE}/${m.file}`)
    seq++
    poems.push({
      id: `poem_${String(seq).padStart(3, '0')}`,
      type: 'poem',
      title: t(j.title || m.title),
      author: t(m.author),
      category: '蒙学',
      grade: '学龄前',
      paragraphs: (j.paragraphs || []).map(t),
      source: 'chinese-poetry 开源数据集（古籍公共领域）',
      license: 'MIT 数据集 · 古籍公版',
    })
  }

  // 诗经（305 篇，按国风/雅/颂分类）
  const shijing = await fetchJSON(RAW_SHIJING)
  for (const p of shijing || []) {
    seq++
    poems.push({
      id: `poem_${String(seq).padStart(3, '0')}`,
      type: 'poem',
      title: t(p.title) || '无题',
      author: '佚名',
      category: '诗经',
      grade: '拓展',
      paragraphs: (p.content || []).map(t),
      source: 'chinese-poetry 开源数据集（古籍公共领域）',
      license: 'MIT 数据集 · 古籍公版',
    })
  }

  await writeFile(
    path.join(DATA_DIR, 'poems.json'),
    JSON.stringify(poems, null, 2) + '\n',
  )
  return poems.length
}

/** 2. 校验现有数据 */
const REQUIRED = {
  dishes: ['id', 'type', 'name', 'icon'],
  stories: ['id', 'type', 'title', 'text'],
  games: ['id', 'type', 'title', 'rules'],
  learn: ['id', 'type', 'title', 'url'],
}

async function validateExisting() {
  for (const [file, fields] of Object.entries(REQUIRED)) {
    const data = JSON.parse(
      await readFile(path.join(DATA_DIR, `${file}.json`), 'utf8'),
    )
    const ids = new Set()
    let dup = 0
    let missing = 0
    for (const item of data) {
      if (ids.has(item.id)) {
        dup++
        fail(`${file}.json 重复 id: ${item.id}`)
      }
      ids.add(item.id)
      for (const f of fields) {
        if (item[f] === undefined || item[f] === null || item[f] === '') {
          missing++
          fail(`${file}.json ${item.id || '?'} 缺少必填字段 ${f}`)
        }
      }
    }
    console.log(
      `  ${file}.json: ${data.length} 条 | id 唯一 ✓ | 必填字段 ✓${dup ? ` | 重复 ${dup}` : ''}${missing ? ` | 缺字段 ${missing}` : ''}`,
    )
  }

  const stories = JSON.parse(
    await readFile(path.join(DATA_DIR, 'stories.json'), 'utf8'),
  )
  let audioMissing = 0
  for (const s of stories) {
    if (s.audio) {
      try {
        await access(path.join(ROOT, 'public', s.audio))
      } catch {
        audioMissing++
        fail(`故事音频缺失: ${s.audio}`)
      }
    }
  }
  console.log(
    `  stories 音频: ${stories.length - audioMissing}/${stories.length} 文件存在`,
  )
}

async function main() {
  console.log('[sync] 拉取 chinese-poetry 蒙学数据 …')
  try {
    const n = await syncPoems()
    console.log(`[sync] src/data/poems.json 已生成，共 ${n} 条`)
  } catch (e) {
    fail(`数据拉取失败: ${e.message}`)
  }

  console.log('[sync] 校验现有数据 …')
  try {
    await validateExisting()
  } catch (e) {
    fail(`校验执行失败: ${e.message}`)
  }

  if (errors > 0) {
    console.error(`[sync] 发现 ${errors} 个问题，请检查后重试`)
    process.exit(1)
  }
  console.log('[sync] 全部通过 ✓')
}

main()
