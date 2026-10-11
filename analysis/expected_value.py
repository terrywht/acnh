# -*- coding: utf-8 -*-
"""
expected_value.py
计算「鱼 · 每月每钓点的期望收益」，河/海各导出一份 CSV。

口径：
  1. 钓点鱼池由「水域表」决定（钓点 -> 可刷 AppearType 集合），并非一一对应：
       河流   <- 河流 / 所有河
       池塘   <- 池塘 / 所有河
       悬崖上 <- 悬崖上 / 河流 / 所有河
       出海口 <- 出海口 / 河流 / 所有河
       大海   <- 大海 / 所有海
       栈桥   <- 栈桥 / 大海 / 所有海          （栈桥池 ⊇ 大海池）
  2. 某 (月, 时段, 钓点) 的咬钩概率 = 该鱼 Weight / 该池 ΣWeight（引擎加权轮盘）。
  3. 该组合的期望售价 E = Σ(Weight × Price) / ΣWeight（= 加权平均价格）。
  4. 一天按 3 个时段档等长（白天 9-16 / 晨昏 5-8&17-20 / 夜晚 18-4，各约 8h），
     故「每月每钓点」的期望收益 = 三个时段 E 的算术平均（空池时段跳过）。
"""
import collections
import csv
import openpyxl

SRC = r'C:/Users/Administrator/Documents/WPSDrive/344975910/WPS云盘/动森鱼虫合集.xlsx'
OUT_DIR = r'C:/Users/Administrator/WorkBuddy/acnh/analysis/'

GROUPS = {
    '河鱼': ['河流', '池塘', '悬崖上', '出海口'],
    '海鱼': ['大海', '栈桥'],
}
TIMES = ['白天', '晨昏', '夜晚']


def load_all():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)

    spot_map = collections.defaultdict(set)
    for row in wb['水域表'].iter_rows(values_only=True):
        if row[0] and row[1]:
            spot_map[str(row[0])].add(str(row[1]))

    recs = []
    for r in wb['鱼分析表'].iter_rows(min_row=3, values_only=True):
        if r[0] is None:
            continue
        w = r[7]
        if not w or w <= 0 or not r[5]:
            continue
        recs.append({
            'iid': int(r[0]), 'name': r[1], 'price': r[3] or 0,
            'month': int(r[5]), 'time': r[6], 'weight': int(w), 'at': str(r[8]),
        })
    return spot_map, recs


def aggregate(recs, spots, spot_map):
    """(month, time, spot) -> [Σweight, Σ(weight*price)]"""
    agg = collections.defaultdict(lambda: [0, 0.0])
    for x in recs:
        for s in spots:
            if x['at'] in spot_map[s]:
                k = (x['month'], x['time'], s)
                agg[k][0] += x['weight']
                agg[k][1] += x['weight'] * x['price']
    return agg


def expected_by_month(agg, spots):
    out = {}
    for m in range(1, 13):
        out[m] = {}
        for s in spots:
            es = []
            for t in TIMES:
                k = (m, t, s)
                if k in agg and agg[k][0] > 0:
                    es.append(agg[k][1] / agg[k][0])
            out[m][s] = (sum(es) / len(es)) if es else None
    return out


def compute(spots, spot_map, recs):
    agg = aggregate(recs, spots, spot_map)
    EV = expected_by_month(agg, spots)
    months = list(range(1, 13))
    data = {s: [EV[m][s] or 0 for m in months] for s in spots}
    mean = [sum(EV[m][s] for s in spots) / len(spots) for m in months]
    return months, data, mean, EV


def export_csv(label, spots, EV):
    path = OUT_DIR + f'{label}期望收益.csv'
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['月份'] + spots + ['均值'])
        for m in range(1, 13):
            vals = [EV[m][s] for s in spots]
            ok = [v for v in vals if v is not None]
            avg = round(sum(ok) / len(ok), 1) if ok else ''
            w.writerow([f'{m}月'] + [round(v, 1) if v is not None else '' for v in vals] + [avg])
    return path


def render_table(label, spots, EV):
    print(f'\n=== {label} · 每月每钓点期望收益（铃钱/次） ===')
    print('月份  ' + ''.join(f'{s:>10s}' for s in spots) + f'{"均值":>10s}')
    for m in range(1, 13):
        vals = [EV[m][s] for s in spots]
        ok = [v for v in vals if v is not None]
        avg = sum(ok) / len(ok) if ok else 0
        line = f'{m:2d}月  ' + ''.join(
            (f'{v:10.1f}' if v is not None else f'{"-":>10s}') for v in vals)
        print(line + f'{avg:10.1f}')


if __name__ == '__main__':
    spot_map, recs = load_all()
    print('钓点 -> AppearType 映射:')
    for k, v in spot_map.items():
        print(f'  {k}: {sorted(v)}')

    for label, spots in GROUPS.items():
        months, data, mean, EV = compute(spots, spot_map, recs)
        render_table(label, spots, EV)
        print('saved:', export_csv(label, spots, EV))
