#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去重：同一首歌的多个版本，只保留最原始版或纯钢琴版
基于人工核对的31组，排除 Komorebi (不同歌曲) 和 The King (不同歌曲)
"""
import os, json, subprocess

WS = os.path.expanduser("~/workspace")
MUSIC = os.path.join(WS, "music")

subprocess.run(["node", "-e",
    "const fs=require('fs'); eval(fs.readFileSync('music-data.js','utf-8').replace('window.musicData','__D__'));"
    "fs.writeFileSync('/tmp/music.json', JSON.stringify(__D__));"], cwd=WS, check=True)
items = json.load(open('/tmp/music.json', encoding='utf-8'))

# 明确指定的删除列表：(保留的id, [删除的id])
# 规则：保留原始版或纯钢琴版
delete_map = {
    5: [603],      # 演员
    6: [647],      # 诀别书
    7: [501],      # 反乌托邦
    11: [478],     # 你从未离去
    12: [487],     # 兰亭序
    15: [648],     # 说了再见
    22: [586],     # 最后一页
    23: [406],     # The King (保留最后攻势)
    37: [510],     # 听妈妈的话
    45: [581],     # 晴天
    46: [557],     # 情绪回收站
    48: [669],     # 青花瓷
    50: [651],     # 起风了
    51: [458],     # 七里香
    52: [642],     # 蒲公英的约定
    54: [483],     # 偏爱
    68: [624],     # 精卫
    77: [637],     # 花海
    79: [596],     # 海阔天空
    84: [502],     # 反方向的钟
    87: [565],     # 打上花火
    91: [546],     # 弥渡山歌
    111: [278, 279], # His Theme
    126: [575],    # 春娇与志明
    197: [198, 199], # Bad Apple
    301: [302],    # Lifeline
    313: [315],    # Megalovania
    331: [330, 332], # NIGHT DANCER (保留纯钢琴)
    396: [395],    # Sunburst (保留日冕)
    426: [422, 423, 424, 425], # UnwelcomeSchool (保留纯钢琴版)
}

delete_ids = set()
delete_files = []
for keeper_id, del_ids in delete_map.items():
    delete_ids.update(del_ids)

# 构建 id->item 映射
item_map = {it['id']: it for it in items}

for del_id in sorted(delete_ids):
    if del_id in item_map:
        it = item_map[del_id]
        fname = os.path.basename(it['downloadUrl'])
        delete_files.append(fname)
        print(f"删除: id {del_id} | {it['title']} | {fname}")

# 删除文件
for f in delete_files:
    p = os.path.join(MUSIC, f)
    if os.path.exists(p):
        os.remove(p)
        print(f"  已删除文件: {f}")

# 重写 music-data.js
kept = [it for it in items if it['id'] not in delete_ids]
out = ['window.musicData = [']
for it in kept:
    out.append('    {')
    out.append(f'        id: {it["id"]},')
    out.append(f'        title: "{it["title"]}",')
    out.append(f'        author: "{it["author"]}",')
    out.append(f'        size: "{it["size"]}",')
    out.append(f'        date: "{it["date"]}",')
    out.append(f'        downloadUrl: "{it["downloadUrl"]}"')
    out.append('    },')
out[-1] = out[-1].rstrip(',')
out.append('];')
open(os.path.join(WS, 'music-data.js'), 'w', encoding='utf-8').write('\n'.join(out))

print(f"\n原条目: {len(items)} | 删除: {len(delete_ids)} | 剩余: {len(kept)}")
