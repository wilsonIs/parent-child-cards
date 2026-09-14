#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
西游记故事完整版升级：把 300-500 字浓缩版替换为基于 Project Gutenberg 原文
改写的中长篇完整版（1800-2500 字，约 8-12 分钟音频）。
每条标注来源回目，可追溯。
用法：python3 scripts/upgrade-xiyouji.py   （更新 stories.json 的 text/duration/source）
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from xyj_texts import XYG  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
STORIES = ROOT / "src" / "data" / "stories.json"
AUDIO_DIR = ROOT / "public" / "assets" / "audio"

# id -> (回目说明, 完整版文本)

def main() -> None:
    data = json.loads(STORIES.read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in data}
    done = []
    for sid, (chap, text) in XYG.items():
        if sid not in by_id:
            print(f"!! 未找到 {sid}")
            continue
        s = by_id[sid]
        s["text"] = text
        s["duration"] = "12分钟" if len(text) > 2200 else "10分钟"
        s["source"] = f"《西游记》{chap}（Project Gutenberg 原文改写）"
        s["license"] = "公共领域"
        done.append(sid)
    STORIES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已更新 {len(done)} 条: {done}")

    # 重新生成音频
    if "--audio" in sys.argv:
        voice = "zh-CN-XiaoyiNeural"  # 活泼儿童向女声（晓伊+35Hz音调+10%语速）
        for sid in done:
            s = by_id[sid]
            out = AUDIO_DIR / f"{sid}.mp3"
            subprocess.run(
                ["edge-tts", "--voice", voice, "--pitch=+35Hz", "--rate=+10%", "--text", s["text"], "--write-media", str(out)],
                check=True,
                capture_output=True,
            )
            print(f"音频已生成: {out.name} ({len(s['text'])}字)")


if __name__ == "__main__":
    main()
