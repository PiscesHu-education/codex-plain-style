#!/usr/bin/env python3
"""统计一份系统提示词的客观底数：总字数、模块分布、禁止句数量与密度。

用法：python3 eval/stats.py <提示词文件>

输出是线索不是判决：密度高不代表该删，要看规则属于哪一类。
见 skill/prompt-diagnose/SKILL.md 第三节。
"""
import re
import sys

if len(sys.argv) < 2:
    sys.exit("用法: python3 eval/stats.py <提示词文件>")

path = sys.argv[1]
t = open(path, encoding="utf-8").read()

EN_NEG = re.compile(r"\bdo not\b|\bdon't\b|\bnever\b|\bavoid\b|\bunless\b", re.I)
ZH_NEG = re.compile(r"不要|禁止|不得|不能|避免")
cjk = len(re.findall(r"[一-鿿]", t))
sents = len(re.findall(r"[.!?](?=\s|$)", t))

print(f"文件      {path}")
print(f"字符      {len(t)}")
print(f"行        {t.count(chr(10)) + 1}")
print(f"中文字    {cjk}")
print(f"英文句    {sents}")
print(f"列表项    {len(re.findall(r'^[ \t]*(?:[-*+]|[0-9]+[.)])[ \t]', t, re.M))}")
print(f"标题      {len(re.findall(r'^#{1,6} [^#]', t, re.M))}")
en_total = len(EN_NEG.findall(t))
zh_total = len(ZH_NEG.findall(t))
print(f"禁止句    英文 {en_total} / 中文 {zh_total} / 合计 {en_total + zh_total}")
print()

rows = []
for p in re.split(r"\n(?=#{1,2} )", t):
    head = p.split("\n", 1)[0].strip() or "(前言)"
    n = len(p)
    en = len(EN_NEG.findall(p))
    zh = len(ZH_NEG.findall(p))
    dens = (en + zh) / n * 1000 if n else 0
    rows.append((head[:44], n, en, zh, dens))

print(f"{'模块':46}{'字数':>7}{'英否':>6}{'中否':>6}{'密度':>8}")
for head, n, en, zh, dens in sorted(rows, key=lambda x: -x[1]):
    flag = "  <-- 过密" if dens > 8 else ""
    print(f"{head:46}{n:7}{en:6}{zh:6}{dens:8.1f}{flag}")

print()
print("密度 = 每条否定表述 / 千字。经验值：超过 8 视为过密，模型会把注意力分给每条细则。")
