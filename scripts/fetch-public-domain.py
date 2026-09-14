#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取 Project Gutenberg 中文公版原著全文，清洗页眉页脚后存到 src/data/raw/。
- 源为 Project Gutenberg（权威公版书库），gutenberg.org 国内外均可访问。
- 幂等：文件已存在且非空则跳过；--force 强制重新抓取。
- 失败详情写入 src/data/raw/_fetch-log.txt（便于在 Action 中排查）。
- 用法：python3 scripts/fetch-public-domain.py [--force] [--book xiyouji|sanguoyanyi|...]
"""
import argparse
import json
import pathlib
import re
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "src" / "data" / "raw"

UA = "ParentChildCards-SourceFetcher/1.0 (public domain texts)"
TIMEOUT = 90
MAX_RETRY = 4

# 书目清单：Gutenberg 中文公版书
# 只收白话底稿（文言古籍已删除——不适合小学生，见需求文档 10.2）
CATALOG = [
    {"key": "xiyouji", "name": "西游记", "gid": 23962},
]


def download(url: str) -> str:
    """流式下载并返回文本（UTF-8）。失败抛异常。"""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for _ in range(MAX_RETRY):
        try:
            chunks = []
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                while True:
                    chunk = resp.read(131072)
                    if not chunk:
                        break
                    chunks.append(chunk)
            data = b"".join(chunks)
            for enc in ("utf-8", "gb18030"):
                try:
                    return data.decode(enc)
                except UnicodeDecodeError:
                    continue
            return data.decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3)
    raise RuntimeError(f"下载失败 {url}: {type(last).__name__}: {last}")


def clean_gutenberg(text: str) -> str:
    """去掉 Gutenberg 页眉页脚声明，保留正文。"""
    t = text
    # 页脚：END OF THE PROJECT GUTENBERG EBOOK 之后全部去掉
    m = re.search(r"\*\*\*\s*END OF THE PROJECT GUTENBERG EBOOK", t)
    if m:
        t = t[: m.start()]
    # 页眉：START OF THE PROJECT GUTENBERG EBOOK 之前全部去掉
    m = re.search(r"\*\*\*\s*START OF THE PROJECT GUTENBERG EBOOK", t)
    if m:
        t = t[m.end() :]
    lines = [ln.strip() for ln in t.splitlines()]
    out = []
    for ln in lines:
        if not ln:
            continue
        out.append(ln)
    return "\n".join(out).strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--book", default="", help="只抓指定书（key）")
    args = ap.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    index = {}
    total_ok, total_fail = 0, 0
    log = [f"# fetch-public-domain 运行日志 {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"]

    for book in CATALOG:
        if args.book and book["key"] not in args.book:
            continue
        key = book["key"]
        out_dir = RAW_DIR / key
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "full.txt"
        if not args.force and out_file.exists() and out_file.stat().st_size > 0:
            size = out_file.stat().st_size
            print(f"  • {book['name']} 已存在（{size//1024}KB），跳过")
            total_ok += 1
            index[key] = {
                "name": book["name"],
                "gid": book["gid"],
                "size_bytes": size,
                "source": f"https://www.gutenberg.org/ebooks/{book['gid']}",
            }
            continue
        url = f"https://www.gutenberg.org/cache/epub/{book['gid']}/pg{book['gid']}.txt"
        try:
            raw = download(url)
            text = clean_gutenberg(raw)
            if len(text) < 1000:
                raise RuntimeError(f"清洗后内容过短（{len(text)} 字），可能是页眉页脚识别失败")
            out_file.write_text(text, encoding="utf-8")
            size = out_file.stat().st_size
            chars = len(text)
            total_ok += 1
            print(f"  ✓ {book['name']} → {out_file.relative_to(ROOT)} ({chars}字, {size//1024}KB)")
            index[key] = {
                "name": book["name"],
                "gid": book["gid"],
                "chars": chars,
                "size_bytes": size,
                "source": f"https://www.gutenberg.org/ebooks/{book['gid']}",
            }
        except Exception as e:  # noqa: BLE001
            total_fail += 1
            msg = f"{type(e).__name__}: {e}"
            log.append(f"FAIL {book['name']} (gid {book['gid']}) → {msg}")
            print(f"  ✗ {book['name']} 失败：{msg}")
        time.sleep(1)

    (RAW_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (RAW_DIR / "_fetch-log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"\n[fetch] 完成：成功 {total_ok} 本，失败 {total_fail} 本")
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
