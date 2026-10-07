#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 learn.json 中的「学什么」知识卡批量生成朗读音频（Edge TTS）。

- 播报文本 = 标题 + 内容（包含标题，满足“包含标题”的播放需求）
- 语音：zh-CN-XiaoxiaoNeural（温柔女声，适合儿童）
- 输出到 public/assets/audio/learn_XXX.mp3，并把 audio 字段写回 learn.json
- 已存在且非空的音频自动跳过（幂等）

用法：
  python3 scripts/tts-learn.py                 # 全量（跳过已有）
  python3 scripts/tts-learn.py learn_001       # 指定单条
  python3 scripts/tts-learn.py --force         # 强制重生成
"""
import argparse
import asyncio
import json
import pathlib
import sys

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data" / "learn.json"
AUDIO_DIR = ROOT / "public" / "assets" / "audio"

VOICE = "zh-CN-XiaoxiaoNeural"  # 温柔女声
RATE = "+0%"


def speak_text(item):
    """标题接内容，标题后以句号断开做自然停顿。"""
    title = (item.get("title") or "").strip()
    content = (item.get("content") or "").strip()
    if title and content:
        return title + "。" + content
    return title or content


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
    ap.add_argument("ids", nargs="*", help="只处理指定 learn id")
    ap.add_argument("--force", action="store_true", help="强制重生成（默认跳过已有）")
    args = ap.parse_args()

    items = json.loads(DATA.read_text(encoding="utf-8"))
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    todo = []
    for it in items:
        if args.ids and it["id"] not in args.ids:
            continue
        audio = "assets/audio/{}.mp3".format(it["id"])
        out = ROOT / "public" / audio
        # 无论是否重新生成，都写回 audio 字段保持一致
        it["audio"] = audio
        if not args.force and out.exists() and out.stat().st_size > 0:
            continue
        todo.append((it, speak_text(it), out, audio))

    # 无论是否生成，落盘 audio 字段保持一致
    DATA.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not todo:
        print("[tts-learn] 全部音频已存在，无需生成 ✓")
        return 0

    print("[tts-learn] 待生成 {} 条 | 语音 {}（含标题）".format(len(todo), VOICE))
    ok = 0
    for i, (it, text, out, _) in enumerate(todo, 1):
        if await gen_one(it, text, out):
            size = out.stat().st_size
            print("  [{}/{}] {} → {} ({}KB)".format(i, len(todo), it["id"], out.name, size // 1024))
            ok += 1
        await asyncio.sleep(0.3)

    if ok < len(todo):
        print("[tts-learn] 成功 {}/{}，有失败，请重试".format(ok, len(todo)), file=sys.stderr)
        return 1
    print("[tts-learn] 全部完成 ✓（{} 条）".format(ok))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))