# -*- coding: utf-8 -*-
"""
plot_ch3_figs.py —— 第三章配图
图13 难度阶梯：浮标等级 / 警戒半径 与售价
图14 八种行为：鱼影在水里干什么
"""
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
RIVER = '#2E5FA3'
SEA = '#C96A1E'
GRID = '#D9DEE5'
INK = '#2B2B2B'


def style(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#9AA3AE')
    ax.spines['bottom'].set_color('#9AA3AE')
    ax.grid(axis='y', color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)


def fig13():
    # 档位（0 最难 → 4 最好对付）-> (条数, 均价, 中位)
    lv = [(14, 11464, 11500), (22, 4266, 3900), (12, 1196, 800),
          (21, 1062, 500), (11, 781, 300)]
    sr = [(14, 8936, 9500), (18, 5058, 3775), (30, 2240, 1150),
          (11, 1041, 400), (7, 686, 200)]

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.1), dpi=160)
    for ax, data, name, note in [
            (axes[0], lv, '浮标等级', '档位越低，鱼越贵'),
            (axes[1], sr, '警戒半径', '半径越小，鱼越贵')]:
        vals = [d[1] for d in data]
        colors = ['#1F4470', '#2E5FA3', '#6E93BF', '#A8BFD6', '#D6E0EB']
        bars = ax.bar(range(5), vals, color=colors, width=0.64, zorder=2)
        style(ax)
        ax.set_xticks(range(5))
        ax.set_xticklabels(['0', '1', '2', '3', '4'], fontsize=11)
        ax.set_xlabel('%s（0 最难对付 → 4 最省心）' % name, fontsize=10.5)
        ax.set_ylabel('这一档鱼的平均售价（铃钱）' if name == '浮标等级' else '')
        ax.set_ylim(0, 13200)
        ax.set_title('%s：%s' % (name, note), fontsize=12.8, pad=12)
        for b, (n, avg, med) in zip(bars, data):
            cx = b.get_x() + b.get_width() / 2
            ax.text(cx, avg + 220, '{:,}'.format(avg), ha='center', va='bottom',
                    fontsize=10.5, fontweight='bold', color=INK)
            ax.text(cx, avg * 0.45, '%d 条' % n, ha='center', va='center',
                    fontsize=9.4, color='white' if avg > 2600 else '#3A4656')
    fig.tight_layout(w_pad=3.0)
    fig.savefig(OUT + '图13_难度阶梯.png', bbox_inches='tight', facecolor='white')
    plt.close(fig)


def fig14():
    # 行为 -> (条数, 均价, 钓点构成, 代表鱼)
    data = [
        ('回游 + 待机', 2, 7500, '海 2', '鳐鱼、锯鲨'),
        ('捕食者', 4, 6875, '栈桥 4', '旗鱼、鲔鱼、鬼头刀、白面弄鱼'),
        ('一直游（通常）', 34, 4555, '海 20 / 河 10 / 池 4', '香鱼、鲈鱼、鲫鱼'),
        ('抗水流', 14, 3593, '河 7 / 悬崖 4 / 出海口 3', '远东哲罗鱼、金鳟、鲟鱼'),
        ('待机不动', 10, 2372, '池 5 / 河 3 / 海 2', '黑鱼、拟鳄龟、皇带鱼'),
        ('追玩家', 2, 1900, '河 2', '食人鱼、孔雀鱼'),
        ('绕圈（巡视）', 13, 1862, '河 5 / 海 5 / 池 3', '金鱼、霓虹灯鱼、海马'),
        ('成群（大群）', 1, 200, '海 1', '凤尾鱼'),
    ]
    labels = [d[0] for d in data]
    vals = [d[2] for d in data]
    cnts = [d[1] for d in data]

    fig, ax = plt.subplots(figsize=(11.2, 5.6), dpi=160)
    colors = ['#8FB3D9', SEA, '#7FA8CC', RIVER, '#5C7791',
              '#B03A2E', '#9BB7D4', '#C9D4E0']
    y = np.arange(len(data))[::-1]
    bars = ax.barh(y, vals, color=colors, height=0.62, zorder=2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#9AA3AE')
    ax.spines['bottom'].set_color('#9AA3AE')
    ax.grid(axis='x', color=GRID, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlim(0, 8900)
    ax.set_xlabel('这一行为的鱼，平均售价（铃钱）')
    ax.set_title('鱼影在水里干什么：八种行为', fontsize=13.5, pad=14)
    for b, (lb, n, avg, area, eg), yy in zip(bars, data, y):
        cx = b.get_width()
        ax.text(cx + 140, yy + 0.16, '{:,}'.format(avg), va='center',
                fontsize=10.5, fontweight='bold', color=INK)
        ax.text(cx + 140, yy - 0.20, '%d 条　%s' % (n, area), va='center',
                fontsize=8.2, color='#5A6472')
    fig.tight_layout()
    fig.savefig(OUT + '图14_八种行为.png', bbox_inches='tight', facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    fig13()
    fig14()
    print('done')
