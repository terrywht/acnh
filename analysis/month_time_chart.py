# -*- coding: utf-8 -*-
"""《动物森友会》河鱼 / 海鱼 —— 月份 × 时段 分布矩阵图（v2 单列排版）

口径：
- 数据源 data/FishAppearRiverParam.csv / FishAppearSeaParam.csv，AppearArea=0（北半球）
- 该 (月, 时段) 权重 > 0 即"可刷出"
- 鱼名按权重降序；字号/颜色按权重分层：≥8 加粗黑、3–7 深灰、1–2 浅灰
- 橙色 = 该鱼当月在三个时段中「仅此一时段」可刷（时段专属鱼）
- 灰色 = 垃圾道具
"""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
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
MLAB = {m: f"{m}月" for m in MONTHS}
TIMES = [("Daytime", "白天"), ("MorningAndEvening", "晨昏"), ("Night", "夜晚")]
TRASH = {"石头", "空罐", "长靴", "轮胎"}

STYLE = {
    "白天": dict(bg="#FFFCF2", edge="#EBD08A", tag="#D9A21B"),
    "晨昏": dict(bg="#FFF5EC", edge="#E9A778", tag="#C96A1E"),
    "夜晚": dict(bg="#F6F3FC", edge="#B0A0D6", tag="#6B3FA0"),
}


def load_names():
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
    out = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if int(row["AppearArea"]) != area:
                continue
            iid = int(row["ItemID"])
            for mth in MONTHS:
                for en, _ in TIMES:
                    out[(iid, mth, en)] = int(row.get(f"Prob{MKEY[mth]}{en}") or 0)
    return out


def build(tbl):
    mat = {m: {en: [] for en, _ in TIMES} for m in MONTHS}
    for (iid, m, en), w in tbl.items():
        if w > 0:
            mat[m][en].append((iid, w))
    return mat


def exclusive_set(mat, m):
    """该月只在一个时段出现的鱼 id 集合。"""
    cnt = {}
    for en, _ in TIMES:
        for iid, _ in mat[m][en]:
            cnt[iid] = cnt.get(iid, 0) + 1
    return {iid for iid, c in cnt.items() if c == 1}


def draw(mat, names, title, outfile):
    LM, RM = 1.02, 0.32
    TOP, BOT = 1.52, 0.92
    CW, LINE_H, HEAD_H, ROW_GAP = 1.62, 0.146, 0.30, 0.22

    W = LM + 12 * CW + RM

    def cell_h(m, en):
        raw = mat[m][en]
        nf = sum(1 for i, _ in raw if names.get(i, "") not in TRASH)
        nt = len(raw) - nf
        return HEAD_H + (nf + (1 if nt else 0)) * LINE_H + 0.10

    row_h = [max(cell_h(m, en) for m in MONTHS) for en, _ in TIMES]
    H = TOP + sum(row_h) + ROW_GAP * 2 + BOT

    fig = plt.figure(figsize=(W, H), dpi=160)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    ax.text(LM - 0.04, H - 0.45, title, fontproperties=fpb(18), color="#141414", va="center")
    ax.text(LM - 0.04, H - 0.88,
            "格内 = 该月该时段可刷出的鱼种（按权重降序）　·　"
            "字重=权重：≥8 加粗、3–7 常规、1–2 浅色　·　橙色 = 该月仅此时段可刷　·　底部灰字 = 垃圾道具（折叠为一行）",
            fontproperties=fp(9.0), color="#5A5A5A", va="center")

    y = H - TOP
    for ridx, (en, zh) in enumerate(TIMES):
        st = STYLE[zh]
        row_h_top = max(cell_h(m, en) for m in MONTHS)

        ax.add_patch(FancyBboxPatch((LM - 0.94, y - row_h_top + 0.04), 0.76, row_h_top - 0.08,
                                    boxstyle="round,pad=0.02,rounding_size=0.05",
                                    facecolor=st["tag"], edgecolor="none"))
        ax.text(LM - 0.56, y - row_h_top / 2, zh, fontproperties=fpb(12.5),
                color="#FFFFFF", ha="center", va="center")

        for m in MONTHS:
            x = LM + (m - 1) * CW
            raw = sorted(mat[m][en], key=lambda t: (-t[1], t[0]))
            fish = [(i, w) for i, w in raw if names.get(i, "") not in TRASH]
            trash = [(i, w) for i, w in raw if names.get(i, "") in TRASH]
            n = len(fish)
            excl = exclusive_set(mat, m)
            ne = sum(1 for iid, _ in fish if iid in excl)
            extra = 1 if trash else 0
            rh = HEAD_H + (n + extra) * LINE_H + 0.10

            ax.add_patch(Rectangle((x + 0.03, y - rh), CW - 0.06, rh,
                                   facecolor=st["bg"], edgecolor=st["edge"], linewidth=0.9))

            # 格头：种数 + 专属数
            ax.text(x + 0.10, y - 0.19, f"{n}", fontproperties=fpb(10.2), color=st["tag"], va="center")
            ax.text(x + 0.29, y - 0.19, "种", fontproperties=fp(7.4), color=st["tag"], va="center")
            if ne:
                ax.text(x + CW - 0.12, y - 0.19, f"专属 {ne}", fontproperties=fpb(7.8),
                        color="#C96A1E", va="center", ha="right")

            for ri, (iid, w) in enumerate(fish):
                nm = names.get(iid, str(iid))
                yy = y - HEAD_H - 0.02 - ri * LINE_H
                if iid in excl:
                    f, c = (fpb(8.2) if w >= 8 else fp(8.2)), "#C96A1E"
                elif w >= 8:
                    f, c = fpb(8.4), "#111111"
                elif w >= 3:
                    f, c = fp(8.3), "#3A3A3A"
                else:
                    f, c = fp(8.1), "#7A7A7A"
                ax.text(x + 0.10, yy, nm, fontproperties=f, color=c, va="center")

            if trash:
                yy = y - HEAD_H - 0.02 - n * LINE_H
                ax.text(x + 0.10, yy, f"＋垃圾 {len(trash)} 件",
                        fontproperties=fp(7.6), color="#B0B0B0", va="center")

        y -= row_h_top + ROW_GAP

    # 月合计带
    yb = BOT - 0.22
    ax.text(LM - 0.94, yb, "月合计", fontproperties=fpb(9.6), color="#333333", va="center")
    ax.text(LM - 0.94, yb - 0.20, "（三时段去重）", fontproperties=fp(7.4), color="#888888", va="center")
    for m in MONTHS:
        x = LM + (m - 1) * CW
        uniq = {i for en, _ in TIMES for i, _ in mat[m][en] if names.get(i, "") not in TRASH}
        ax.add_patch(Rectangle((x + 0.03, yb - 0.17), CW - 0.06, 0.34,
                               facecolor="#ECEFF3", edgecolor="#D3D7DE", linewidth=0.8))
        ax.text(x + CW / 2 - 0.02, yb, str(len(uniq)), fontproperties=fpb(10.8),
                color="#2E5FA3", ha="center", va="center")

    for m in MONTHS:
        x = LM + (m - 1) * CW
        ax.text(x + CW / 2 - 0.02, H - TOP + 0.16, MLAB[m], fontproperties=fpb(10.6),
                color="#404040", ha="center", va="bottom")

    ax.text(LM - 0.04, 0.38,
            "数据源：FishAppearRiverParam.csv / FishAppearSeaParam.csv（北半球 AppearArea=0）　·　"
            "判定：该月该时段 Weight > 0 即可刷出　·　垃圾道具 = 石头 / 空罐 / 长靴 / 轮胎（不计数）　·　不含南半球",
            fontproperties=fp(8.5), color="#7A7A7A", va="center")

    fig.savefig(outfile, dpi=160, facecolor="#FFFFFF", bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("saved:", outfile, f"({W:.1f}x{H:.1f} inch)")


names = load_names()
for label, fname, out in [
    ("河鱼", "FishAppearRiverParam.csv", "河鱼_月份x时段分布.png"),
    ("海鱼", "FishAppearSeaParam.csv", "海鱼_月份x时段分布.png"),
]:
    tbl = load_table(DATA / fname)
    mat = build(tbl)
    draw(mat, names, f"{label} · 月份 × 时段 刷鱼分布（北半球）", OUT / out)
