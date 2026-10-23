# -*- coding: utf-8 -*-
"""《动物森友会》河鱼 / 海鱼 —— 时段互斥分组图

核心：把鱼按「可刷时段组合」分成 7 个互斥组，组内排季节窗口。
- 组头右侧三格图标：白 / 昏 / 夜，实心=可刷、空心=刷不到 → 互斥关系一眼可见
- 行 = 鱼；列 = 1–12 月；格色 = 该月实际可刷组合（跨月变化的个例会露出异色）
- 数据：data/*.csv，北半球 AppearArea=0，Weight>0 即可刷出
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties
import openpyxl

ROOT = Path(r"D:/Github/acnh")
DATA = ROOT / "data"
OUT = Path(r"C:/Users/admin/WorkBuddy/2026-09-28-14-15-50/outputs/acnh-r9-r10")
OUT.mkdir(parents=True, exist_ok=True)
XLSX = Path(r"C:/Users/admin/Desktop/动森钓鱼概率总表.xlsx")

F, FB = "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttc"
fp = lambda s: FontProperties(fname=F, size=s)
fpb = lambda s: FontProperties(fname=FB, size=s)

MONTHS = list(range(1, 13))
MKEY = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
TIMES = [("Daytime", "白"), ("MorningAndEvening", "昏"), ("Night", "夜")]
TRASH = {"石头", "空罐", "长靴", "轮胎"}

COLORS = {
    ("夜", "昏", "白"): "#2E5FA3",
    ("昏", "白"): "#D29418",
    ("夜", "昏"): "#7B54B8",
    ("夜", "白"): "#3E8E5A",
    ("白",): "#FCE9B6",
    ("夜",): "#C4B2E2",
    ("昏",): "#F0A868",
}
# (key, 组名, 互斥说明, (白,昏,夜) 是否可刷)
GROUPS = [
    (("夜", "昏", "白"), "全天 · 白+昏+夜", "三时段都可刷，不与其他时段互斥", (1, 1, 1)),
    (("昏", "白"), "白天 + 晨昏", "夜晚刷不到 · 与「夜晚」互斥", (1, 1, 0)),
    (("夜", "昏"), "晨昏 + 夜晚", "白天刷不到 · 与「白天」互斥", (0, 1, 1)),
    (("夜", "白"), "白天 + 夜晚", "晨昏刷不到 · 唯一「掐掉中间」的组合", (1, 0, 1)),
    (("白",), "仅白天", "晨昏、夜晚都刷不到", (1, 0, 0)),
    (("夜",), "仅夜晚", "白天、晨昏都刷不到", (0, 0, 1)),
    (("昏",), "仅晨昏", "白天、夜晚都刷不到", (0, 1, 0)),
]
BLANK = "#FBFBFB"


def load_meta():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    rows = list(wb["Sheet1"].iter_rows(values_only=True))
    meta = {}
    for r in rows[1:]:
        if r[0] is None or not str(r[5]).isdigit():
            continue
        try:
            iid = int(r[0])
            if iid in meta:
                continue
            meta[iid] = (str(r[1]).strip(), str(r[2]).strip(), int(r[3]) if r[3] else 0)
        except (TypeError, ValueError):
            continue
    return meta


def load_combo(path, area=0):
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["AppearArea"]) != area:
                continue
            iid = int(row["ItemID"])
            for mth in MONTHS:
                s = {zh for en, zh in TIMES if int(row.get(f"Prob{MKEY[mth]}{en}") or 0) > 0}
                if s:
                    out[(iid, mth)] = tuple(sorted(s))
    return out


def dominant(iid, combos):
    """该鱼出现最多的组合；并列时取可刷时段更多的。"""
    from collections import Counter
    c = Counter(combos[(iid, m)] for m in MONTHS if (iid, m) in combos)
    return max(c.items(), key=lambda kv: (kv[1], len(kv[0])))[0]


def draw(combos, meta, title, subtitle, outfile):
    LM, NAME_W, SHADOW_W, PRICE_W = 0.34, 1.16, 0.40, 0.62
    CW, CNT_W, RM = 0.565, 0.52, 0.26
    TOP, RH, GH, GGAP = 1.95, 0.225, 0.355, 0.10
    BOT = 1.10

    nm_of = lambda i: meta.get(i, ("", "", 0))[0]
    ids = [i for i in {i for i, _ in combos} if nm_of(i) not in TRASH]

    buckets = {g[0]: [] for g in GROUPS}
    for i in ids:
        buckets[dominant(i, combos)].append(i)
    for k in buckets:
        buckets[k].sort(key=lambda i: (-len([m for m in MONTHS if (i, m) in combos]),
                                        min(m for m in MONTHS if (i, m) in combos),
                                        -meta.get(i, ("", "", 0))[2]))

    nrow = len(ids)
    from itertools import groupby
    active = [(g, buckets[g[0]]) for g in GROUPS if buckets[g[0]]]
    ngroups = len(active)

    W = LM + NAME_W + SHADOW_W + PRICE_W + 12 * CW + CNT_W + RM
    H = TOP + nrow * RH + ngroups * (GH + GGAP) + BOT

    fig = plt.figure(figsize=(W, H), dpi=160)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    ax.text(LM, H - 0.42, title, fontproperties=fpb(19), color="#141414", va="center")
    ax.text(LM, H - 0.72, subtitle, fontproperties=fp(9.2), color="#5E5E5E", va="center")

    # 顶部总览：7 个互斥组的人数条
    SHORT = {("夜", "昏", "白"): "全天", ("昏", "白"): "白+昏", ("夜", "昏"): "昏+夜",
             ("夜", "白"): "白+夜", ("白",): "仅白", ("夜",): "仅夜", ("昏",): "仅昏"}
    lx, ly = LM, H - 1.20
    ax.text(LM, ly + 0.30, "时段互斥结构（鱼种数）", fontproperties=fpb(9.4), color="#333333", va="center")
    for key, gname, gdesc, flags in GROUPS:
        cnt = len(buckets[key])
        if not cnt:
            continue
        ax.add_patch(Rectangle((lx, ly - 0.02), 0.20, 0.20, facecolor=COLORS[key], edgecolor="none"))
        ax.text(lx + 0.26, ly + 0.08, SHORT[key], fontproperties=fp(8.4), color="#333333", va="center")
        ax.text(lx + 0.26, ly - 0.14, f"{cnt} 条", fontproperties=fpb(8.4), color="#1F4E8C", va="center")
        lx += 1.15

    # 表头
    hy = H - TOP + 0.06
    ax.text(LM + 0.02, hy, "鱼名", fontproperties=fpb(9.2), color="#333333", va="center")
    ax.text(LM + NAME_W - 0.08, hy, "影档", fontproperties=fpb(8.0), color="#666666", va="center")
    ax.text(LM + NAME_W + SHADOW_W - 0.04, hy, "售价", fontproperties=fpb(8.0), color="#666666", va="center")
    mx = LM + NAME_W + SHADOW_W + PRICE_W
    for m in MONTHS:
        ax.text(mx + (m - 1) * CW + CW / 2, hy, str(m), fontproperties=fpb(9.0),
                color="#555555", ha="center", va="center")
    ax.text(mx + 12 * CW + CNT_W / 2, hy, "月数", fontproperties=fpb(8.0), color="#666666",
            ha="center", va="center")
    ax.plot([LM, W - RM], [hy - 0.24, hy - 0.24], color="#D8D8D8", lw=0.8)

    y = hy - 0.36
    for g, items in active:
        key, gname, gdesc, flags = g
        # 组头
        ax.add_patch(Rectangle((LM - 0.04, y - GH + 0.10), W - LM - RM + 0.04, GH - 0.04,
                               facecolor="#F2F5F9", edgecolor="none", zorder=0))
        ax.add_patch(Rectangle((LM - 0.04, y - GH + 0.10), 0.035, GH - 0.04,
                               facecolor=COLORS[key], edgecolor="none", zorder=3))
        ax.add_patch(Rectangle((LM, y - 0.09), 0.20, 0.20, facecolor=COLORS[key], edgecolor="none", zorder=2))
        ax.text(LM + 0.28, y + 0.01, gname, fontproperties=fpb(10.4), color="#1A1A1A", va="center", zorder=2)
        ax.text(LM + 0.28 + len(gname) * 0.145, y + 0.01, f"· {len(items)} 条",
                fontproperties=fp(9.0), color="#5A6A7A", va="center", zorder=2)
        ax.text(LM + 2.30, y - 0.13, gdesc, fontproperties=fp(8.2), color="#7A7A7A", va="center", zorder=2)
        # 三格图标
        for k, (fl, lab) in enumerate(zip(flags, ["白", "昏", "夜"])):
            xx = mx + 12 * CW + 0.03 + k * 0.155
            ax.add_patch(Rectangle((xx, y - 0.09), 0.12, 0.12,
                                   facecolor=COLORS[key] if fl else "#FFFFFF",
                                   edgecolor="#9AA3AE" if not fl else "none", linewidth=0.8,
                                   zorder=2))
        y -= GH + 0.06

        for iid in items:
            nm, sh, pr = meta.get(iid, (str(iid), "?", 0))
            mm = {m: combos[(iid, m)] for m in MONTHS if (iid, m) in combos}
            ax.text(LM + 0.02, y, nm, fontproperties=fp(8.6), color="#1A1A1A", va="center")
            ax.text(LM + NAME_W - 0.02, y, sh, fontproperties=fp(7.4), color="#8A8A8A", va="center")
            ax.text(LM + NAME_W + SHADOW_W - 0.02, y, f"¥{pr:,}", fontproperties=fp(7.6),
                    color="#5A5A5A", va="center")
            for m in MONTHS:
                x = mx + (m - 1) * CW
                c = mm.get(m)
                if c:
                    ax.add_patch(Rectangle((x + 0.035, y - RH / 2 + 0.026), CW - 0.07, RH - 0.052,
                                           facecolor=COLORS[c], edgecolor="none"))
                else:
                    ax.add_patch(Rectangle((x + 0.035, y - RH / 2 + 0.026), CW - 0.07, RH - 0.052,
                                           facecolor=BLANK, edgecolor="#F0F0F0", linewidth=0.4))
            ax.text(mx + 12 * CW + CNT_W / 2, y, str(len(mm)), fontproperties=fpb(8.6),
                    color="#2E5FA3" if len(mm) == 12 else "#6A6A6A", ha="center", va="center")
            y -= RH
        y -= GGAP

    ax.plot([LM, W - RM], [y + GGAP - 0.02, y + GGAP - 0.02], color="#C9CFD8", lw=1.0)

    # 当月可刷合计
    ys = y + GGAP - 0.36
    ax.text(LM + 0.02, ys, "当月可刷", fontproperties=fpb(8.2), color="#333333", va="center")
    ax.text(LM + 0.02, ys - 0.18, "（种）", fontproperties=fp(7.0), color="#8A8A8A", va="center")
    for m in MONTHS:
        k = sum(1 for i in ids if (i, m) in combos)
        ax.text(mx + (m - 1) * CW + CW / 2, ys, str(k), fontproperties=fpb(9.0),
                color="#2E5FA3", ha="center", va="center")

    ax.text(LM, 0.42,
            "互斥读法：组头右侧三格 = 白 / 昏 / 夜，实心=可刷、空心=刷不到　·　格色 = 该月实际可刷组合　·　"
            "空白 = 该月钓不到该鱼（垃圾道具石头/空罐/长靴/轮胎除外，未计入）",
            fontproperties=fp(8.3), color="#7A7A7A", va="center")

    fig.savefig(outfile, dpi=160, facecolor="#FFFFFF", bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("saved:", outfile, f"({W:.1f}x{H:.1f} in, {nrow} 鱼, {ngroups} 组)")


meta = load_meta()
for label, fname, out in [
    ("河鱼", "FishAppearRiverParam.csv", "河鱼_时段互斥图.png"),
    ("海鱼", "FishAppearSeaParam.csv", "海鱼_时段互斥图.png"),
]:
    draw(load_combo(DATA / fname), meta,
         f"{label} · 时段互斥 × 季节窗口（北半球）",
         "按「可刷时段组合」分组 · 组内按活跃月数排序 · 一条鱼一行",
         OUT / out)
