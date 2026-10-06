#!/usr/bin/env python3
"""批量流水线：切分故事文本 → 对齐AI说话人标注 → edge-tts叙述 → 拼接角色音频
用法:
  python3 scripts/assemble_story.py story_022 --list-dials
  python3 scripts/assemble_story.py story_022 --assemble
对话音频约定: public/assets/tmp/{story_id}/dial_{i:02d}.wav (i=对话序号)
non_speech 对话自动用叙述音色(edge-tts Xiaoxiao)生成。
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.load(open(ROOT / 'src/data/stories.json'))
ROLES = json.load(open(ROOT / 'src/data/dialogue_roles.json'))
VOICE_MAP = json.load(open(ROOT / 'scripts/voice_map.json'))
NARR_VOICE = 'zh-CN-XiaoxiaoNeural'

def story_text(sid):
    s = next(x for x in DATA if x['id'] == sid)
    return s

def split_segments(text):
    parts = re.split(r'(“.*?”)', text, flags=re.S)
    segs = []
    for p in parts:
        if not p.strip():
            continue
        if p.startswith('“') and p.endswith('”'):
            segs.append({'type': 'dial', 'text': p[1:-1]})
        else:
            segs.append({'type': 'narr', 'text': p})
    return segs

def dial_roles(sid):
    return ROLES.get(sid, {}).get('dials', [])

def list_dials(sid):
    s = story_text(sid)
    segs = split_segments(s['text'])
    dials = [x for x in segs if x['type'] == 'dial']
    anno = dial_roles(sid)
    print(f"# {sid} {s['title']} | 总段数={len(segs)} 对话数={len(dials)} 标注数={len(anno)}")
    for i, d in enumerate(dials):
        role = anno[i]['role'] if i < len(anno) else '?'
        spk = anno[i]['speaker'] if i < len(anno) else '?'
        print(f"{i}\t{role}\t{spk}\t{d['text']}")

def assemble(sid):
    s = story_text(sid)
    segs = split_segments(s['text'])
    anno = dial_roles(sid)
    dials = [x for x in segs if x['type'] == 'dial']
    if len(dials) != len(anno):
        print(f"WARN 对话数不匹配: 文本{len(dials)} vs 标注{len(anno)}")
    tmp = ROOT / 'public/assets/tmp' / sid
    tmp.mkdir(parents=True, exist_ok=True)
    narr_dir = tmp / 'narr'
    narr_dir.mkdir(exist_ok=True)

    # 1) 生成叙述段(edge-tts)
    narr_k = 0
    order = []
    for i, seg in enumerate(segs):
        if seg['type'] == 'narr':
            out = narr_dir / f'narr_{narr_k:02d}.mp3'
            if not out.exists():
                r = subprocess.run(['edge-tts', '--voice', NARR_VOICE, '--text', seg['text'],
                                    '--write-media', str(out)], capture_output=True)
                if r.returncode != 0:
                    print(f"narr {narr_k} FAIL", r.stderr[:120])
            order.append(str(out))
            narr_k += 1
        else:
            di = len([x for x in segs[:i] if x['type'] == 'dial'])
            role = anno[di]['role'] if di < len(anno) else 'non_speech'
            if role == 'non_speech':
                out = narr_dir / f'non_{di:02d}.mp3'
                if not out.exists():
                    subprocess.run(['edge-tts', '--voice', NARR_VOICE, '--text', seg['text'] + '。',
                                    '--write-media', str(out)], capture_output=True)
                order.append(str(out))
            else:
                f = tmp / f'dial_{di:02d}.wav'
                if not f.exists():
                    print(f"MISSING dial {di}: {f}")
                    return False
                order.append(str(f))
    # 2) 统一转码 + 拼接
    norm = tmp / 'norm'
    norm.mkdir(exist_ok=True)
    for idx, f in enumerate(order):
        out = norm / f'seg_{idx:03d}.mp3'
        if not out.exists():
            subprocess.run(['ffmpeg', '-y', '-i', f, '-ar', '44100', '-ac', '2', '-b:a', '128k', str(out)],
                           capture_output=True)
    lst = tmp / 'list.txt'
    lst.write_text('\n'.join(f"file '{norm / ('seg_%03d.mp3' % i)}'" for i in range(len(order))))
    outfile = ROOT / 'public/assets/audio' / f'{sid}.mp3'
    r = subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst),
                        '-c:a', 'libmp3lame', '-b:a', '128k', str(outfile)], capture_output=True)
    if r.returncode != 0:
        print("concat FAIL", r.stderr[-200:])
        return False
    dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=noprint_wrappers=1:nokey=1', str(outfile)],
                         capture_output=True, text=True).stdout.strip()
    print(f"{sid} OK -> {outfile} 时长={dur}s 段数={len(order)}")
    return True

if __name__ == '__main__':
    sid = sys.argv[1]
    if '--list-dials' in sys.argv:
        list_dials(sid)
    elif '--assemble' in sys.argv:
        assemble(sid)
