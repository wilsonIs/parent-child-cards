#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 stories.json 中缺失音频的故事批量生成 mp3（Edge TTS）。
- 已存在音频文件的故事自动跳过（幂等）
- 用法：python3 scripts/tts.py
- CI 中配合 GitHub Action 定时运行，新增故事自动生成音频
"""
import asyncio
import json
import pathlib
import sys

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data" / "stories.json"
AUDIO_DIR = ROOT / "public" / "assets" / "audio"

VOICE = "zh-CN-XiaoxiaoNeural"  # 温柔女声，适合故事
RATE = "+0%"  # 语速适中


async def gen_one(story_id: str, text: str, out_path: pathlib.Path) -> bool:
    tts = edge_tts.Communicate(text, voice=VOICE, rate=RATE)
    try:
        await tts.save(str(out_path))
        return True
    except Exception as e:  # noqa: BLE001
        print(f"  ✗ {story_id} 生成失败: {e}", file=sys.stderr)
        return False


async def main() -> int:
    stories = json.loads(DATA.read_text(encoding="utf-8"))
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    todo = []
    for s in stories:
        audio = s.get("audio", "")
        if not audio:
            print(f"  ⚠ {s['id']} 无 audio 字段，跳过")
            continue
        out = ROOT / "public" / audio
        if out.exists() and out.stat().st_size > 0:
            continue  # 已存在，跳过
        todo.append((s["id"], s["text"], out))

    if not todo:
        print(f"[tts] 全部 {len(stories)} 个故事已有音频，无需生成 ✓")
        return 0

    print(f"[tts] 待生成 {len(todo)} 个音频，语音 {VOICE} …")
    ok = 0
    for i, (sid, text, out) in enumerate(todo, 1):
        if await gen_one(sid, text, out):
            size = out.stat().st_size
            print(f"  [{i}/{len(todo)}] {sid} → {out.name} ({size//1024}KB)")
            ok += 1
        await asyncio.sleep(0.3)  # 避免请求过快

    if ok < len(todo):
        print(f"[tts] 成功 {ok}/{len(todo)}，有失败，请重试", file=sys.stderr)
        return 1
    print(f"[tts] 全部完成 ✓（新增 {ok} 个音频）")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
