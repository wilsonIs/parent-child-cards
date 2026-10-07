#!/usr/bin/env python3
"""并行拼接多章节有声剧。用法: python3 scripts/build_batch.py story_133 story_134 ..."""
import json, pathlib, subprocess, sys

ids = sys.argv[1:]
# 角色音色映射（与 build_drama.py 一致，用于校验 wav 是否齐全）
def run(short):
    r = subprocess.run(['python3','scripts/build_drama.py',short], capture_output=True, text=True, timeout=600)
    return (short, r.returncode, r.stdout.strip().splitlines()[-1:] if r.stdout else [], r.stderr.strip()[:300])

import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(run, s): s for s in ids}
    for f in concurrent.futures.as_completed(futs):
        short, rc, tail, err = f.result()
        print(f'{short} rc={rc} {tail} {err}', flush=True)
