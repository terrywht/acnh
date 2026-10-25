# -*- coding: utf-8 -*-
"""
ch2_extra.py —— 第二章补充统计
1) 垃圾份数（验证每档 Σw=100）
2) 每月顶级鱼（≥8000）按河海分：条数 / 份额（验证"海系多种类稀释"）
3) 摊薄效应：每鱼平均份数 = Σw / 当月鱼种数
4) 12×12 Jaccard 矩阵（导出 CSV 供热力图）
5) 顶级鱼在其窗口内的平均池内概率（河 vs 海）
输出：analysis/ch2_extra.txt + analysis/jaccard_river.csv / jaccard_sea.csv
"""
import collections
import csv
import io
import openpyxl

SRC = r'C:/Users/Administrator/Documents/WPSDrive/344975910/WPS云盘/动森鱼虫合集.xlsx'
OUT = r'C:/Users/Administrator/WorkBuddy/acnh/analysis/ch2_extra.txt'
TIMES = ['白天', '晨昏', '夜晚']
MONTHS = list(range(1, 13))
SYS_TAG = {'河流': '河', '池塘': '河', '悬崖上': '河', '出海口': '河', '所有河': '河',
           '大海': '海', '栈桥': '海', '所有海': '海'}
out = []


def p(*a):
    line = ' '.join(str(x) for x in a)
    out.append(line)
    print(line)


def load():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    rows = []
    for r in wb['鱼分析表'].iter_rows(min_row=3, values_only=True):
        if r[0] is None or not r[5] or not r[6]:
            continue
        rows.append({'iid': int(r[0]), 'name': r[1], 'size': r[2], 'price': r[3] or 0,
                     'month': int(r[5]), 'time': r[6], 'weight': int(r[7] or 0),
                     'at': str(r[8]), 'sys': SYS_TAG.get(str(r[8]), '?')})
    return rows


rows = load()
junk = [x for x in rows if x['at'] in ('所有河', '所有海')]
fish = [x for x in rows if x['at'] not in ('所有河', '所有海')]

p('## 1 垃圾份数')
for sysname in ('河', '海'):
    p(' [%s系]' % sysname)
    jj = [x for x in junk if x['sys'] == sysname]
    for x in jj[:12]:
        p('   %-6s %2d月 %-3s w=%d' % (x['at'], x['month'], x['time'], x['weight']))
    tot = collections.Counter()
    for x in jj:
        tot[(x['month'], x['time'])] += x['weight']
    p('   每档合计：' + ' '.join('%d月:%d' % (m, tot[(m, '白天')]) for m in MONTHS))

p('\n## 2 总分验证：鱼 + 垃圾 每档合计')
for sysname in ('河', '海'):
    vals = set()
    for m in MONTHS:
        for t in TIMES:
            s = sum(x['weight'] for x in fish if x['sys'] == sysname and x['month'] == m and x['time'] == t)
            s += sum(x['weight'] for x in junk if x['sys'] == sysname and x['month'] == m and x['time'] == t)
            vals.add(s)
    p('   %s系 36 格合计取值集合 = %s' % (sysname, sorted(vals)))

p('\n## 3 每月顶级鱼（≥8000）条数与份额')
p('月份  河条 河份  海条 海份   河顶级占比 海顶级占比')
for m in MONTHS:
    line = '%2d月' % m
    res = {}
    for sysname in ('河', '海'):
        # 取该月在场的顶级鱼，份额取该月三档中最大值
        names = {x['iid'] for x in fish if x['sys'] == sysname and x['month'] == m and x['price'] >= 8000}
        best = 0
        bestcnt = 0
        for t in TIMES:
            sel = [x for x in fish if x['sys'] == sysname and x['month'] == m and x['time'] == t and x['price'] >= 8000]
            w = sum(x['weight'] for x in sel)
            if w > best:
                best, bestcnt = w, len(sel)
        res[sysname] = (len(names), best)
        line += '  %2d  %2d ' % (len(names), best)
    line += '   %.1f%%      %.1f%%' % (res['河'][1], res['海'][1])
    p(line)

p('\n## 4 摊薄：每鱼平均份数')
p('月份  河种 河Σw 河均份   海种 海Σw 海均份')
for m in MONTHS:
    line = '%2d月' % m
    for sysname in ('河', '海'):
        n = len({x['iid'] for x in fish if x['sys'] == sysname and x['month'] == m and x['weight'] > 0})
        s = sum(x['weight'] for x in fish if x['sys'] == sysname and x['month'] == m and x['time'] == '白天')
        line += '  %3d %4d %5.2f' % (n, s, s / n if n else 0)
    p(line)

p('\n## 5 顶级鱼窗口内平均池内概率（分母=100）')
for sysname in ('河', '海'):
    top = sorted([f for f in {x['iid']: x for x in fish if x['sys'] == sysname}.values()],
                 key=lambda f: -f['price'])[:10]
    vals = []
    for f in top:
        ws = [x['weight'] for x in fish if x['iid'] == f['iid'] and x['weight'] > 0]
        vals.append(sum(ws) / len(ws) / 100)
    p('  %s系 Top10 平均 w=%.2f 平均池内概率=%.2f%%' % (sysname, sum(
        sum(x['weight'] for x in fish if x['iid'] == f['iid'] and x['weight'] > 0) /
        len([x for x in fish if x['iid'] == f['iid'] and x['weight'] > 0]) for f in top) / 10,
        sum(vals) / len(vals) * 100))

p('\n## 6 Jaccard 12x12')
for sysname in ('河', '海'):
    sets = {m: {x['iid'] for x in fish if x['sys'] == sysname and x['month'] == m and x['weight'] > 0}
            for m in MONTHS}
    mat = []
    for a in MONTHS:
        row = []
        for b in MONTHS:
            u = len(sets[a] | sets[b])
            row.append(len(sets[a] & sets[b]) / u if u else 0)
        mat.append(row)
    fn = r'C:/Users/Administrator/WorkBuddy/acnh/analysis/jaccard_%s.csv' % ('river' if sysname == '河' else 'sea')
    with io.open(fn, 'w', encoding='utf-8', newline='') as fh:
        wr = csv.writer(fh)
        wr.writerow(['月'] + ['%d月' % m for m in MONTHS])
        for i, m in enumerate(MONTHS):
            wr.writerow(['%d月' % m] + ['%.3f' % v for v in mat[i]])
    p('   %s 系 -> %s  平均=%.3f' % (sysname, fn, sum(sum(r) for r in mat) / 144))

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
print('\n->', OUT)
