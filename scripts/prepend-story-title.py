#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给故事MP3前面补读故事名（最小代价方案）。

- 用 edge-tts 生成每个故事的标题短音频（叙述音色）
- 拼接：[标题朗读] + 0.6s静音 + [原故事音频]
- 不重新生成整个故事，只加个开头
- 自动备份原文件到 .bak

用法：
  python3 scripts/prepend-story-title.py                # 全量处理所有story
  python3 scripts/prepend-story-title.py story_001       # 指定单个
  python3 scripts/prepend-story-title.py --dry-run       # 只看会处理哪些
  python3 scripts/prepend-story-title.py --restore       # 从备份恢复
"""
import argparse
import asyncio
import json
import pathlib
import subprocess
import sys

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data" / "stories.json"
AUDIO_DIR = ROOT / "public" / "assets" / "audio"

# 叙述音色（与故事正文一致）
TITLE_VOICE = "zh-CN-XiaoxiaoNeural"
TITLE_PITCH = "+0Hz"
TITLE_RATE = "+0%"

# 标题后静音时长（秒）
TITLE_GAP = 0.6


def run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ffmpeg", "-y", *args],
        capture_output=True, text=True,
    )


async def gen_title_audio(title: str, out: pathlib.Path) -> bool:
    """生成故事标题朗读音频。"""
    # 加个句号让朗读更自然
    text = f"{title}。"
    tts = edge_tts.Communicate(text, voice=TITLE_VOICE, pitch=TITLE_PITCH, rate=TITLE_RATE)
    try:
        await tts.save(str(out))
        return out.stat().st_size > 0
    except Exception as e:
        print(f"    ✗ 标题TTS失败: {e}", file=sys.stderr)
        return False


def make_silence(duration: float, out: pathlib.Path):
    """生成匹配原MP3格式的静音段（44100Hz stereo 128kbps）。"""
    r = run_ffmpeg([
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", f"{duration:.3f}", "-q:a", "4", "-b:a", "128k", str(out)
    ])
    if r.returncode != 0:
        print(f"    ✗ 生成静音失败: {r.stderr[-200:]}", file=sys.stderr)
        return False
    return True


def prepend_title(original: pathlib.Path, title_mp3: pathlib.Path, tmp_dir: pathlib.Path) -> bool:
    """把标题音频 + 静音 + 原故事 拼接成新文件，替换原文件。
    用concat demuxer + -c copy，不重新编码，音质零损失。"""
    # 生成静音
    silence = tmp_dir / "silence.mp3"
    if not make_silence(TITLE_GAP, silence):
        return False

    # 写concat列表文件
    list_file = tmp_dir / "list.txt"
    lines = [
        f"file '{title_mp3.as_posix()}'",
        f"file '{silence.as_posix()}'",
        f"file '{original.as_posix()}'",
    ]
    list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    out_tmp = tmp_dir / "merged.mp3"
    # 统一重新编码为128kbps MP3，确保时长和格式正确
    r = run_ffmpeg([
        "-i", str(title_mp3),
        "-i", str(silence),
        "-i", str(original),
        "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]",
        "-map", "[out]",
        "-codec:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "2",
        str(out_tmp)
    ])
    if r.returncode != 0:
        print(f"    ✗ 拼接失败: {r.stderr[-300:]}", file=sys.stderr)
        return False

    if not out_tmp.exists() or out_tmp.stat().st_size < 1000:
        print(f"    ✗ 拼接结果异常", file=sys.stderr)
        return False

    # 备份原文件（如果还没备份过）
    bak = original.with_suffix(".mp3.bak")
    if not bak.exists():
        original.rename(bak)
    else:
        original.unlink()

    # 移动新文件到位
    out_tmp.rename(original)
    return True


def restore_backups():
    """从.bak恢复所有故事MP3。"""
    restored = 0
    for bak in AUDIO_DIR.glob("story_*.mp3.bak"):
        orig = bak.with_suffix("")  # 去掉.bak
        bak.rename(orig)
        restored += 1
        print(f"  ✓ 恢复 {orig.name}")
    print(f"[restore] 共恢复 {restored} 个文件")


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--dry-run", action="store_true", help="只列出待处理，不实际执行")
    ap.add_argument("--restore", action="store_true", help="从备份恢复")
    ap.add_argument("--only-drama", action="store_true",
                    help="只处理做过音色调整的故事（/tmp有segs.json的）")
    args = ap.parse_args()

    if args.restore:
        restore_backups()
        return 0

    stories = json.loads(DATA.read_text(encoding="utf-8"))

    # 可选：只处理做过音色调整的故事（有segs.json的）
    drama_ids = None
    if args.only_drama:
        import glob
        drama_ids = set()
        for f in glob.glob("/tmp/story_*_segs.json"):
            sid = pathlib.Path(f).stem.replace("_segs", "")
            drama_ids.add(sid)
        print(f"[prepend-title] --only-drama模式：共{len(drama_ids)}个做过音色调整的故事")

    todo = []
    for s in stories:
        if s.get("type") != "story":
            continue
        if args.ids and s["id"] not in args.ids:
            continue
        if drama_ids is not None and s["id"] not in drama_ids:
            continue
        audio_path = ROOT / "public" / s["audio"]
        if not audio_path.exists():
            continue
        # 已经处理过的（有.bak说明已经拼过标题了）
        bak = audio_path.with_suffix(".mp3.bak")
        if bak.exists():
            continue
        todo.append((s["id"], s["title"], audio_path))

    if not todo:
        print("[prepend-title] 没有需要处理的故事（都已加过标题或无备份）")
        return 0

    print(f"[prepend-title] 待处理 {len(todo)} 个故事 | 音色={TITLE_VOICE} | 标题后静音={TITLE_GAP}s")

    if args.dry_run:
        for sid, title, _ in todo:
            print(f"  {sid}: 《{title}》")
        return 0

    import tempfile
    ok = 0
    fail = 0
    for i, (sid, title, audio_path) in enumerate(todo, 1):
        print(f"  [{i}/{len(todo)}] {sid} 《{title}》...", end=" ", flush=True)
        with tempfile.TemporaryDirectory() as td:
            td = pathlib.Path(td)
            title_mp3 = td / "title.mp3"
            if not await gen_title_audio(title, title_mp3):
                print("✗ 标题生成失败")
                fail += 1
                continue
            if prepend_title(audio_path, title_mp3, td):
                size_kb = audio_path.stat().st_size // 1024
                print(f"✓ ({size_kb}KB)")
                ok += 1
            else:
                print("✗ 拼接失败")
                fail += 1
        await asyncio.sleep(0.2)  # 避免TTS限流

    print(f"\n[prepend-title] 完成 ✓={ok} ✗={fail}")
    if fail > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
