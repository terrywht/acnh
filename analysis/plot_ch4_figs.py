# -*- coding: utf-8 -*-
"""
plot_ch4_figs.py —— 总结章配图
图15 六个条件的分工
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager

FONT = 'C:/Windows/Fonts/msyh.ttc'
font_manager.fontManager.addfont(FONT)
plt.rcParams['font.family'] = font_manager.FontProperties(fname=FONT).get_name()
plt.rcParams['axes.unicode_minus'] = False

OUT = 'C:/Users/Administrator/WorkBuddy/acnh/analysis/'
INK = '#2B2B2B'
SUB = '#5A6472'


def box(ax, x, y, w, h, title, sub='', fc='#FFFFFF', ec='#2E5FA3', tc=INK,
        fs=12, sfs=9.2, lw=1.6, ls='-'):
    p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.008,rounding_size=0.018',
                       fc=fc, ec=ec, lw=lw, ls=ls, zorder=3)
    ax.add_patch(p)
    if sub:
        ax.text(x + w / 2, y + h * 0.62, title, ha='center', va='center',
                fontsize=fs, color=tc, zorder=4, fontweight='bold')
        ax.text(x + w / 2, y + h * 0.29, sub, ha='center', va='center',
                fontsize=sfs, color=tc, zorder=4)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha='center', va='center',
                fontsize=fs, color=tc, zorder=4, fontweight='bold')


def arrow(ax, p1, p2, color='#7A8592', lw=1.5, ls='-', rad=0.0):
    a = FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=13,
                        color=color, lw=lw, ls=ls, zorder=2,
                        connectionstyle='arc3,rad=%s' % rad)
    ax.add_patch(a)


def fig15():
    fig, ax = plt.subplots(figsize=(12.4, 5.6), dpi=160)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 三个开关
    for i, (t, s) in enumerate([('地点', '按标签筛池子'),
                                ('月份', '开或关'),
                                ('当日时间', '开或关')]):
        box(ax, 0.02, 0.72 - i * 0.24, 0.15, 0.16, t, s,
            fc='#EAF0F7', ec='#2E5FA3', tc='#1E4470', fs=13, sfs=9)
        arrow(ax, (0.17, 0.80 - i * 0.24), (0.235, 0.56), color='#9AA3AE', lw=1.2)

    # 池子
    box(ax, 0.235, 0.36, 0.215, 0.34,
        '池子', '当月当刻在场的鱼\n十几条 + 几件垃圾',
        fc='#2E5FA3', ec='#2E5FA3', tc='white', fs=14, sfs=9.6)

    # 抽签
    box(ax, 0.50, 0.36, 0.20, 0.34,
        '按权重抽签', '分母是池子的权重合计\n不一定是 100',
        fc='#C96A1E', ec='#C96A1E', tc='white', fs=13, sfs=9.4)

    # 结果
    box(ax, 0.75, 0.36, 0.20, 0.34,
        '一条鱼', '权重越大的越常来',
        fc='#FFFFFF', ec='#2B2B2B', tc=INK, fs=13, sfs=9.4)

    arrow(ax, (0.45, 0.53), (0.50, 0.53), lw=2)
    arrow(ax, (0.70, 0.53), (0.75, 0.53), lw=2)

    # 影子（投影）
    box(ax, 0.725, 0.80, 0.25, 0.145,
        '影子', '把结果提前投到水面上',
        fc='#FBEDEA', ec='#B03A2E', tc='#8B2E2E', fs=12.5, sfs=9.2, ls='--')
    arrow(ax, (0.85, 0.70), (0.85, 0.80), color='#B03A2E', lw=1.4, ls='--')

    # 岛屿（换池）
    box(ax, 0.235, 0.08, 0.215, 0.155,
        '岛屿限制', '整池换人，抽法不变',
        fc='#EAF4EE', ec='#2F8F4E', tc='#1E6B3A', fs=12, sfs=9, ls='--')
    arrow(ax, (0.3425, 0.235), (0.3425, 0.36), color='#2F8F4E', lw=1.4, ls='--')

    # 说明
    ax.text(0.50, 0.24, '只有这一步在真正抽签', fontsize=10, color='#A9530F',
            va='top')
    ax.text(0.75, 0.24, '影子是结果的前投影，\n不参与计算', fontsize=10,
            color='#8B2E2E', va='top', linespacing=1.7)

    fig.tight_layout()
    fig.savefig(OUT + '图15_六因子分工.png', bbox_inches='tight', facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    fig15()
    print('done')
