# -*- coding: utf-8 -*-
"""
plot_ch2_figs.py —— 第二章配图
图07 夏天摊薄：鱼种数 vs 每鱼平均权重
图09 月份相似度矩阵（Jaccard）
图09 窗口长度与售价
"""
import csv
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

FONT = 'C:/Windows/Fonts/msyh.ttc'
font_manager.fontManager.addfont(FONT)
plt.rcParams['font.family'] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams['axes.unicode_minus'] = False

OUT = 'C:/Users/Administrator/WorkBuddy/acnh/analysis/'
MONTHS = list(range(1, 13))
RIVER = '#2E5FA3'
SEA = '#C96A1E'
GRID = '#D9DEE5'

# 数据（来自 ch2.txt / ch2_extra.txt）
R_CNT = [16, 16, 20, 21, 27, 33, 32, 32, 37, 26, 21, 17]
S_CNT = [15, 15, 15, 18, 17, 22, 26, 28, 26, 16, 16, 15]
R_AVG = [5.88, 5.88, 4.70, 4.48, 3.48, 2.85, 2.94, 2.94, 2.54, 3.62, 4.48, 5.53]
S_AVG = [6.33, 6.33, 6.33, 5.28, 5.59, 4.32, 3.65, 3.39, 3.65, 5.94, 5.94, 6.33]


def style(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#9AA3AE')
    ax.spines['bottom'].set_color('#9AA3AE')
    ax.grid(axis='y', color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)


def fig07():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), dpi=160)
    for ax, cnt, avg, color, name in [
            (axes[0], R_CNT, R_AVG, RIVER, '河鱼'),
            (axes[1], S_CNT, S_AVG, SEA, '海鱼')]:
        ax.bar(MONTHS, cnt, color=color, alpha=0.85, width=0.68, zorder=2,
               label='当月能钓到几种鱼（左轴）')
        style(ax)
        ax.set_ylim(0, max(cnt) * 1.30)
        ax.set_xticks(MONTHS)
        ax.set_xticklabels(['%d' % m for m in MONTHS])
        ax.set_xlabel('月份')
        ax.set_ylabel('能钓到几种鱼' if name == '河鱼' else '')
        for x, y in zip(MONTHS, cnt):
            ax.text(x, y + 0.7, str(y), ha='center', va='bottom', fontsize=9, color=color)

        ax2 = ax.twinx()
        ax2.plot(MONTHS, avg, color='#3A3A3A', lw=2.1, marker='o', ms=5, zorder=5)
        ax2.set_ylim(0, max(avg) * 1.30)
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.tick_params(axis='y', colors='#3A3A3A', labelsize=8.5)
        # 只在两端标数值，避免与柱标冲突
        for x in (1, 12):
            ax2.text(x, avg[x - 1] + 0.30, '%.1f' % avg[x - 1], ha='center', va='bottom',
                     fontsize=9, color='#3A3A3A',
                     bbox=dict(fc='white', ec='none', alpha=0.75, pad=1.2))
        low = avg.index(min(avg)) + 1
        ax2.text(low, min(avg) - 0.38, '%.1f' % min(avg), ha='center', va='top',
                 fontsize=9, color='#C0392B', fontweight='bold',
                 bbox=dict(fc='white', ec='none', alpha=0.8, pad=1.2))
        ax.set_title('%s：鱼最多的月份，每条分到的权重最少' % name, fontsize=13, pad=26)
        ax.text(0.5, 1.035, '柱 = 当月能钓到几种鱼（左轴）　　线 = 每条鱼的平均权重（右轴）',
                transform=ax.transAxes, ha='center', va='bottom', fontsize=9.2, color='#5A6675')
    fig.tight_layout(w_pad=3.4)
    fig.savefig(OUT + '图07_夏天摊薄.png', bbox_inches='tight', facecolor='white')
    plt.close(fig)


def fig08():
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.6), dpi=160)
    for ax, fn, name in [(axes[0], 'jaccard_river.csv', '河鱼'),
                         (axes[1], 'jaccard_sea.csv', '海鱼')]:
        mat = []
        for r in list(csv.reader(io.open(OUT + fn, encoding='utf-8')))[1:]:
            mat.append([float(x) for x in r[1:]])
        arr = np.array(mat)
        im = ax.imshow(arr, cmap='YlGnBu', vmin=0.2, vmax=1.0)
        ax.set_xticks(range(12))
        ax.set_yticks(range(12))
        ax.set_xticklabels(['%d' % m for m in MONTHS], fontsize=8)
        ax.set_yticklabels(['%d' % m for m in MONTHS], fontsize=8)
        ax.set_xlabel('月份')
        ax.set_ylabel('月份')
        ax.set_title('%s：两个月的鱼种重合度（1 = 完全相同）' % name, fontsize=12.5, pad=10)
        for i in range(12):
            for j in range(12):
                v = arr[i, j]
                ax.text(j, i, '%.2f' % v, ha='center', va='center', fontsize=6.4,
                        color='white' if v > 0.72 else '#333333')
        for k in range(12):
            ax.add_patch(plt.Rectangle((k - 0.5, k - 0.5), 1, 1, fill=False,
                                       edgecolor='#C0392B', lw=1.1))
        cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        cb.ax.tick_params(labelsize=8)
        cb.set_label('鱼种重合度', fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT + '图09_月份相似度.png', bbox_inches='tight', facecolor='white')
    plt.close(fig)


def fig09():
    # 一年能钓几个月 -> (几条鱼, 平均售价, 中位售价)
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 12]
    cnt = [2, 2, 8, 17, 7, 14, 5, 4, 3, 18]
    avgp = [1250, 6875, 1931, 7231, 957, 3696, 4020, 850, 5167, 2641]

    fig, ax = plt.subplots(figsize=(10.2, 5.4), dpi=160)
    colors = ['#2E5FA3'] * len(data)
    colors[data.index(4)] = '#B03A2E'
    bars = ax.bar(range(len(data)), avgp, color=colors, width=0.62, zorder=2)
    style(ax)
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels(['%d 个月' % d for d in data], fontsize=9.5)
    ax.set_ylabel('这一档鱼的平均售价（铃钱）')
    ax.set_ylim(0, 9000)
    ax.set_title('窗口正好四个月的鱼，最贵', fontsize=13.5, pad=14)
    for b, v, n in zip(bars, avgp, cnt):
        ax.text(b.get_x() + b.get_width() / 2, v + 90, '%d' % v, ha='center', va='bottom',
                fontsize=9.2, fontweight='bold', color='#2B2B2B')
        ax.text(b.get_x() + b.get_width() / 2, 150, 'n=%d' % n, ha='center', va='bottom',
                fontsize=8.6, color='white')
    ax.annotate('17 条鱼挤在这一档：\n鲨鱼、鲸鲨、锯鲨、黄金河虎、\n远东哲罗鱼、骨舌鱼……',
                xy=(data.index(4) + 0.34, 7180), xytext=(data.index(4) + 1.05, 8300),
                fontsize=9.2, color='#8B2E2E', va='top',
                arrowprops=dict(arrowstyle='->', color='#8B2E2E', lw=1.2))
    fig.tight_layout()
    fig.savefig(OUT + '图08_窗口长度与售价.png', bbox_inches='tight', facecolor='white')
    plt.close(fig)


def fig10():
    r = [53.5, 53.5, 50.7, 50.4, 42.9, 43.3, 40.1, 41.5, 23.0, 49.3, 51.4, 53.5]
    s_ = [54.7, 54.7, 53.3, 46.3, 54.7, 50.5, 42.5, 40.7, 45.6, 57.9, 55.8, 54.7]
    fig, ax = plt.subplots(figsize=(9.8, 5.3), dpi=160)
    ax.axhspan(0, 60, color='#F3F6F9', zorder=0)
    ax.plot(MONTHS, r, color=RIVER, lw=2.4, marker='o', ms=6, label='河鱼系的 11 条常驻鱼', zorder=4)
    ax.plot(MONTHS, s_, color=SEA, lw=2.4, marker='s', ms=5.5, label='海鱼系的 7 条常驻鱼', zorder=4)
    ax.axhline(50, color='#9AA3AE', lw=1, ls=':', zorder=1)
    ax.text(0.78, 50.9, '50% 参考线', fontsize=8.4, color='#7A8592', va='bottom')
    style(ax)
    ax.set_xticks(MONTHS)
    ax.set_xticklabels(['%d' % m for m in MONTHS])
    ax.set_xlim(0.6, 12.9)
    ax.set_ylim(0, 62)
    ax.set_xlabel('月份')
    ax.set_ylabel('常驻鱼占当月总权重的比例（%）')
    ax.set_title('旺季一到，常驻鱼把权重让出去', fontsize=13.5, pad=14)
    for x, y in zip(MONTHS, r):
        ax.text(x, y - 3.2, '%.0f' % y, ha='center', va='top', fontsize=8.4, color=RIVER)
    for x, y in zip(MONTHS, s_):
        ax.text(x, y + 1.6, '%.0f' % y, ha='center', va='bottom', fontsize=8.4, color=SEA)
    ax.annotate('9 月河鱼 37 种，\n常驻鱼只剩 23%',
                xy=(9, 23.0), xytext=(7.4, 12.5), fontsize=9.4, color='#8B2E2E',
                arrowprops=dict(arrowstyle='->', color='#8B2E2E', lw=1.2))
    ax.legend(loc='lower left', frameon=False, fontsize=9.4, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT + '图10_常驻鱼让位.png', bbox_inches='tight', facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    fig07()
    fig08()
    fig09()
    fig10()
    print('ok')
