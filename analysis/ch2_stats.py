# -*- coding: utf-8 -*-
"""
ch2_stats.py
第二章（数值分析）所需的全部统计口径，一次算完。
数据源：《动森鱼虫合集.xlsx》「鱼分析表」（鱼 × 月 × 时段 展开行）

输出：analysis/ch2.txt
"""
import collections
import csv
import io
import math
import openpyxl

SRC = r'C:/Users/Administrator/Documents/WPSDrive/344975910/WPS云盘/动森鱼虫合集.xlsx'
OUT = r'C:/Users/Administrator/WorkBuddy/acnh/analysis/ch2.txt'

TIMES = ['白天', '晨昏', '夜晚']
MONTHS = list(range(1, 13))
SYS_TAG = {'河流': '河', '池塘': '河', '悬崖上': '河', '出海口': '河', '所有河': '河',
           '大海': '海', '栈桥': '海', '所有海': '海'}
SHADOW_ORDER = ['SS', 'S', 'M', 'L', 'LL', 'LLL', 'J', 'K', 'U']


def load():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    rows = []
    for r in wb['鱼分析表'].iter_rows(min_row=3, values_only=True):
        if r[0] is None:
            continue
        w = r[7] or 0
        if not r[5] or not r[6]:
            continue
        rows.append({
            'iid': int(r[0]), 'name': r[1], 'size': r[2], 'price': r[3] or 0,
            'month': int(r[5]), 'time': r[6], 'weight': int(w), 'at': str(r[8]),
        })
    return rows


def fish_table(rows):
    """iid -> 元信息 + 月份集合 + 权重矩阵"""
    fish = {}
    for x in rows:
        f = fish.setdefault(x['iid'], {
            'iid': x['iid'], 'name': x['name'], 'size': x['size'],
            'price': x['price'], 'at': x['at'],
            'sys': SYS_TAG.get(x['at'], '?'),
            'months': set(), 'w': collections.defaultdict(int), 'wmax': 0,
        })
        if x['weight'] > 0:
            f['months'].add(x['month'])
            f['w'][(x['month'], x['time'])] = x['weight']
            f['wmax'] = max(f['wmax'], x['weight'])
    # 垃圾（AppearType 为 所有河/所有海 且 price<=75）不计入鱼统计
    return fish


def mean(v):
    v = list(v)
    return sum(v) / len(v) if v else float('nan')


def corr(xs, ys):
    xs, ys = list(xs), list(ys)
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys)) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in xs) / n)
    sy = math.sqrt(sum((b - my) ** 2 for b in ys) / n)
    return cov / (sx * sy) if sx and sy else float('nan')


def main():
    rows = load()
    fish = fish_table(rows)
    junk = {k for k, f in fish.items() if f['at'] in ('所有河', '所有海')}
    real = {k: v for k, v in fish.items() if k not in junk}
    out = []

    def p(*a, **kw):
        line = ' '.join(str(x) for x in a)
        out.append(line)
        print(line, **kw)

    p('# 第二章统计  fish=%d  junk=%d' % (len(real), len(junk)))

    # ---------- A. 每月基础量 ----------
    p('\n## A 每月：鱼种数 / 每档份数合计 / 期望收益（不分钓点）')
    p('月份  河种  海种  合计  河Σw(白天/晨昏/夜)  海Σw(白天/晨昏/夜)  河E    海E')
    mon_cnt = collections.defaultdict(lambda: {'河': set(), '海': set()})
    mon_ev = {}
    for m in MONTHS:
        for sysname in ('河', '海'):
            tot_w = 0
            tot_wp = 0
            for t in TIMES:
                s = sum(f['w'].get((m, t), 0) for f in real.values() if f['sys'] == sysname)
                sp = sum(f['w'].get((m, t), 0) * f['price'] for f in real.values() if f['sys'] == sysname)
                if s:
                    tot_w += 1
                    tot_wp += sp / s
            mon_ev[(m, sysname)] = tot_wp / tot_w if tot_w else 0
        for f in real.values():
            if m in f['months']:
                mon_cnt[m][f['sys']].add(f['iid'])
        rw = [sum(f['w'].get((m, t), 0) for f in real.values() if f['sys'] == '河') for t in TIMES]
        sw = [sum(f['w'].get((m, t), 0) for f in real.values() if f['sys'] == '海') for t in TIMES]
        p('%2d月  %3d  %3d  %3d   %s   %s  %6.0f %6.0f' % (
            m, len(mon_cnt[m]['河']), len(mon_cnt[m]['海']),
            len(mon_cnt[m]['河']) + len(mon_cnt[m]['海']),
            '/'.join('%3d' % x for x in rw), '/'.join('%3d' % x for x in sw),
            mon_ev[(m, '河')], mon_ev[(m, '海')]))

    # ---------- B. 每月贵价鱼 ----------
    p('\n## B 每月贵价鱼集中度（价格分档，按"当月在场"计）')
    p('月份  >=3000  >=5000  >=8000  最高价  最高价鱼')
    for m in MONTHS:
        pres = [f for f in real.values() if m in f['months']]
        top = max(pres, key=lambda f: f['price'])
        p('%2d月   %3d   %3d   %3d   %5d  %s' % (
            m, sum(1 for f in pres if f['price'] >= 3000),
            sum(1 for f in pres if f['price'] >= 5000),
            sum(1 for f in pres if f['price'] >= 8000),
            top['price'], top['name']))

    # ---------- C. 出现月份数 vs 售价 ----------
    p('\n## C 出现月份数 vs 售价')
    buckets = collections.defaultdict(list)
    for f in real.values():
        buckets[len(f['months'])].append(f)
    p('月数  n   均价   中位   最高价  最高价鱼')
    for k in sorted(buckets, reverse=True):
        v = buckets[k]
        pr = sorted(x['price'] for x in v)
        top = max(v, key=lambda x: x['price'])
        p('%3d  %3d  %6.0f %6.0f  %6d  %s' % (
            k, len(v), mean(pr), pr[len(pr) // 2], top['price'], top['name']))
    p('r(月数, 价格) = %.3f' % corr([len(f['months']) for f in real.values()],
                                    [f['price'] for f in real.values()]))

    # 分档聚合
    p('\n分档聚合（月数区间）：')
    bands = [('12', lambda n: n == 12), ('9-11', lambda n: 9 <= n <= 11),
             ('6-8', lambda n: 6 <= n <= 8), ('4-5', lambda n: 4 <= n <= 5),
             ('1-3', lambda n: 1 <= n <= 3)]
    for label, ok in bands:
        v = [f for f in real.values() if ok(len(f['months']))]
        pr = [x['price'] for x in v]
        p('  %-6s n=%2d 均价%6.0f 中位%6.0f 最高%5d  >=5000: %d 条' % (
            label, len(v), mean(pr), sorted(pr)[len(pr) // 2],
            max(pr), sum(1 for x in pr if x >= 5000)))

    # ---------- D. Jaccard ----------
    p('\n## D 月份鱼种集合 Jaccard（相邻月 + 跨度）')
    for sysname in ('河', '海'):
        p(' [%s系]' % sysname)
        sets = {m: {f['iid'] for f in real.values() if f['sys'] == sysname and m in f['months']}
                for m in MONTHS}
        p('  相邻月：' + ' '.join('%d-%d:%.2f' % (m, m + 1,
                                                len(sets[m] & sets[m + 1]) / len(sets[m] | sets[m + 1]))
                                  for m in range(1, 12)))
        p('  对角（同月隔6月）：' + ' '.join('%d-%d:%.2f' % (m, (m + 5) % 12 + 1,
                                                        len(sets[m] & sets[(m + 5) % 12 + 1]) / len(sets[m] | sets[(m + 5) % 12 + 1]))
                                          for m in range(1, 7)))
        p('  最不相似月对：', end='')
        pairs = sorted(((len(sets[a] & sets[b]) / len(sets[a] | sets[b]), a, b)
                        for a in MONTHS for b in MONTHS if a < b))[:3]
        p(' '.join('%d/%d=%.2f' % (a, b, s) for s, a, b in pairs))

    # ---------- E. 河海顶级鱼 ----------
    p('\n## E 河海顶级鱼（价格 Top8）窗口与池内占比')
    for sysname in ('河', '海'):
        p(' [%s系]' % sysname)
        v = sorted([f for f in real.values() if f['sys'] == sysname],
                   key=lambda f: -f['price'])[:8]
        for f in v:
            # 该鱼在其在场月份里的最大池内占比（不分钓点）
            best = 0
            for m in f['months']:
                for t in TIMES:
                    w = f['w'].get((m, t), 0)
                    if not w:
                        continue
                    s = sum(g['w'].get((m, t), 0) for g in real.values() if g['sys'] == sysname)
                    best = max(best, w / s)
            p('   %-8s %6d 价 %2d月 窗口 wmax=%2d 最高占比=%.3f' % (
                f['name'], f['price'], len(f['months']), f['wmax'], best))
        # 系统平均
        p('   --- 全系：均价%.0f 平均窗口%.1f月 平均wmax%.1f' % (
            mean(f['price'] for f in real.values() if f['sys'] == sysname),
            mean(len(f['months']) for f in real.values() if f['sys'] == sysname),
            mean(f['wmax'] for f in real.values() if f['sys'] == sysname)))

    # ---------- F. 相关性 ----------
    p('\n## F 相关性（全 80 种）')
    pr = [f['price'] for f in real.values()]
    mo = [len(f['months']) for f in real.values()]
    avgw = [mean(f['w'].values()) for f in real.values()]
    sh = [SHADOW_ORDER.index(f['size']) if f['size'] in SHADOW_ORDER else -1 for f in real.values()]
    p('r(价格, 月数)      = %.3f' % corr(pr, mo))
    p('r(价格, 平均份数)  = %.3f' % corr(pr, avgw))
    p('r(月数, 平均份数)  = %.3f' % corr(mo, avgw))
    ok = [(s, p_) for s, p_ in zip(sh, pr) if s >= 0]
    p('r(影子序, 价格)    = %.3f  (n=%d)' % (corr([a for a, _ in ok], [b for _, b in ok]), len(ok)))
    ok2 = [(s, w) for s, w in zip(sh, avgw) if s >= 0]
    p('r(影子序, 平均份数)= %.3f' % corr([a for a, _ in ok2], [b for _, b in ok2]))

    # ---------- G. 常驻 vs 短窗口 ----------
    p('\n## G 窗口长度 vs 份数（看常驻鱼是否被摊薄）')
    for label, ok_ in bands:
        v = [f for f in real.values() if ok_(len(f['months']))]
        p('  %-6s n=%2d 平均wmax=%.1f 平均份数=%.1f 均价%.0f' % (
            label, len(v), mean(f['wmax'] for f in v),
            mean(mean(f['w'].values()) for f in v), mean(f['price'] for f in v)))

    # ---------- H. 事件鱼 ----------
    p('\n## H 9 月前后单月/短窗口鱼')
    for f in sorted(real.values(), key=lambda f: len(f['months'])):
        if len(f['months']) <= 2:
            p('   %-8s %6d 价 窗口 %s' % (f['name'], f['price'], sorted(f['months'])))

    # ---------- I. 影子 ----------
    p('\n## I 影子档 × 鱼数 / 均价 / 平均窗口')
    g = collections.defaultdict(list)
    for f in real.values():
        g[f['size']].append(f)
    for s in SHADOW_ORDER:
        v = g.get(s, [])
        if not v:
            continue
        p('  %-3s n=%2d 均价%6.0f 平均窗口%.1f月 平均wmax%.1f 最低价%5d 最高价%5d' % (
            s, len(v), mean(f['price'] for f in v),
            mean(len(f['months']) for f in v), mean(f['wmax'] for f in v),
            min(f['price'] for f in v), max(f['price'] for f in v)))

    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(out))
    print('\n-> %s' % OUT)


if __name__ == '__main__':
    main()
