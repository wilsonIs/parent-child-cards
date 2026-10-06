#!/usr/bin/env python3
"""批量构建多角色有声剧：edge-tts 叙述（带超时重试）+ 豆包AI对话 + ffmpeg 拼接。"""
import json, pathlib, subprocess, sys, time

def edge_tts(text, out, voice='zh-CN-XiaoxiaoNeural', retries=5, timeout=90):
    """edge-tts with per-call timeout + retries"""
    for attempt in range(retries):
        try:
            r = subprocess.run(['edge-tts','--text',text,'--voice',voice,'--write-media',str(out)],
                               capture_output=True, timeout=timeout)
            if r.returncode == 0 and out.exists() and out.stat().st_size > 1000:
                return True
        except subprocess.TimeoutExpired:
            pass
        # cleanup partial file
        if out.exists():
            try: out.unlink()
            except Exception: pass
        time.sleep(2)
    return False

def edge_tts_file(txtfile, out, voice='zh-CN-XiaoxiaoNeural', retries=5, timeout=90):
    for attempt in range(retries):
        try:
            r = subprocess.run(['edge-tts','--voice',voice,'--file',str(txtfile),'--write-media',str(out)],
                               capture_output=True, timeout=timeout)
            if r.returncode == 0 and out.exists() and out.stat().st_size > 1000:
                return True
        except subprocess.TimeoutExpired:
            pass
        if out.exists():
            try: out.unlink()
            except Exception: pass
        time.sleep(2)
    return False

def main(short, alts=None):
    sid = 'story_' + short
    segs = json.load(open(f'/tmp/{sid}_segs.json'))
    tmp = pathlib.Path('public/assets/tmp').resolve()
    narr_out = tmp/'narr'
    dial_out = tmp/'dial'
    norm = tmp/'norm'
    narr_out.mkdir(exist_ok=True); dial_out.mkdir(exist_ok=True); norm.mkdir(exist_ok=True)

    # 1. narr segments via edge-tts (file mode) — 用顺序索引命名，与 order 一致
    narr_idx = 0
    for i, s in enumerate(segs):
        if s['type']=='narr':
            txtf = narr_out/f's{short}_n{narr_idx:02d}.txt'
            txtf.write_text(s['text'])
            mp3 = narr_out/f's{short}_n{narr_idx:02d}.mp3'
            if not edge_tts_file(txtf, mp3):
                print(short, 'NARR_FAIL', i); sys.exit(2)
            narr_idx += 1

    # 2. special alt segments (non_speech) via edge-tts text mode
    for di, txt in (alts or {}).items():
        mp3 = narr_out/f's{short}_alt{di}.mp3'
        if not edge_tts(txt, mp3):
            print(short, 'ALT_FAIL', di); sys.exit(2)

    # 3. build order
    order = []
    narr_k = 0
    for i, s in enumerate(segs):
        if s['type']=='narr':
            order.append(narr_out/f's{short}_n{narr_k:02d}.mp3'); narr_k += 1
        else:
            dial_i = len([x for x in segs[:i] if x['type']=='dial'])
            alt = narr_out/f's{short}_alt{dial_i}.mp3'
            if alt.exists(): order.append(alt)
            else: order.append(dial_out/f's{short}_d{dial_i:02d}.wav')

    # 4. normalize all segments with unique prefix
    for idx, f in enumerate(order):
        out = norm/f'seg_{short}_{idx:03d}.mp3'
        r = subprocess.run(['ffmpeg','-y','-i',str(f),'-ar','44100','-ac','2','-b:a','128k',str(out)],
                           capture_output=True, timeout=120)
        if r.returncode != 0:
            print(short, 'NORM_FAIL', idx, f); sys.exit(2)

    # 5. concat
    lst = tmp/f'list{short}.txt'
    lst.write_text('\n'.join(f"file '{norm/f'seg_{short}_{i:03d}.mp3'}'" for i in range(len(order))))
    out_mp3 = f'public/assets/audio/{sid}.mp3'
    r = subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c:a','libmp3lame','-b:a','128k',out_mp3],
                       capture_output=True, timeout=180)
    if r.returncode != 0:
        print(short, 'CONCAT_FAIL'); sys.exit(2)
    print(short, 'OK segs:', len(order))

if __name__ == '__main__':
    alts_map = {
        '003': {0:'扑通。',5:'扑通。'},
        '004': {4:'亡羊补牢。'},
        '006': {4:'狐假虎威。'},
        '034': {4:'自相矛盾。'},
        '035': {2:'嘣——。'},
        '037': {4:'轰隆。'},
        '109': {5:'杞人忧天。'},
        '113': {0:'哗哗。',4:'庖丁解牛。',5:'游刃有余。'},
        '022': {4:'花果山福地，水帘洞洞天。'},
        '067': {15:'白骨夫人。'},
        '068': {6:'仙丹。'},
        '070': {10:'砍头。',12:'长！',13:'剖腹。',14:'下油锅。'},
        '074': {1:'一秤金。',4:'咔嚓。'},
        '077': {7:'人种袋。'},
        '078': {3:'滋溜。'},
        '079': {4:'晒经石。',5:'真经。'},
    }
    main(sys.argv[1], alts_map.get(sys.argv[1], {}))
