# -*- coding: utf-8 -*-
"""《动物森友会》河鱼 / 海鱼 —— 「一鱼一行」季节 × 时段 热力表

与 v1（月×时段的矩阵、鱼名在每格重复）不同：本版每条鱼只出现一次。
- 行 = 鱼（按活跃月数降序 → 首次出现月 → 售价降序）
- 列 = 1–12 月
- 格色 = 该月该鱼可刷的时段组合（7 类，见 COLORS）
- 空白 = 该月刷不到

口径：data/*.csv，北半球 AppearArea=0，Weight>0 即判定可刷出。
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
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

# 时段组合 → (颜色, 图例名)。key 为 sorted(tuple) 后的 Unicode 序：夜 < 昏 < 白
COLORS = {
    ("夜", "昏", "白"): ("#2E5FA3", "全天（白+昏+夜）"),
    ("昏", "白"): ("#D29418", "白天 + 晨昏"),
    ("夜", "昏"): ("#7B54B8", "晨昏 + 夜晚"),
    ("夜", "白"): ("#3E8E5A", "白天 + 夜晚"),
    ("白",): ("#FCE9B6", "仅白天"),
    ("夜",): ("#C4B2E2", "仅夜晚"),
    ("昏",): ("#F0A868", "仅晨昏"),
}
BLANK = "#FBFBFB"


def load_meta():
    """ItemID -> (名字, 影子档, 售价)。"""
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
    """(itemid, month) -> tuple(可刷时段中文集合)。"""
    raw = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["AppearArea"]) != area:
                continue
            iid = int(row["ItemID"])
            for mth in MONTHS:
                s = {zh for en, zh in TIMES if int(row.get(f"Prob{MKEY[mth]}{en}") or 0) > 0}
                if s:
                    raw[(iid, mth)] = tuple(sorted(s))
    return raw


def draw(combos, meta, title, subtitle, outfile, weight_of=None):
    nm_of = lambda i: meta.get(i, ("", "", 0))[0]
    LM, NAME_W, SHADOW_W, PRICE_W = 0.34, 1.16, 0.40, 0.62
    CW, CNT_W, RM = 0.565, 0.44, 0.28
    TOP, BOT, RH = 1.62, 1.12, 0.235

    # 汇总每个 id 的活跃月
    ids = sorted({i for i, _ in combos})
    info = {}
    for iid in ids:
        mm = {m: combos[(iid, m)] for m in MONTHS if (iid, m) in combos}
        info[iid] = mm
    # 排序：正常鱼在前、垃圾沉底 → 活跃月数↓ → 首次月↑ → 售价↓
    def sort_key(i):
        nm = meta.get(i, ("", "", 0))[0]
        return (1 if nm in TRASH else 0, -len(info[i]),
                min(info[i]) if info[i] else 99, -meta.get(i, ("", "", 0))[2])

    ids.sort(key=sort_key)

    n = len(ids)
    W = LM + NAME_W + SHADOW_W + PRICE_W + 12 * CW + CNT_W + RM
    H = TOP + n * RH + BOT

    fig = plt.figure(figsize=(W, H), dpi=160)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    ax.text(LM, H - 0.40, title, fontproperties=fpb(19), color="#141414", va="center")
    ax.text(LM, H - 0.70, subtitle, fontproperties=fp(9.2), color="#5E5E5E", va="center")

    # 图例（顶部一行）
    used = sorted({c for c in info.values() for c in c.values()},
                  key=lambda t: list(COLORS).index(t) if t in COLORS else 99)
    lx = LM
    for c in used:
        col, lab = COLORS[c]
        ax.add_patch(Rectangle((lx, H - 1.02), 0.17, 0.17, facecolor=col, edgecolor="none"))
        ax.text(lx + 0.23, H - 0.935, lab, fontproperties=fp(8.4), color="#333333", va="center")
        lx += 0.34 + len(lab) * 0.121

    # 表头
    hy = H - TOP + 0.10
    ax.text(LM + 0.02, hy, "鱼名", fontproperties=fpb(9.2), color="#333333", va="center")
    ax.text(LM + NAME_W - 0.06, hy, "影档", fontproperties=fpb(8.2), color="#666666", va="center")
    ax.text(LM + NAME_W + SHADOW_W - 0.04, hy, "售价", fontproperties=fpb(8.2), color="#666666", va="center")
    for m in MONTHS:
        x = LM + NAME_W + SHADOW_W + PRICE_W + (m - 1) * CW
        ax.text(x + CW / 2, hy, f"{m}", fontproperties=fpb(9.0), color="#555555",
                ha="center", va="center")
    ax.text(LM + NAME_W + SHADOW_W + PRICE_W + 12 * CW + CNT_W / 2 - 0.02, hy, "月数",
            fontproperties=fpb(8.0), color="#666666", ha="center", va="center")

    # 一条浅线
    ax.plot([LM, W - RM], [hy - 0.20, hy - 0.20], color="#D8D8D8", lw=0.8)

    y = hy - 0.32
    prev_n = None
    for idx, iid in enumerate(ids):
        mm = info[iid]
        nm, sh, pr = meta.get(iid, (str(iid), "?", 0))
        is_trash = nm in TRASH
        cnt = len(mm)

        # 组间分隔（活跃月数变化处）
        if prev_n is not None and cnt != prev_n:
            ax.plot([LM, W - RM], [y + RH / 2 + 0.015, y + RH / 2 + 0.015],
                    color="#C9CFD8", lw=1.1, zorder=1)
        prev_n = cnt

        # 常驻鱼（12 月）整行浅底
        if cnt == 12 and not is_trash:
            ax.add_patch(Rectangle((LM - 0.04, y - RH / 2), W - LM - RM + 0.04, RH,
                                   facecolor="#F4F8FF", edgecolor="none", zorder=0))

        c_name = "#ADADAD" if is_trash else "#1A1A1A"
        ax.text(LM + 0.02, y, nm, fontproperties=fp(8.6), color=c_name, va="center")
        ax.text(LM + NAME_W + 0.02, y, sh, fontproperties=fp(7.4),
                color="#B5B5B5" if is_trash else "#8A8A8A", va="center")
        ax.text(LM + NAME_W + SHADOW_W + 0.02, y, f"¥{pr:,}", fontproperties=fp(7.6),
                color="#B5B5B5" if is_trash else "#5A5A5A", va="center")

        mx = LM + NAME_W + SHADOW_W + PRICE_W
        for m in MONTHS:
            x = mx + (m - 1) * CW
            c = mm.get(m)
            if c:
                col = COLORS.get(c, ("#999999", ""))[0]
                ax.add_patch(Rectangle((x + 0.035, y - RH / 2 + 0.028), CW - 0.07, RH - 0.056,
                                       facecolor=col, edgecolor="none"))
            else:
                ax.add_patch(Rectangle((x + 0.035, y - RH / 2 + 0.028), CW - 0.07, RH - 0.056,
                                       facecolor=BLANK, edgecolor="#F0F0F0", linewidth=0.4))

        ax.text(mx + 12 * CW + CNT_W / 2 - 0.02, y, str(cnt), fontproperties=fpb(8.6),
                color="#2E5FA3" if cnt == 12 else "#6A6A6A", ha="center", va="center")
        y -= RH

    ax.plot([LM, W - RM], [y + RH / 2, y + RH / 2], color="#D8D8D8", lw=0.8)

    # 底部：每月可刷鱼种数（不含垃圾）
    ysum = y + RH / 2 - 0.30
    ax.text(LM + 0.02, ysum, "当月可刷", fontproperties=fpb(8.4), color="#333333", va="center")
    ax.text(LM + 0.02, ysum - 0.19, "（种，不含垃圾）", fontproperties=fp(7.0), color="#8A8A8A", va="center")
    mx = LM + NAME_W + SHADOW_W + PRICE_W
    for m in MONTHS:
        k = sum(1 for i in ids if nm_of(i) not in TRASH and (i, m) in combos)
        x = mx + (m - 1) * CW
        ax.text(x + CW / 2, ysum, str(k), fontproperties=fpb(9.0), color="#2E5FA3",
                ha="center", va="center")

    ax.text(LM, 0.40,
            "口径：北半球 AppearArea=0　·　格色 = 该月可刷的时段组合，空白 = 该月刷不到　·　"
            "行序按活跃月数降序，浅蓝底 = 全年 12 个月常驻　·　灰色行为垃圾道具",
            fontproperties=fp(8.4), color="#7A7A7A", va="center")

    fig.savefig(outfile, dpi=160, facecolor="#FFFFFF", bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("saved:", outfile, f"({W:.1f}x{H:.1f} in, {n} 行)")


meta = load_meta()
for label, fname, out, sub in [
    ("河鱼", "FishAppearRiverParam.csv", "河鱼_一鱼一行.png",
     "一行一鱼 · 横轴 12 个月 · 格色=该月可刷时段组合（连续色块 = 连续季节窗口）"),
    ("海鱼", "FishAppearSeaParam.csv", "海鱼_一鱼一行.png",
     "一行一鱼 · 横轴 12 个月 · 格色=该月可刷时段组合（连续色块 = 连续季节窗口）"),
]:
    combos = load_combo(DATA / fname)
    draw(combos, meta, f"{label} · 季节窗口 × 可刷时段（北半球）", sub, OUT / out)
