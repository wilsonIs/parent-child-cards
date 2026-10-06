#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多角色配音 v3（Edge TTS 分角色音色拼接）。

- 叙述段 → zh-CN-XiaoxiaoNeural（自然女声旁白）
- 对话段 → 识别说话人 → 按角色分配音色：
    男角色(唐僧/国王/老爷爷…) → zh-CN-YunxiNeural（按角色微调 pitch）
    女角色(公主/仙女/母亲…)  → zh-CN-XiaoyiNeural（活泼）
    特别角色表（悟空/八戒/观音/妖怪…）→ 精确配置
    无说话人提示 → 默认活泼女声 Xiaoyi
- 每段独立生成 mp3，ffmpeg concat 拼接（段间 120ms 静音）

用法：
  python3 scripts/tts-v3.py story_067            # 指定故事
  python3 scripts/tts-v3.py --force              # 全量（跳过已有）
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
GAP_MS = 120

NARR = ("zh-CN-XiaoxiaoNeural", "+0Hz", "+0%")
DEFAULT_DIAL = ("zh-CN-XiaoyiNeural", "+8Hz", "+4%")

# 特别角色表：包含匹配 → (voice, pitch, rate)
SPECIAL = {
    "悟空": ("zh-CN-YunxiNeural", "+10Hz", "+2%"),
    "猴王": ("zh-CN-YunxiNeural", "+10Hz", "+2%"),
    "美猴王": ("zh-CN-YunxiNeural", "+10Hz", "+2%"),
    "唐僧": ("zh-CN-YunxiNeural", "+0Hz", "+0%"),
    "师父": ("zh-CN-YunxiNeural", "+0Hz", "+0%"),
    "三藏": ("zh-CN-YunxiNeural", "+0Hz", "+0%"),
    "八戒": ("zh-CN-YunxiNeural", "-8Hz", "-2%"),
    "沙僧": ("zh-CN-YunxiNeural", "-5Hz", "-1%"),
    "观音": ("zh-CN-XiaoxiaoNeural", "+0Hz", "-5%"),
    "菩萨": ("zh-CN-XiaoxiaoNeural", "+0Hz", "-5%"),
    "玉帝": ("zh-CN-YunxiNeural", "-5Hz", "-3%"),
    "如来": ("zh-CN-YunxiNeural", "-10Hz", "-5%"),
    "龙王": ("zh-CN-YunxiNeural", "-10Hz", "-5%"),
    "老龙王": ("zh-CN-YunxiNeural", "-12Hz", "-6%"),
    "阎王": ("zh-CN-YunxiNeural", "-12Hz", "-6%"),
    "仙女": ("zh-CN-XiaoyiNeural", "+12Hz", "+6%"),
    "王母": ("zh-CN-XiaoyiNeural", "+10Hz", "+4%"),
    "精": ("zh-CN-XiaoyiNeural", "+15Hz", "+6%"),
    "怪": ("zh-CN-XiaoyiNeural", "+15Hz", "+6%"),
}
# 通用性别/年龄段关键词（SPECIAL 之后匹配）
FEMALE_KEYS = ("女", "婆", "娘", "母", "姐", "妹", "姑", "公主", "娘娘", "太后",
               "王后", "皇后", "夫人", "小姐", "姑娘", "嫂子", "妈妈", "奶奶",
               "姥姥", "外婆", "嫦娥", "织女", "农妇")
MALE_KEYS = ("公", "父", "爷", "叔", "伯", "哥", "弟", "男", "王", "帝", "皇帝",
             "国王", "和尚", "道士", "将军", "老翁", "老农", "爷爷", "爸爸",
             "父亲", "儿子", "仙长", "祖师", "大汉", "农夫", "官", "将")
CHILD_KEYS = ("小孩", "孩子", "小童", "儿童", "娃娃", "孙子")

# 说话人提取：对话前 1-6 字内的提示语 "XXX(说道/问/喊…)："（组1 不允许标点）
SPEAK_RE = re.compile(r'([^“”\n，。！？、；：]{1,6}?)(?:说道|问道|喊道|答道|笑道|嚷道|叫道|'
                      r'叹道|气道|喝道|叮嘱|劝|说|问|喊|叫|答|嚷|笑|叹|骂|吼)'
                      r'[：:，,]?$')
# 对话文本（全角引号）
DIAL_RE = re.compile(r'“[^”]*”|"[^"]*"')


def extract_speaker(prefix: str) -> str | None:
    """从前置提示语提取说话人，无效返回 None。"""
    name = re.sub(r'[，。！？、；：: \s]', '', prefix)
    if not name or len(name) > 8:
        return None
    # 排除明显非说话人（以助词/状态词收尾的片段）
    if name[-1] in "的得地着了吗呢吧啊呀":
        return None
    if "着" in name or "了" in name:
        return None
    if name in ("他", "她", "它", "他们", "她们", "自己"):
        return None
    return name


def role_voice(name: str) -> tuple[str, str, str]:
    for key, cfg in SPECIAL.items():
        if key in name:
            return cfg
    if any(k in name for k in CHILD_KEYS):
        return ("zh-CN-XiaoyiNeural", "+20Hz", "+8%")
    if any(k in name for k in FEMALE_KEYS):
        return ("zh-CN-XiaoyiNeural", "+10Hz", "+5%")
    if any(k in name for k in MALE_KEYS):
        return ("zh-CN-YunxiNeural", "+0Hz", "+0%")
    return DEFAULT_DIAL


def split_text(text: str) -> list[tuple[str, str, str | None]]:
    """返回 [(kind, segment, speaker)]，kind ∈ narr/dial，speaker 仅 dial 有。"""
    segs: list[tuple[str, str, str | None]] = []
    pos = 0
    for m in DIAL_RE.finditer(text):
        if m.start() > pos:
            segs.append(("narr", text[pos:m.start()], None))
        # 找对话前的提示语
        prefix = text[max(0, m.start() - 14):m.start()]
        speaker = None
        pm = SPEAK_RE.search(prefix)
        if pm:
            speaker = extract_speaker(pm.group(1))
        segs.append(("dial", m.group(), speaker))
        pos = m.end()
    if pos < len(text):
        segs.append(("narr", text[pos:], None))
    # 合并相邻同类段
    merged: list[tuple[str, str, str | None]] = []
    for kind, seg, sp in segs:
        seg = seg.strip()
        if not seg:
            continue
        if merged and merged[-1][0] == kind:
            # 对话段相邻：说话人不同则不合并（保持角色音色独立）
            if kind == "narr" or (kind == "dial" and merged[-1][2] == sp):
                merged[-1] = (kind, merged[-1][1] + seg, merged[-1][2])
                continue
        merged.append((kind, seg, sp))
    return merged


async def gen_segment(kind: str, seg: str, speaker: str | None, out: pathlib.Path) -> bool:
    if kind == "narr":
        voice, pitch, rate = NARR
    else:
        voice, pitch, rate = role_voice(speaker or "")
    tts = edge_tts.Communicate(seg, voice=voice, pitch=pitch, rate=rate)
    try:
        await tts.save(str(out))
        return out.stat().st_size > 0
    except Exception as e:  # noqa: BLE001
        print(f"    ✗ {kind}/{speaker} 失败: {e}", file=sys.stderr)
        return False


def concat_mp3(parts: list[pathlib.Path], out: pathlib.Path) -> bool:
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
                gap = td / f"g{i}.mp3"
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                     "-t", f"{GAP_MS/1000:.3f}", "-q:a", "9", str(gap)],
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
            print(f"    ✗ concat: {r.stderr[-200:]}", file=sys.stderr)
            return False
    return out.exists() and out.stat().st_size > 0


async def gen_story(sid: str, text: str, out: pathlib.Path, verbose=False) -> bool:
    segs = split_text(text)
    if not segs:
        return False
    if verbose:
        for kind, seg, sp in segs:
            v = role_voice(sp or "") if kind == "dial" else NARR[0]
            label = f"{v.split('-')[-1][:-7]}" if kind == "dial" else "叙述"
            print(f"    [{label:>4}] {sp or ''} | {seg[:26]}…")
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        parts = []
        for i, (kind, seg, sp) in enumerate(segs, 1):
            part = td / f"{i:03d}.mp3"
            if not await gen_segment(kind, seg, sp, part):
                return False
            parts.append(part)
            await asyncio.sleep(0.25)
        return concat_mp3(parts, out)


async def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
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
        todo = todo[:args.limit]

    if not todo:
        print("[tts-v3] 无需生成（--force 强制重生成）")
        return 0
    print(f"[tts-v3] 生成 {len(todo)} 条 | 叙述={NARR[0]} 多角色对话")
    ok = 0
    for i, (sid, text, out) in enumerate(todo, 1):
        if await gen_story(sid, text, out, verbose=args.verbose):
            print(f"  [{i}/{len(todo)}] ✓ {sid} ({out.stat().st_size//1024}KB)")
            ok += 1
        else:
            print(f"  [{i}/{len(todo)}] ✗ {sid}", file=sys.stderr)
        await asyncio.sleep(0.3)
    if ok < len(todo):
        return 1
    print(f"[tts-v3] 全部完成 ✓（{ok} 条）")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
