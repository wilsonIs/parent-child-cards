#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取维基文库（zh.wikisource.org）公版原著原文，清洗后存到 src/data/raw/。
- 本脚本设计在 GitHub Actions 上运行（GitHub 海外服务器可访问维基文库，不受墙影响）；
  本地（国内网络）直接运行会超时失败，属预期。
- 幂等：文件已存在且非空则跳过；--force 强制重新抓取。
- 用法：python3 scripts/fetch-public-domain.py [--force] [--limit N]
"""
import argparse
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "src" / "data" / "raw"

API = "https://zh.wikisource.org/w/api.php"
UA = "ParentChildCards-SourceFetcher/1.0 (public domain texts; contact: repo owner)"
TIMEOUT = 30
MAX_RETRY = 2


def cn_num(n: int) -> str:
    """阿拉伯数字 → 中文数字（第一、第二…第一百）"""
    digits = "零一二三四五六七八九"
    if n < 10:
        return digits[n]
    if n < 20:
        return "十" + (digits[n % 10] if n % 10 else "")
    if n < 100:
        s = digits[n // 10] + "十"
        return s + (digits[n % 10] if n % 10 else "")
    if n < 110:
        return "一百" + (digits[n % 10] if n % 10 else "")
    return "一百" + (cn_num(n - 100) if n > 100 else "")


def fetch_wikitext(page: str) -> str:
    """通过 MediaWiki API 获取页面 wikitext 原文。失败抛异常。"""
    params = urllib.parse.urlencode(
        {
            "action": "parse",
            "page": page,
            "prop": "wikitext",
            "format": "json",
            "formatversion": "2",
        }
    )
    url = f"{API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "parse" not in data:
        err = data.get("error", {})
        raise RuntimeError(
            f"API error {err.get('code')}: {err.get('info')} (page: {page})"
        )
    return data["parse"]["wikitext"]


def clean_wikitext(raw: str) -> str:
    """去除模板/注释/内部链接/编辑标记，保留正文。"""
    t = raw
    # 注释
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    # 模板（含嵌套）
    while "{{" in t:
        new = re.sub(r"\{\{[^{}]*\}\}", "", t)
        if new == t:
            break
        t = new
    # <ref> 脚注及其内容
    t = re.sub(r"<ref[^>]*/>", "", t)
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    # 其余 html 标签保留内部文字（如 <br>、<poem>）
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"</?poem[^>]*>", "", t)
    # 内部链接 [[目标|显示]] → 显示；[[目标]] → 目标
    t = re.sub(r"\[\[([^|\]]*)\|([^\]]*)\]\]", r"\2", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    # 清理残留标记
    t = re.sub(r"[\u00a0\u200b]", " ", t)
    lines = [ln.strip() for ln in t.splitlines()]
    out = []
    for ln in lines:
        if not ln:
            continue
        if ln.startswith("==") and ln.endswith("=="):
            out.append(ln.strip("= "))  # 保留小标题（章节名）
            out.append("")
            continue
        out.append(ln)
    text = "\n".join(out).strip()
    return text + "\n"


# 书目清单：key / 名称 / 页面列表（按顺序尝试，先简体后繁体）
CATALOG = [
    {
        "key": "xiyouji",
        "name": "西游记",
        "pages": [
            ["西游记/第{cn}回", "西遊記/第{cn}回"] for cn in [cn_num(i) for i in range(1, 101)]
        ],
    },
    {
        "key": "sanguoyanyi",
        "name": "三国演义",
        "pages": [
            ["三国演义/第{cn}回", "三國演義/第{cn}回"] for cn in [cn_num(i) for i in range(1, 121)]
        ],
    },
    {
        "key": "shuihuzhuan",
        "name": "水浒传",
        "pages": [
            ["水浒传/第{cn}回", "水滸傳/第{cn}回"] for cn in [cn_num(i) for i in range(1, 101)]
        ],
    },
    {
        "key": "fengshenyanyi",
        "name": "封神演义",
        "pages": [
            ["封神演义/第{cn}回", "封神演義/第{cn}回"] for cn in [cn_num(i) for i in range(1, 101)]
        ],
    },
    {
        "key": "hongloumeng",
        "name": "红楼梦",
        "pages": [
            ["红楼梦/第{cn}回", "紅樓夢/第{cn}回"] for cn in [cn_num(i) for i in range(1, 121)]
        ],
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="强制重新抓取已存在文件")
    ap.add_argument("--limit", type=int, default=0, help="每个书目最多抓取前 N 页（调试用）")
    args = ap.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    index = {}
    total_ok, total_fail = 0, 0
    log_lines = [f"# fetch-public-domain 运行日志 {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"]
    log_lines.append(f"# 成功 {0} 页起步；书目: " + ", ".join(b["name"] for b in CATALOG))

    for book in CATALOG:
        key = book["key"]
        out_dir = RAW_DIR / key
        out_dir.mkdir(parents=True, exist_ok=True)
        pages = book["pages"]
        if args.limit > 0:
            pages = pages[: args.limit]
        ok = 0
        fails = []
        for i, names in enumerate(pages, 1):
            out_file = out_dir / f"{i:03d}.txt"
            if not args.force and out_file.exists() and out_file.stat().st_size > 0:
                ok += 1
                continue
            text = None
            used = None
            last_err = ""
            for name in names:
                page = name.format(cn=cn_num(i)) if "{cn}" in name else name
                try:
                    raw = fetch_wikitext(page)
                    text = clean_wikitext(raw)
                    used = page
                    break
                except Exception as e:  # noqa: BLE001
                    last_err = f"{type(e).__name__}: {e}"
                    time.sleep(0.5)
            if text is None or not text.strip():
                fails.append((i, names[0], last_err))
                log_lines.append(f"FAIL {book['name']} #{i} 尝试页名 {names[0]} → {last_err}")
                continue
            out_file.write_text(text, encoding="utf-8")
            ok += 1
            total_ok += 1
            print(f"  ✓ {book['name']} 第{i}页 → {out_file.relative_to(ROOT)} ({len(text)}字)")
            time.sleep(0.3)
        total_fail += len(fails)
        if fails:
            print(f"  ✗ {book['name']} 失败 {len(fails)} 页（前 5 个）：")
            for f in fails[:5]:
                print(f"    - 第{f[0]}页 {f[1]}: {f[2][:120]}")
        index[key] = {
            "name": book["name"],
            "count": ok,
            "dir": f"src/data/raw/{key}",
            "source": f"https://zh.wikisource.org/wiki/{book['name']}",
        }

    (RAW_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (RAW_DIR / "_fetch-log.txt").write_text(
        "\n".join(log_lines) + "\n", encoding="utf-8"
    )
    print(f"\n[fetch] 完成：成功 {total_ok} 页，失败 {total_fail} 页（详情见 src/data/raw/_fetch-log.txt）")
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
