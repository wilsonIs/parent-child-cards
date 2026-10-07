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

    # 5. concat（concat demuxer + copy 封装，libmp3lame 重编码在拼接流上有已知 bug）
    n = len(order)
    lst = tmp / f'list{short}.txt'
    lst.write_text('\n'.join(f"file '{norm / f'seg_{short}_{i:03d}.mp3'}'" for i in range(n)))
    out_mp3 = f'public/assets/audio/{sid}.mp3'
    r = subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy',out_mp3],
                       capture_output=True, timeout=300)
    if r.returncode != 0:
        print(short, 'CONCAT_FAIL'); sys.exit(2)
    print(short, 'OK segs:', n)

if __name__ == '__main__':
    alts_map = {
        '003': {0:'扑通。',5:'扑通。'},
        '004': {4:'亡羊补牢。'},
        '006': {4:'狐假虎威。'},
        '034': {4:'自相矛盾。'},
        '035': {2:'嘣——。',5:'惊弓之鸟。'},
        '037': {4:'轰隆。',5:'画龙点睛。'},
        '109': {5:'杞人忧天。'},
        '113': {0:'哗哗。',4:'庖丁解牛。',5:'游刃有余。'},
        '111': {5:'歧路亡羊。'},
        '114': {0:'邯郸学步。'},
        '115': {2:'望洋兴叹。'},
        '259': {0:'明修栈道，暗度陈仓。'},
        '260': {1:'洛阳纸贵。'},
        '261': {0:'江郎。',2:'江郎才尽。'},
        '262': {2:'才高八斗。'},
        '263': {3:'东山再起。'},
        '264': {0:'精忠报国。',3:'精忠报国。',5:'精忠报国。'},
        '265': {4:'马革裹尸。',5:'马革裹尸。'},
        '266': {3:'投笔从戎。'},
        '267': {6:'张良拾履。'},
        '268': {2:'雪中送炭。'},
        '269': {1:'锲而不舍。'},
        '270': {4:'毛遂自荐。'},
        '271': {2:'一字千金。'},
        '272': {1:'口若悬河。'},
        '273': {1:'一叶知秋。',2:'一叶知秋。'},
        '274': {3:'未雨绸缪。'},
        '275': {1:'防微杜渐。'},
        '276': {1:'文景之治。',2:'前车之鉴。'},
        '277': {0:'吁——',7:'螳臂当车。'},
        '278': {2:'朝三暮四。'},
        '244': {0:'囊萤夜读。'},
        '245': {0:'映雪读书。'},
        '246': {4:'开卷有益。'},
        '247': {4:'手不释卷。'},
        '248': {2:'咔嚓。',5:'半途而废。'},
        '249': {9:'三人成虎。'},
        '250': {5:'曾子杀猪。'},
        '251': {2:'一饭千金。'},
        '252': {3:'胯下之辱。'},
        '253': {6:'退避三舍。'},
        '254': {6:'唇亡齿寒。'},
        '255': {8:'三令五申。'},
        '256': {5:'田忌赛马。'},
        '257': {3:'约法三章。'},
        '258': {2:'兔死狗烹。'},
        '218': {2:'鹬蚌相争，渔翁得利。'},
        '223': {2:'围魏救赵。'},
        '225': {2:'破釜沉舟。'},
        '228': {2:'七步成诗。'},
        '232': {2:'老马识途。'},
        '235': {1:'草木皆兵。'},
        '236': {2:'风声鹤唳。'},
        '239': {2:'闻鸡起舞。'},
        '240': {2:'中流击楫。'},
        '241': {1:'东施效颦。'},
        '242': {0:'工匠祖师。',4:'班门弄斧。'},
        '243': {4:'画饼充饥。'},
        '001': {0:'咚。'},
        '002': {0:'咣。',1:'咣、咣、咣。'},
        '032': {0:'呱呱。'},
        '038': {0:'咔嚓咔嚓。',1:'对牛弹琴。'},
        '039': {2:'叶公好龙。'},
        '040': {1:'梅子！',2:'望梅止渴。'},
        '204': {1:'专心致志。'},
        '205': {1:'卧薪尝胆。'},
        '206': {0:'头悬梁。',1:'锥刺股。',2:'悬梁刺股。'},
        '207': {0:'凿壁偷光。',1:'凿壁偷光。'},
        '211': {1:'胸有成竹。'},
        '222': {4:'纸上谈兵。'},
        '224': {3:'四面楚歌。'},
        '226': {4:'背水一战。'},
        '227': {4:'草船借箭。'},
        '229': {4:'对症下药。'},
        '230': {0:'嗖嗖嗖。',4:'百发百中。',5:'百发百中。'},
        '231': {2:'嗖。',5:'一箭双雕。'},
        '233': {5:'呆若木鸡。'},
        '234': {3:'按图索骥。'},
        '237': {0:'安乐公。',6:'乐不思蜀。'},
        '238': {7:'指鹿为马。'},
        '210': {6:'亚圣。',7:'孟母三迁。'},
        '212': {0:'嗖。',6:'熟能生巧。'},
        '213': {6:'水滴石穿。'},
        '214': {6:'塞翁失马。'},
        '215': {9:'南辕北辙。'},
        '216': {3:'买椟还珠。'},
        '217': {5:'郑人买履。'},
        '219': {4:'螳螂捕蝉，黄雀在后。'},
        '220': {0:'和氏璧。',5:'完璧归赵。'},
        '221': {4:'负荆请罪。'},
        '196': {2:'一鸣惊人。',3:'一鸣惊人。'},
        '197': {7:'一叶障目。'},
        '198': {3:'一诺千金。'},
        '199': {5:'一鼓作气。'},
        '200': {0:'书圣。',1:'墨池。',3:'入木三分。'},
        '201': {4:'三顾茅庐。'},
        '202': {9:'大公无私。'},
        '203': {4:'不耻下问。'},
        '208': {5:'程门立雪。'},
        '209': {4:'铁杵磨针。'},
        '022': {4:'花果山福地，水帘洞洞天。'},
        '067': {15:'白骨夫人。'},
        '068': {6:'仙丹。'},
        '070': {10:'砍头。',12:'长！',13:'剖腹。',14:'下油锅。'},
        '074': {1:'一秤金。',4:'咔嚓。'},
        '077': {7:'人种袋。'},
        '078': {3:'滋溜。'},
        '079': {4:'晒经石。',5:'真经。'},
        '182': {0:'哗啦。',1:'咕嘟咕嘟。'},
        '183': {0:'呼——。',1:'呜——。'},
        '184': {8:'唰！'},
        '185': {5:'哇！'},
        '186': {3:'咕噜咕噜。',7:'轰！'},
        '188': {0:'咯噔。',2:'唐僧！'},
        '189': {2:'咔嚓咔嚓。',8:'和尚！',12:'钦法国。'},
        '190': {2:'人头！'},
        '191': {6:'啪！',7:'轰隆隆——。'},
        '192': {5:'嗖——。'},
        '171': {0:'笨汉汉斯。',3:'嘿哟嘿哟。',14:'啪！',17:'笨汉汉斯。'},
        '172': {2:'咚咚咚。',12:'扑通。'},
        '014': {4:'外婆！'},
        '174': {0:'啪！',3:'一下打死七个！',5:'嗖。',7:'一下打死七个！'},
        '166': {0:'真正的好朋友，要分享一切。'},
        '167': {7:'轰！',9:'啪！'},
        '179': {5:'哗啦！',7:'鲤鱼跳龙门。',8:'龙门。'},
        '165': {1:'闲人莫入！'},
        '169': {2:'啪！'},
        '173': {0:'傻小子。',7:'扑哧。'},
        '088': {5:'啪！'},
        '176': {1:'日。',2:'月。',3:'山。',4:'水。',5:'字。',6:'造字圣人。'},
        '015': {2:'呼——。',3:'咔嚓。',4:'扑通。',5:'嗷嗷。'},
        '058': {4:'呼呼——。'},
        '095': {2:'新衣。'},
        '178': {1:'咔嚓。',4:'咔嚓！',5:'吴刚伐桂，砍了又生。'},
        '041': {0:'精卫！精卫！',3:'精卫填海。'},
    }
    main(sys.argv[1], alts_map.get(sys.argv[1], {}))
