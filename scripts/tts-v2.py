#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 stories.json 生成角色化 mp3（Edge TTS 双音色拼接）。

方案（优化2+4）：
- 叙述段（引号外）→ zh-CN-XiaoxiaoNeural（自然深情的小说朗读女声，微软最自然中文音色）
- 对话段（引号内）→ zh-CN-XiaoyiNeural + pitch +8Hz（活泼轻快的儿童/对话感）
- 两段式交替拼接，形成"旁白自然 + 对话活泼"的抑扬顿挫层次
- 每段独立调用 edge-tts 生成 mp3，用 ffmpeg concat 无缝拼接（段间 120ms 静音间隙自然停顿）

用法：
  python3 scripts/tts-v2.py            # 全量重生成（--force）
  python3 scripts/tts-v2.py story_001  # 单条
  python3 scripts/tts-v2.py --force --limit 5   # 只重生成前 5 条（测试）
"""
import argparse
import asyncio
import json
import pathlib
import re
import subprocess
import sys
import tempfile

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data" / "stories.json"
AUDIO_DIR = ROOT / "public" / "assets" / "audio"

NARR_VOICE = "zh-CN-XiaoxiaoNeural"  # 叙述：自然深情
NARR_RATE = "+0%"
NARR_PITCH = "+0Hz"
DIAL_VOICE = "zh-CN-XiaoyiNeural"  # 对话：活泼
DIAL_RATE = "+4%"
DIAL_PITCH = "+8Hz"
GAP_MS = 120  # 段间静音间隔


def split_text(text: str):
    """按中文/英文引号把文本切成 (narr|dial, segment) 交替段，相邻同类合并。"""
    pattern = re.compile(r'“[^”]*”|"[^"]*"')
    segments: list[tuple[str, str]] = []
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            segments.append(("narr", text[pos:m.start()]))
        segments.append(("dial", m.group()))
        pos = m.end()
    if pos < len(text):
        segments.append(("narr", text[pos:]))
    merged: list[tuple[str, str]] = []
    for kind, seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if merged and merged[-1][0] == kind:
            merged[-1] = (kind, merged[-1][1] + seg)
        else:
            merged.append((kind, seg))
    return merged


async def gen_segment(kind: str, seg_text: str, out: pathlib.Path) -> bool:
    if kind == "dial":
        voice, rate, pitch = DIAL_VOICE, DIAL_RATE, DIAL_PITCH
    else:
        voice, rate, pitch = NARR_VOICE, NARR_RATE, NARR_PITCH
    tts = edge_tts.Communicate(seg_text, voice=voice, rate=rate, pitch=pitch)
    try:
        await tts.save(str(out))
        return out.stat().st_size > 0
    except Exception as e:  # noqa: BLE001
        print(f"    ✗ {kind} 段生成失败: {e}", file=sys.stderr)
        return False


def concat_mp3(parts: list[pathlib.Path], out: pathlib.Path) -> bool:
    """用 ffmpeg concat 拼接 mp3 片段，段间加静音间隙。"""
    if len(parts) == 1:
        parts[0].replace(out)
        return True
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        list_file = td / "list.txt"
        lines = []
        for i, part in enumerate(parts):
            lines.append(f"file '{part.as_posix()}'")
            if i < len(parts) - 1:
                gap = td / f"gap_{i}.mp3"
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono",
                     "-t", f"{GAP_MS / 1000:.3f}", "-q:a", "9", str(gap)],
                    capture_output=True, check=True,
                )
                lines.append(f"file '{gap.as_posix()}'")
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        r = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
             "-c", "copy", str(out)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"    ✗ concat 失败: {r.stderr[-300:]}", file=sys.stderr)
            return False
    return out.exists() and out.stat().st_size > 0


async def gen_story(sid: str, text: str, out: pathlib.Path) -> bool:
    segments = split_text(text)
    if not segments:
        print(f"  ✗ {sid} 文本为空", file=sys.stderr)
        return False
    n_dial = sum(1 for k, _ in segments if k == "dial")
    print(f"  · {sid}: {len(segments)} 段（对话 {n_dial}）")
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        parts: list[pathlib.Path] = []
        for i, (kind, seg) in enumerate(segments, 1):
            part = td / f"{i:03d}_{kind}.mp3"
            if not await gen_segment(kind, seg, part):
                return False
            parts.append(part)
            await asyncio.sleep(0.25)
        return concat_mp3(parts, out)


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="只处理指定 story id")
    ap.add_argument("--force", action="store_true", help="强制重生成（默认跳过已有）")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 条")
    args = ap.parse_args()

    stories = json.loads(DATA.read_text(encoding="utf-8"))
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    todo = []
    for s in stories:
        if args.ids and s["id"] not in args.ids:
            continue
        audio = s.get("audio", "")
        if not audio:
            continue
        out = ROOT / "public" / audio
        if not args.force and out.exists() and out.stat().st_size > 0:
            continue
        todo.append((s["id"], s["text"], out))
    if args.limit:
        todo = todo[: args.limit]

    if not todo:
        print("[tts-v2] 无需生成（全部已有音频，可用 --force 重生成）")
        return 0

    print(f"[tts-v2] 生成 {len(todo)} 条 | 叙述={NARR_VOICE} 对话={DIAL_VOICE}(+8Hz +4%)")
    ok = 0
    for i, (sid, text, out) in enumerate(todo, 1):
        if await gen_story(sid, text, out):
            size = out.stat().st_size
            dur = "?"
            try:
                r = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(out)],
                    capture_output=True, text=True,
                )
                dur = f"{float(r.stdout.strip()):.0f}s"
            except Exception:  # noqa: BLE001
                pass
            print(f"  [{i}/{len(todo)}] ✓ {sid} → {out.name} ({size // 1024}KB, {dur})")
            ok += 1
        else:
            print(f"  [{i}/{len(todo)}] ✗ {sid} 失败", file=sys.stderr)
        await asyncio.sleep(0.3)

    if ok < len(todo):
        print(f"[tts-v2] 成功 {ok}/{len(todo)}，有失败", file=sys.stderr)
        return 1
    print(f"[tts-v2] 全部完成 ✓（{ok} 条）")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
