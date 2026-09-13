#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习资源扩充：删除国外资源（GeoGebra/PhET/Khan/英国文化协会/SuperSimple/
Scratch/BBC/Storyline/可汗学院/熊猫博士），全部替换为已实测可访问的中国
权威资源，总数 40 → 60。URL 均已用 curl 验证可访问。
"""
import json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATH = ROOT / "src" / "data" / "learn.json"

# 待删除的国外资源（按标题匹配）
REMOVE_TITLES = {
    "GeoGebra · 数学互动课堂",
    "PhET · 数学与科学模拟",
    "Khan Academy Kids · 数学启蒙",
    "Khan Academy Kids · 英语阅读",
    "LearnEnglish Kids",
    "Super Simple Songs · 英文儿歌",
    "Scratch · 少儿编程",
    "BBC Learning English",
    "Storyline Online",
    "可汗学院",
    "熊猫博士",
}

NEW = [
    ("中国科学院", "科学", "https://www.cas.cn/", "国家科研机构官网，科学资讯与前沿动态"),
    ("中国科技馆", "科学", "https://www.cstm.org.cn/", "国家级科技馆，常设展览与科普活动"),
    ("中国载人航天工程网", "科学", "https://www.cmse.gov.cn/", "官方航天工程，航天知识与发射直播"),
    ("中国航天科技集团", "科学", "https://www.spacechina.com/", "航天科普与火箭发射资讯"),
    ("中国国家博物馆", "历史", "https://www.chnmuseum.cn/", "云端看国宝，历史与艺术课堂"),
    ("北京天文馆", "科学", "https://www.bjp.org.cn/", "仰望星空，天文科普与球幕影院"),
    ("中国丝绸博物馆", "历史", "https://www.chinasilkmuseum.com/", "丝绸文化与中国服饰史"),
    ("三星堆博物馆", "历史", "https://www.sxd.cn/", "古蜀文明探秘"),
    ("秦始皇帝陵博物院", "历史", "https://www.bmy.com.cn/", "兵马俑与秦文化"),
    ("河南博物院", "历史", "https://www.chnmus.net/", "华夏文明寻宝，文物云展览"),
    ("南京博物院", "历史", "https://www.njmuseum.com/", "六朝古都的文物宝库"),
    ("上海博物馆", "历史", "https://www.shanghaimuseum.net/", "青铜器与书画珍藏"),
    ("陕西历史博物馆", "历史", "https://www.sxhm.com/", "周秦汉唐历史长廊"),
    ("广东省博物馆", "历史", "https://www.gdmuseum.com/", "岭南文化博物馆"),
    ("中少在线", "阅读", "https://www.ccppg.com.cn/", "中国少年儿童新闻出版总社官方阅读平台"),
    ("未来网", "阅读", "https://www.k618.cn/", "共青团中央少年儿童门户，少先队资讯"),
    ("中国青年网·少年", "阅读", "https://www.youth.cn/", "面向青少年的新闻与成长内容"),
    ("中国文明网·未成年人", "道法", "https://www.wenming.cn/", "未成年人思想道德建设专题"),
    ("国家体育总局·青少年体育", "体育", "https://www.sport.gov.cn/", "青少年体质与运动指导"),
    ("中国教育电视台", "全科", "http://www.cetv.cn/", "教育节目与《同上一堂课》"),
    ("中国大学MOOC", "全科", "https://www.icourse163.org/", "国家精品在线开放课程"),
    ("学堂在线", "全科", "https://www.xuetangx.com/", "教育部在线教育研究中心平台"),
    ("国家高等教育智慧教育平台", "全科", "https://higher.smartedu.cn/", "国家高等教育课程平台"),
    ("中国国家地理", "地理", "https://www.dili360.com/", "中国地理、自然与人文科普"),
    ("中国电子学会·青少年科创", "科学", "https://www.cie.org.cn/", "青少年编程与机器人等级认证"),
    ("国家大剧院·古典音乐频道", "艺术", "https://www.chncpa.org/", "音乐、舞蹈、戏剧艺术欣赏"),
    ("中央音乐学院", "艺术", "https://www.ccom.edu.cn/", "中国最高音乐学府，音乐知识"),
    ("外研社·少儿英语", "英语", "https://www.fltrp.com/", "中国专业外语出版机构"),
    ("中国日报双语新闻", "英语", "https://language.chinadaily.com.cn/", "中英双语阅读素材"),
    ("中国大百科全书（第三版）", "全科", "https://www.zgbk.com/", "国家级百科全书在线版"),
    ("人民教育出版社", "全科", "https://www.pep.com.cn/", "中小学教材与配套课程资源"),
]

learn = json.loads(PATH.read_text(encoding="utf-8"))
kept = [x for x in learn if x["title"] not in REMOVE_TITLES]
removed = len(learn) - len(kept)

for i, (title, subject, url, desc) in enumerate(NEW, start=1):
    kept.append(dict(id=f"learn_{i:03d}", type="learn", title=title, subject=subject,
                     grade="全年级", resourceType="网站", url=url,
                     source=title, license="官方免费", description=desc))

# 重新连续编号
for i, x in enumerate(kept, start=1):
    x["id"] = f"learn_{i:03d}"

PATH.write_text(json.dumps(kept, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"删除国外资源 {removed} 条，共 {len(kept)} 条")
print("国外残留:", [x['title'] for x in kept if 'khan' in x['url'].lower() or 'bbc' in x['url'].lower() or 'colorado' in x['url'].lower() or 'britishcouncil' in x['url'].lower() or 'scratch.mit' in x['url'].lower() or 'supersimple' in x['url'].lower() or 'geogebra' in x['url'].lower() or 'storylineonline' in x['url'].lower() or 'drpanda' in x['url'].lower()])
