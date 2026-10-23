# -*- coding: utf-8 -*-
"""月份 × 时段 矩阵探查：确认数据结构与规模，再决定绘图布局。"""
import csv
from pathlib import Path
import openpyxl

ROOT = Path(r"D:/Github/acnh")
DATA = ROOT / "data"
XLSX = Path(r"C:/Users/admin/Desktop/动森钓鱼概率总表.xlsx")

MONTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
MLAB = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
# 列名里的月份写法
MKEY = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
TIMES = [("Daytime", "白天"), ("MorningAndEvening", "晨昏"), ("Night", "夜晚")]


def load_names():
    """ItemID -> 中文名（桌面总表）。"""
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb["Sheet1"]
    rows = list(ws.iter_rows(values_only=True))
    m = {}
    for r in rows[1:]:
        if r[0] is None or not str(r[5]).isdigit():
            continue
        try:
            m[int(r[0])] = str(r[1]).strip()
        except (TypeError, ValueError):
            continue
    return m


def load_table(path, area=0):
    """返回 (itemid, month, time) -> weight，只取指定半球。"""
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["AppearArea"]) != area:
                continue
            iid = int(row["ItemID"])
            for m in MONTHS:
                for en, _ in TIMES:
                    col = f"Prob{MKEY[m]}{en}"
                    out[(iid, m, en)] = int(row.get(col) or 0)
    return out


def build(tbl):
    """month -> time_en -> [(name, weight)]，权重>0 才算可刷出。"""
    mat = {m: {en: [] for en, _ in TIMES} for m in MONTHS}
    for (iid, m, en), w in tbl.items():
        if w > 0:
            mat[m][en].append((iid, w))
    return mat


names = load_names()
print("名字映射条数:", len(names))

for label, fname in [("河鱼", "FishAppearRiverParam.csv"), ("海鱼", "FishAppearSeaParam.csv")]:
    tbl = load_table(DATA / fname)
    mat = build(tbl)
    print(f"\n===== {label} =====")
    print("月  白天 晨昏 夜晚 | 合计(去重)")
    print("-" * 46)
    mx = 0
    for m in MONTHS:
        cnts = []
        uniq = set()
        for en, _ in TIMES:
            ids = {iid for iid, _ in mat[m][en]}
            cnts.append(len(ids))
            uniq |= ids
            mx = max(mx, len(ids))
        print(f"{MLAB[m]}  {cnts[0]:4d} {cnts[1]:4d} {cnts[2]:4d} | {len(uniq):3d}")
    print("单格最大鱼数:", mx)

    # 逐格明细抽样（9 月）
    print(f"\n[{label}] 9 月逐时段明细（按权重降序）:")
    for en, zh in TIMES:
        lst = sorted(mat[9][en], key=lambda x: -x[1])
        print(f"  {zh}({len(lst)}):", "、".join(f"{names.get(i, i)}w{w}" for i, w in lst))
