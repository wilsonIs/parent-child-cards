#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 poems.json 中的古诗/蒙学批量生成朗读音频（Edge TTS）。

- 播报文本 = 诗名 + 朝代 + 诗人 + 正文
  （朝代由分类推导：唐诗→唐代、宋词→宋代、诗经→先秦、楚辞→战国、蒙学按篇目细分）
- 语音：zh-CN-XiaoxiaoNeural（温柔女声，适合儿童）
- 输出到 public/assets/audio/poem_XXX.mp3，并写回 poems.json 的 audio 字段
- 已存在且非空的音频自动跳过（幂等）

用法：
  python3 scripts/tts-poems.py                 # 全量（跳过已有）
  python3 scripts/tts-poems.py poem_001        # 指定单条
  python3 scripts/tts-poems.py --force         # 强制重生成
  python3 scripts/tts-poems.py --limit 20      # 只生成前 N 条（测试）
"""
import argparse
import asyncio
import json
import pathlib
import sys

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data" / "poems.json"
AUDIO_DIR = ROOT / "public" / "assets" / "audio"

VOICE = "zh-CN-XiaoxiaoNeural"  # 温柔女声
RATE = "-25%"  # 放慢语速，方便儿童跟读

# 蒙学经典按篇目细分朝代
MENGXUE_DYNASTY = {
    "三字经": "宋代",
    "百家姓": "宋代",
    "千字文": "南朝",
    "弟子规": "清代",
    "声律启蒙": "清代",
}


def dynasty_of(item):
    """按分类推导朝代（蒙学经典细分为具体朝代）。"""
    cat = item.get("category")
    if cat == "唐诗":
        return "唐代"
    if cat == "宋词":
        return "宋代"
    if cat == "诗经":
        return "先秦"
    if cat == "楚辞":
        return "战国"
    if cat == "蒙学":
        title = item.get("title") or ""
        for key, dyn in MENGXUE_DYNASTY.items():
            if key in title:
                return dyn
    return "古代"


def speak_text(item):
    title = (item.get("title") or "").strip()
    author = (item.get("author") or "").strip()
    body = "".join(p for p in (item.get("paragraphs") or [])).strip()
    head = "{}，{}，{}。".format(title, dynasty_of(item), author or "佚名")
    return head + body if body else head


async def gen_one(item, text, out_path):
    tts = edge_tts.Communicate(text, voice=VOICE, rate=RATE)
    try:
        await tts.save(str(out_path))
        return out_path.exists() and out_path.stat().st_size > 0
    except Exception as e:  # noqa: BLE001
        print("  ✗ {} 生成失败: {}".format(item["id"], e), file=sys.stderr)
        return False


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="只处理指定 poem id")
    ap.add_argument("--force", action="store_true", help="强制重生成（默认跳过已有）")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 条")
    args = ap.parse_args()

    items = json.loads(DATA.read_text(encoding="utf-8"))
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    todo = []
    for it in items:
        if args.ids and it["id"] not in args.ids:
            continue
        audio = "assets/audio/{}.mp3".format(it["id"])
        out = ROOT / "public" / audio
        it["audio"] = audio
        if not args.force and out.exists() and out.stat().st_size > 0:
            continue
        todo.append((it, speak_text(it), out))
    if args.limit:
        todo = todo[: args.limit]

    DATA.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not todo:
        print("[tts-poems] 全部音频已存在，无需生成 ✓")
        return 0

    print("[tts-poems] 待生成 {} 条 | 语音 {}（诗名+朝代+诗人+正文）".format(len(todo), VOICE))
    ok = 0
    for i, (it, text, out) in enumerate(todo, 1):
        if await gen_one(it, text, out):
            size = out.stat().st_size
            print("  [{}/{}] {} → {} ({}KB)".format(i, len(todo), it["id"], out.name, size // 1024), flush=True)
            ok += 1
        await asyncio.sleep(0.3)

    if ok < len(todo):
        print("[tts-poems] 成功 {}/{}，有失败，请重试".format(ok, len(todo)), file=sys.stderr)
        return 1
    print("[tts-poems] 全部完成 ✓（{} 条）".format(ok))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))