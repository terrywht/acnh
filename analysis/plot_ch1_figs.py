"""第一章配图：六钓点覆盖关系 + 九档影子对照"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.font_manager import FontProperties

CN = FontProperties(fname=r'C:/Windows/Fonts/msyh.ttc')
OUT = r'C:/Users/Administrator/WorkBuddy/acnh/analysis'

RIVER = '#2E5FA3'
SEA = '#C96A1E'
TRASH = '#8C8C8C'

# ---------- 图 1：标签 → 钓点 ----------
TAGS = [
    ('河流', 27, 'r'), ('池塘', 12, 'r'), ('悬崖上', 4, 'r'), ('出海口', 3, 'r'),
    ('所有河', 4, 't'), ('大海', 30, 's'), ('栈桥', 4, 's'), ('所有海', 4, 't'),
]
SPOTS = [
    ('河流', 31, 'r'), ('池塘', 16, 'r'), ('悬崖上', 35, 'r'), ('出海口', 34, 'r'),
    ('大海', 34, 's'), ('栈桥', 38, 's'),
]
MAP = {
    '河流': ['河流', '悬崖上', '出海口'],
    '池塘': ['池塘'],
    '悬崖上': ['悬崖上'],
    '出海口': ['出海口'],
    '所有河': ['河流', '池塘', '悬崖上', '出海口'],
    '大海': ['大海', '栈桥'],
    '栈桥': ['栈桥'],
    '所有海': ['大海', '栈桥'],
}


def color_of(kind):
    return {'r': RIVER, 's': SEA, 't': TRASH}[kind]


def draw_cover(outpath):
    fig, ax = plt.subplots(figsize=(12.4, 8.9))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 8.9)
    ax.axis('off')

    lx, rx = 1.55, 7.35
    ly = [6.95, 6.10, 5.25, 4.40, 3.55, 2.70, 1.85, 1.00]
    ry = [6.85, 5.70, 4.55, 3.40, 2.25, 1.10]

    tagpos = {t: y for (t, _, _), y in zip(TAGS, ly)}
    spotpos = {s: y for (s, _, _), y in zip(SPOTS, ry)}

    # 连线
    for tag, _, kind in TAGS:
        for spot in MAP[tag]:
            ax.add_patch(FancyArrowPatch(
                (lx + 0.72, tagpos[tag]), (rx - 0.72, spotpos[spot]),
                connectionstyle='arc3,rad=0.18', arrowstyle='-',
                linewidth=1.5, color=color_of(kind), alpha=0.55, zorder=1))

    # 左：标签
    for tag, n, kind in TAGS:
        y = tagpos[tag]
        c = color_of(kind)
        ax.add_patch(FancyBboxPatch((lx - 0.72, y - 0.27), 1.44, 0.54,
                                    boxstyle='round,pad=0.05,rounding_size=0.12',
                                    facecolor=c, edgecolor='none', zorder=3,
                                    alpha=0.92))
        ax.text(lx, y, f'{tag}  {n}', fontproperties=CN, fontsize=11.5,
                ha='center', va='center', color='white', zorder=4)

    # 右：钓点
    for spot, n, kind in SPOTS:
        y = spotpos[spot]
        c = color_of(kind)
        ax.add_patch(FancyBboxPatch((rx - 0.72, y - 0.31), 1.44, 0.62,
                                    boxstyle='round,pad=0.05,rounding_size=0.12',
                                    facecolor='white', edgecolor=c, linewidth=2.0, zorder=3))
        ax.text(rx, y + 0.06, spot, fontproperties=CN, fontsize=12,
                ha='center', va='center', color=c, zorder=4)
        ax.text(rx, y - 0.19, f'{n} 种候选', fontproperties=CN, fontsize=8.5,
                ha='center', va='center', color='#777777', zorder=4)

    # 标题与注
    ax.text(0.35, 8.55, '八个标签，六个钓点', fontproperties=CN, fontsize=17)
    ax.text(0.35, 8.13, '每条鱼只挂一个标签，标签决定它能在哪些位置出现',
            fontproperties=CN, fontsize=10, color='#777777')

    # 归属说明
    ax.text(lx, 0.56, '挂标签的鱼', fontproperties=CN, fontsize=10,
            ha='center', color='#555555')
    ax.text(rx, 0.56, '钓点看到的池子', fontproperties=CN, fontsize=10,
            ha='center', color='#555555')

    # 图例注释
    ax.plot([8.78, 8.95], [1.55, 1.55], color=TRASH, linewidth=2.6)
    ax.text(9.05, 1.55, '所有河 / 所有海：各 4 条\n全部是垃圾',
            fontproperties=CN, fontsize=9, va='center', color='#7A7A7A')

    ax.annotate('栈桥把全部海鱼都包了\n34 + 4 = 38 种',
                xy=(rx + 0.75, 1.10), xytext=(9.05, 0.32),
                fontproperties=CN, fontsize=9, color=SEA,
                arrowprops=dict(arrowstyle='-', color=SEA, linewidth=0.9,
                                connectionstyle='arc3,rad=0.22'))

    ax.annotate('池塘只有 16 种候选\n是全场最小的池子',
                xy=(rx + 0.75, 5.70), xytext=(9.05, 6.95),
                fontproperties=CN, fontsize=9, color=RIVER,
                arrowprops=dict(arrowstyle='-', color=RIVER, linewidth=0.9,
                                connectionstyle='arc3,rad=-0.22'))

    plt.tight_layout()
    fig.savefig(outpath, dpi=170, facecolor='#FFFFFF', bbox_inches='tight')
    plt.close(fig)
    print('saved:', outpath)


# ---------- 图 2：九档影子 ----------
def draw_shadow(outpath):
    fig, ax = plt.subplots(figsize=(12.6, 5.2))
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 5.2)
    ax.axis('off')

    COL = {'n': '#3D5A80', 'f': '#C96A1E', 'u': '#3F7D6A'}
    # (标号, 底部描述, [(标签, 条数, 类型)])
    CELLS = [
        ('1', '最小', [('SS', 13, 'n')]),
        ('2', '小', [('S', 17, 'n')]),
        ('3', '中', [('M', 13, 'n')]),
        ('4', '中', [('L', 12, 'n'), ('K', 1, 'f')]),
        ('5', '大', [('LL', 10, 'n')]),
        ('6', '最大', [('LLL', 7, 'n'), ('J', 5, 'f')]),
    ]
    W, GAP = 1.26, 0.235
    x0 = 1.30
    top, bot = 3.86, 1.92

    for idx, (num, desc, items) in enumerate(CELLS):
        cx = x0 + W / 2 + idx * (W + GAP)
        ax.text(cx, 4.16, num, fontproperties=CN, fontsize=15,
                ha='center', va='center', color='#222222')
        ax.text(cx, 1.62, desc, fontproperties=CN, fontsize=9,
                ha='center', va='center', color='#8C8C8C')

        n = len(items)
        if n == 1:
            slots = [(bot, top, items[0])]
        else:
            h = (top - bot - 0.06) / 2
            slots = [(bot + h + 0.06, top, items[1]), (bot, bot + h, items[0])]
        for b, t, (name, cnt, kind) in slots:
            ax.add_patch(FancyBboxPatch((cx - W / 2, b), W, t - b,
                                        boxstyle='round,pad=0.02,rounding_size=0.08',
                                        facecolor=COL[kind], edgecolor='none', zorder=3))
            ax.text(cx, (b + t) / 2 + 0.11, name, fontproperties=CN, fontsize=13,
                    ha='center', va='center', color='white', zorder=4)
            ax.text(cx, (b + t) / 2 - 0.17, f'{cnt} 条', fontproperties=CN, fontsize=8.5,
                    ha='center', va='center', color='white', zorder=4, alpha=0.9)

    # 细长
    ux = x0 + 6 * (W + GAP) + 0.55
    ax.text(ux + 0.48, 4.16, '—', fontproperties=CN, fontsize=15,
            ha='center', va='center', color='#222222')
    ax.add_patch(FancyBboxPatch((ux, bot), 0.96, top - bot,
                                boxstyle='round,pad=0.02,rounding_size=0.08',
                                facecolor=COL['u'], edgecolor='none', zorder=3))
    ax.text(ux + 0.48, (bot + top) / 2 + 0.11, 'U', fontproperties=CN, fontsize=13,
            ha='center', va='center', color='white', zorder=4)
    ax.text(ux + 0.48, (bot + top) / 2 - 0.17, '2 条', fontproperties=CN, fontsize=8.5,
            ha='center', va='center', color='white', zorder=4, alpha=0.9)
    ax.text(ux + 0.48, 1.62, '细长·无标号', fontproperties=CN, fontsize=9,
            ha='center', va='center', color='#8C8C8C')

    # 轴标签
    ax.text(x0 - 0.72, (bot + top) / 2, '体型\n标号', fontproperties=CN, fontsize=9.5,
            ha='center', va='center', color='#8C8C8C', linespacing=1.5)

    # 标题
    ax.text(0.35, 4.92, '九个影子标签，对回真正的尺寸', fontproperties=CN, fontsize=16)
    ax.text(0.35, 4.58, '格子里的数字是第三方数据给的体量标号，1 最小、6 最大',
            fontproperties=CN, fontsize=9.5, color='#777777')

    # 说明
    notes = [
        ('J 和 LLL 挤在同一个格子里', '都是 6，J 只多了鳍，不是「比 LLL 小一点」', COL['f']),
        ('K 挂在 4 号格，和 L 同档', '全游戏只有吸盘鱼一条，远没那么大', COL['f']),
        ('U 不在尺寸序列里', '裸胸鳝、五彩鳗，标的是形状不是大小', COL['u']),
    ]
    for i, (main, sub, c) in enumerate(notes):
        y = 1.12 - i * 0.34
        ax.plot([0.55, 0.74], [y + 0.03, y + 0.03], color=c, linewidth=2.2)
        ax.text(0.84, y, main, fontproperties=CN, fontsize=10, va='center', color=c)
        ax.text(3.42, y, sub, fontproperties=CN, fontsize=9.2, va='center', color='#777777')

    plt.tight_layout()
    fig.savefig(outpath, dpi=170, facecolor='#FFFFFF', bbox_inches='tight')
    plt.close(fig)
    print('saved:', outpath)


if __name__ == '__main__':
    draw_cover(f'{OUT}/六钓点覆盖关系.png')
    draw_shadow(f'{OUT}/九档影子对照.png')
