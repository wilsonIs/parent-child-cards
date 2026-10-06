# -*- coding: utf-8 -*-
"""将 idioms_1/idioms_2 的成语故事合并入库（去重），分配 story_196+ 新 id。"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from idioms_1 import IDIOMS_1
from idioms_2 import IDIOMS_2

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data" / "stories.json"
TTSCFG = {"voice": "narr:zh-CN-XiaoxiaoNeural/dial:zh-CN-XiaoyiNeural",
          "pitch": "narr:+0Hz/dial:+8Hz", "rate": "narr:+0%/dial:+4%"}

def duration_of(text: str) -> str:
    n = len(text)
    if n >= 800:
        return "5分钟"
    if n >= 600:
        return "4分钟"
    return "3分钟"

def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    existing = {s["title"] for s in data}
    existing_series = {s.get("series", "") for s in data}

    # 已有 id 数字
    max_num = max(int(s["id"].split("_")[1]) for s in data)
    next_num = max_num + 1

    added, skipped = [], []
    seen = set()
    for title, icon, text in IDIOMS_1 + IDIOMS_2:
        if title in existing or title in seen:
            skipped.append(title)
            continue
        seen.add(title)
        entry = {
            "id": f"story_{next_num}",
            "type": "story",
            "title": title,
            "cover": "assets/covers/themed/idiom.jpg",
            "icon": icon,
            "category": ["成语"],
            "age": "6岁+",
            "duration": duration_of(text),
            "text": text,
            "audio": f"assets/audio/story_{next_num}.mp3",
            "source": "公共领域改写",
            "license": "公共领域",
            "series": "成语故事",
            "source_url": "",
            "tts": TTSCFG,
            "copyright_status": "public_domain",
            "audio_channel": "tts",
        }
        data.append(entry)
        added.append((entry["id"], title))
        next_num += 1

    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"新增 {len(added)} 条（story_196 ~ story_{next_num-1}）")
    print(f"跳过重复 {len(skipped)} 条: {skipped[:30]}")
    print("新增列表:")
    for sid, t in added:
        print(" ", sid, t)
    print(f"现在总数: {len(data)}")

if __name__ == "__main__":
    main()
