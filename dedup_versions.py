#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去重：同一首歌的多个版本，只保留最原始版或钢琴版
规则：
- 如果有"纯钢琴"版，保留纯钢琴版
- 否则保留不带版本后缀的原始版
- 删除其他版本的文件和数据条目
"""
import os, json, subprocess, shutil, re

WS = os.path.expanduser("~/workspace")
MUSIC = os.path.join(WS, "music")

subprocess.run(["node", "-e",
    "const fs=require('fs'); eval(fs.readFileSync('music-data.js','utf-8').replace('window.musicData','__D__'));"
    "fs.writeFileSync('/tmp/music.json', JSON.stringify(__D__));"], cwd=WS, check=True)
items = json.load(open('/tmp/music.json', encoding='utf-8'))

# 按去掉括号后的基础名分组
def base_title(t):
    t = re.sub(r'（[^）]*）', '', t)
    t = re.sub(r'\([^)]*\)', '', t)
    return t.strip()

groups = {}
for it in items:
    b = base_title(it['title'])
    groups.setdefault(b, []).append(it)

# 判断是否是纯钢琴版
def is_piano(t):
    return '纯钢琴' in t or '纯钢琴版' in t

# 判断是否是原始版（没有版本后缀）
def is_original(t):
    # 去掉括号后如果和原标题一样，说明没有版本后缀
    return t == base_title(t)

to_delete = []  # 要删除的条目 id
to_delete_files = []  # 要删除的文件名

for base, group in groups.items():
    if len(group) <= 1:
        continue
    
    # 排序：优先保留纯钢琴版，其次保留原始版，其余删除
    def sort_key(it):
        t = it['title']
        if is_piano(t):
            return (0, it['id'])  # 纯钢琴版优先
        if is_original(t):
            return (1, it['id'])  # 原始版其次
        return (2, it['id'])  # 其他版本最后
    
    group.sort(key=sort_key)
    keeper = group[0]
    
    print(f"保留: id {keeper['id']} | {keeper['title']} | {keeper['author']}")
    
    for it in group[1:]:
        print(f"  删除: id {it['id']} | {it['title']} | {it['author']}")
        to_delete.append(it['id'])
        fname = os.path.basename(it['downloadUrl'])
        to_delete_files.append(fname)

# 删除文件
deleted_files = []
for f in to_delete_files:
    p = os.path.join(MUSIC, f)
    if os.path.exists(p):
        os.remove(p)
        deleted_files.append(f)
        print(f"  删除文件: {f}")

# 从数据中删除条目
kept = [it for it in items if it['id'] not in to_delete]

# 重写 music-data.js
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

print(f"\n=== 总结 ===")
print(f"原条目: {len(items)}")
print(f"删除条目: {len(to_delete)}")
print(f"删除文件: {len(deleted_files)}")
print(f"剩余条目: {len(kept)}")
