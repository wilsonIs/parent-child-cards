#!/usr/bin/env python3
"""并行下载豆包配音 wav 到 public/assets/tmp/dial/。用法: python3 scripts/dl_batch.py <json-file>"""
import json, pathlib, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

dl = json.load(open(sys.argv[1]))
dial_out = pathlib.Path('public/assets/tmp/dial')
dial_out.mkdir(parents=True, exist_ok=True)

jobs = []
for short, mp in dl.items():
    for di, token in mp.items():
        jobs.append((short, di, token))

def one(job):
    short, di, token = job
    p = dial_out / f's{short}_d{int(di):02d}.wav'
    r = subprocess.run(['curl','-sL','--noproxy','*','-o',str(p),'https://aka.doubaocdn.com/s/'+token],
                       capture_output=True, timeout=90)
    if r.returncode == 0 and p.exists() and p.stat().st_size > 20000:
        return (short, di, True)
    return (short, di, False)

with ThreadPoolExecutor(max_workers=20) as ex:
    results = list(ex.map(one, jobs))
ok = sum(1 for r in results if r[2])
fail = [r[:2] for r in results if not r[2]]
print(f'downloaded {ok} failed {len(fail)} {fail}', flush=True)
