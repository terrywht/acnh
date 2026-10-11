# -*- coding: utf-8 -*-
"""
plot_expected_value.py
可视化「每月每钓点期望收益」，河鱼 / 海鱼各两张：

  图 1：分组柱状图（每月 N 根柱 = N 个钓点）+ 均值折线
        -> 回答"某月哪个钓点期望收益更高"
  图 2：热力图（N 钓点 × 12 月）
        -> 矩阵全景，快速定位最优 (月, 钓点)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

from expected_value import load_all, compute, export_csv, GROUPS

CN = FontProperties(fname=r'C:/Windows/Fonts/msyh.ttc')
OUT_DIR = r'C:/Users/Administrator/WorkBuddy/acnh/analysis/'

SPOT_COLOR = {
    '河流':   '#2E5FA3',
    '池塘':   '#2F8F4E',
    '悬崖上': '#C96A1E',
    '出海口': '#6B3FA0',
    '大海':   '#2E5FA3',
    '栈桥':   '#C96A1E',
}


def draw_bar(label, spots, months, data, mean, outpath):
    fig, ax = plt.subplots(figsize=(13.5, 6.2))
    fig.patch.set_facecolor('#FFFFFF')
    x = np.arange(len(months))
    w = 0.7 / len(spots)
    for i, s in enumerate(spots):
        off = (i - (len(spots) - 1) / 2) * w
        ax.bar(x + off, data[s], w,
               label=s, color=SPOT_COLOR[s], edgecolor='white', linewidth=0.6, zorder=3)

    ax.plot(x, mean, color='#333333', linewidth=2.0, marker='o', markersize=5,
            markerfacecolor='white', markeredgewidth=1.6, zorder=5,
            label=f'均值（{len(spots)} 钓点）')
    for xi, v in zip(x, mean):
        ax.annotate(f'{v:.0f}', (xi, v), textcoords='offset points', xytext=(0, 9),
                    ha='center', fontproperties=CN, fontsize=8.5, color='#333333')

    ax.set_xticks(x)
    ax.set_xticklabels([f'{m}月' for m in months], fontproperties=CN, fontsize=10.5)
    ax.set_ylabel('期望收益（铃钱 / 次）', fontproperties=CN, fontsize=11)
    ax.set_title(f'{label} · 每月每钓点期望收益（北半球）', fontproperties=CN,
                 fontsize=15, pad=16, loc='left')
    ax.grid(axis='y', color='#E6E6E6', linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        ax.spines[sp].set_color('#CCCCCC')
    ax.legend(prop=CN, fontsize=10, frameon=False, ncol=len(spots) + 1, loc='upper left')
    ax.set_ylim(0, max(max(data[s]) for s in spots) * 1.18)

    ax.annotate('口径：期望收益 = Σ(Weight×Price) / ΣWeight，再对 白天/晨昏/夜晚 三档取平均；'
                '钓点鱼池由「水域表」决定',
                xy=(0, 0), xytext=(0, -0.13), xycoords='axes fraction',
                textcoords='axes fraction', fontproperties=CN, fontsize=9,
                color='#888888', va='top')

    plt.tight_layout(rect=[0, 0.05, 1, 0.98])
    fig.savefig(outpath, dpi=170, facecolor='#FFFFFF', bbox_inches='tight')
    plt.close(fig)
    print('saved:', outpath)


def draw_heat(label, spots, months, data, outpath):
    M = np.array([data[s] for s in spots], dtype=float)
    rows = len(spots)
    fig, ax = plt.subplots(figsize=(13.5, 1.5 + rows * 0.95))
    fig.patch.set_facecolor('#FFFFFF')
    cmap = plt.cm.YlOrRd
    vmin, vmax = M.min(), M.max()
    norm = (M - vmin) / (vmax - vmin) if vmax > vmin else np.zeros_like(M)

    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                       facecolor=cmap(0.15 + 0.8 * norm[i, j]),
                                       edgecolor='white', linewidth=1.2))
            ax.text(j, i, f'{v:.0f}', ha='center', va='center',
                    fontproperties=CN, fontsize=10,
                    color='white' if norm[i, j] > 0.62 else '#2A2F38',
                    fontweight='bold' if norm[i, j] > 0.62 else 'normal')

    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(rows - 0.5, -0.5)
    ax.set_xticks(range(12))
    ax.set_xticklabels([f'{m}月' for m in months], fontproperties=CN, fontsize=10.5)
    ax.set_yticks(range(rows))
    ax.set_yticklabels(spots, fontproperties=CN, fontsize=11)
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    ax.tick_params(length=0, pad=5)
    for sp in ax.spines.values():
        sp.set_visible(False)

    ax.set_title(f'{label} · 期望收益热力图（铃钱/次 · 颜色越深越高）', fontproperties=CN,
                 fontsize=14, pad=30, loc='left')

    for j in range(12):
        best = int(np.argmax(M[:, j]))
        ax.add_patch(plt.Rectangle((j - 0.5, best - 0.5), 1, 1, fill=False,
                                   edgecolor='#111111', linewidth=2.2, zorder=5))

    ax.annotate('黑框 = 该月期望收益最高的钓点',
                xy=(0, 0), xytext=(0, -0.05 - 0.03 / rows - 0.03), xycoords='axes fraction',
                textcoords='axes fraction', fontproperties=CN, fontsize=9.5,
                color='#777777', va='top')

    plt.tight_layout(rect=[0, 0.07, 1, 0.90])
    fig.savefig(outpath, dpi=170, facecolor='#FFFFFF', bbox_inches='tight')
    plt.close(fig)
    print('saved:', outpath)


if __name__ == '__main__':
    spot_map, recs = load_all()
    for label, spots in GROUPS.items():
        months, data, mean, EV = compute(spots, spot_map, recs)
        export_csv(label, spots, EV)
        draw_bar(label, spots, months, data, mean,
                 OUT_DIR + f'{label}期望收益_分组柱状.png')
        draw_heat(label, spots, months, data,
                  OUT_DIR + f'{label}期望收益_热力图.png')
