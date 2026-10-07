# -*- coding: utf-8 -*-
"""
deep9_rarity_river_sea.py
在 ACNH 原版参数表上重建权威基线，并做「稀有度 × 河海」专项分析。

数据源（data/，来自 https://wuffs.org/acnh/bcsv_130/csv/）：
  FishAppearRiverParam.csv  河流系出现权重（ItemID × 半球 × 12月 × 3时段）
  FishAppearSeaParam.csv    海洋系出现权重（同上）
  FishStatusParam.csv       鱼状态参数（AppearType / ShadowType / BuoyLv / ...）

外部对照：桌面 fish.json（ACNHAPI 社区数据）提供 4 档 rarity 标签 + 日文名
对齐方式：FishStatusParam.DebugName(日文名) ↔ fish.json.name-JPja（80/85 命中）

口径（用户指定）：
  时段 = 白天(9-16) / 晨昏(5-8 & 17-20) / 夜晚(18-4)，各 8 小时
  归属 = 以原表为准（河海严格分开）
"""
import csv, io, json, os, re, collections, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FISH_JSON = r"C:\Users\Administrator\Desktop\fish.json"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MN = {m: i + 1 for i, m in enumerate(MONTHS)}
TIDX = {"Daytime": 0, "MorningAndEvening": 1, "Night": 2}
TN = {0: "白天", 1: "晨昏", 2: "夜晚"}
RI = {"Common": 1, "Uncommon": 2, "Rare": 3, "Ultra-rare": 4}
OUT = []


def p(*a):
    s = " ".join(str(t) for t in a)
    OUT.append(s)
    print(s)


def load_csv(name):
    rows = list(csv.reader(io.open(os.path.join(DATA, name), encoding="utf-8")))
    return rows[0], [r for r in rows[1:] if any(r)]


def q(s):
    return re.findall(r"'([^']*)'", s)


def pear(x, y):
    n = len(x)
    if n < 2:
        return 0.0
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    return num / den if den else 0.0


# ---------------- 载入 ----------------
sh, sd = load_csv("FishStatusParam.csv")
I = {n: sh.index(n) for n in ["ItemID", "AppearType", "BuoyLv", "ShadowType",
                              "Label", "DebugName", "IsCreateBait", "UniqueID"]}
status = {}
for r in sd:
    status[int(r[I["ItemID"]])] = dict(
        atype=q(r[I["AppearType"]])[0], shadow=q(r[I["ShadowType"]])[0],
        buoy=q(r[I["BuoyLv"]])[0], label=r[I["Label"]].strip("'"),
        jp=r[I["DebugName"]].strip("'"), bait=int(r[I["IsCreateBait"]]),
        uid=int(r[I["UniqueID"]]),
    )

fish = json.load(io.open(FISH_JSON, encoding="utf-8"))
jp2zh = {v["name"]["name-JPja"]: v["name"]["name-CNzh"] for v in fish.values()}
rarity = {v["name"]["name-CNzh"]: v["availability"]["rarity"] for v in fish.values()}
price = {v["name"]["name-CNzh"]: v["price"] for v in fish.values()}
item2zh = {i: jp2zh[s["jp"]] for i, s in status.items() if s["jp"] in jp2zh}
junk = [i for i in status if i not in item2zh]


def load_appear(fname):
    h, d = load_csv(fname)
    col = {}
    for i, c in enumerate(h):
        m = re.match(r"Prob(\w+?)(Daytime|MorningAndEvening|Night)$", c)
        if m:
            col[(m.group(1), m.group(2))] = i
    ac = h.index("AppearArea")
    out = {}
    for r in d:
        rec = {}
        for mo in MONTHS:
            for t, ti in TIDX.items():
                rec[(mo, ti)] = float(r[col[(mo, t)]])
        out[(int(r[0]), int(r[ac]))] = rec
    return out


river, sea = load_appear("FishAppearRiverParam.csv"), load_appear("FishAppearSeaParam.csv")


def agg(tbl, area=0):
    a = {}
    for (item, ar), rec in tbl.items():
        if ar != area:
            continue
        f = a.setdefault(item, dict(months=set(), times=set(), w={}))
        for (mo, ti), w in rec.items():
            if w > 0:
                f["months"].add(mo)
                f["times"].add(ti)
                f["w"][(mo, ti)] = w
    return a


R, S = agg(river), agg(sea)
ri, si = {i for (i, a) in river}, {i for (i, a) in sea}

p("=" * 78)
p("【0】数据基准")
p("=" * 78)
p(f"  FishStatusParam : {len(status)} 条（含 4 垃圾 + 1 鱼卵）")
p(f"  RiverParam      : {len(river)//2} 种 × 2 半球")
p(f"  SeaParam        : {len(sea)//2} 种 × 2 半球")
p(f"  fish.json 对齐  : {len(item2zh)}/{len(status)}（未匹配均为非鱼道具: "
  f"{[status[i]['label'] for i in junk]}）")
p(f"  归属：只河 {len(ri-si)} / 只海 {len(si-ri)} / 两表皆有 {len(ri&si)}")
amb = collections.defaultdict(list)
for i in sorted(ri & si):
    amb[status[i]["atype"]].append(item2zh.get(i, status[i]["label"]))
for k, v in amb.items():
    p(f"    两表皆有·{k}: {v}")
p()

# ---------------- 1. 时段模型校验 ----------------
p("=" * 78)
p("【1】时段模型校验：三档 8 小时制")
p("=" * 78)
allw = {}
for tag, A in [("河", R), ("海", S)]:
    for item, f in A.items():
        for (mo, ti), w in f["w"].items():
            allw.setdefault(item, set()).add(ti)
cnt = collections.Counter(len(v) for v in allw.values())
p(f"  鱼的活跃时段组合数分布：{dict(sorted(cnt.items()))}")
p(f"    → 1 档 {cnt[1]} 种 / 2 档 {cnt[2]} 种 / 3 档 {cnt[3]} 种（共 {sum(cnt.values())} 种鱼）")
p()
for t in [0, 1, 2]:
    n = sum(1 for v in allw.values() if v == {t})
    if n:
        who = [item2zh.get(i, status[i]["label"]) for i, v in allw.items()
               if v == {t} and i in item2zh]
        p(f"  仅 {TN[t]}（1 档）{n} 种：{'、'.join(who)}")
p()

# ---------------- 2. 影子档（原表实测）----------------
p("=" * 78)
p("【2】影子档：原表 ShadowType 实测 9 档")
p("=" * 78)
seg = {}
for i in status:
    seg[i] = "河" if i in ri else ("海" if i in si else "?")
cnt = collections.Counter(status[i]["shadow"] for i in status if i in item2zh)
p(f"  {dict(sorted(cnt.items(), key=lambda x: -x[1]))}")
p()
p(f"  {'档':<5}{'总数':>4}{'河':>4}{'海':>4}   {'河均价':>8}{'海均价':>8}")
for s in ["SS", "S", "M", "L", "LL", "LLL", "J", "K", "U"]:
    items = [i for i in status if status[i]["shadow"] == s and i in item2zh]
    r_ = [i for i in items if seg[i] == "河"]
    h_ = [i for i in items if seg[i] == "海"]
    pr = lambda L: (sum(price[item2zh[i]] for i in L) // len(L)) if L else 0
    p(f"  {s:<5}{len(items):>4}{len(r_):>4}{len(h_):>4}   {pr(r_):>8}{pr(h_):>8}")
p()

# ---------------- 3. 稀有度 × 河海 ----------------
p("=" * 78)
p("【3】稀有度 × 河海  —— 逐档特征（核心）")
p("=" * 78)


def collect(A, tag):
    rows = []
    for item, f in A.items():
        zh = item2zh.get(item)
        if not zh:
            continue
        ws = list(f["w"].values())
        rows.append(dict(zh=zh, item=item, rarity=rarity[zh], seg=tag,
                         nmon=len(f["months"]), mon=sorted(MN[m] for m in f["months"]),
                         times=set(f["times"]), wmax=max(ws), wavg=st.mean(ws),
                         wsum=sum(ws), shadow=status[item]["shadow"],
                         atype=status[item]["atype"], buoy=status[item]["buoy"],
                         price=price[zh]))
    return rows


ALL = collect(R, "河") + collect(S, "海")
p(f"  河系 {sum(1 for x in ALL if x['seg']=='河')} 种 / 海系 {sum(1 for x in ALL if x['seg']=='海')} 种")
p()
for tag in ["河", "海"]:
    sub = [x for x in ALL if x["seg"] == tag]
    p("-" * 78)
    p(f"### {tag}系（{len(sub)} 种）")
    p(f"  {'稀有度':<11}{'n':>3}{'占比':>7}{'月数均值':>9}{'时段均值':>9}"
      f"{'wmax均值':>9}{'wavg均值':>9}{'均价':>8}")
    for r in ["Common", "Uncommon", "Rare", "Ultra-rare"]:
        g = [x for x in sub if x["rarity"] == r]
        if not g:
            p(f"  {r:<11}{0:>3}{'—':>7}")
            continue
        p(f"  {r:<11}{len(g):>3}{len(g)/len(sub)*100:>6.0f}%{st.mean(x['nmon'] for x in g):>9.1f}"
          f"{st.mean(len(x['times']) for x in g):>9.1f}{st.mean(x['wmax'] for x in g):>9.1f}"
          f"{st.mean(x['wavg'] for x in g):>9.1f}{int(st.mean(x['price'] for x in g)):>8}")
    p(f"  --- {tag}系 逐档明细 ---")
    for r in ["Common", "Uncommon", "Rare", "Ultra-rare"]:
        g = sorted([x for x in sub if x["rarity"] == r], key=lambda x: -x["wmax"])
        if not g:
            continue
        p(f"   [{r}] {len(g)} 种")
        for x in g:
            t = "".join(str(i) for i in sorted(x["times"]))
            p(f"     {x['zh']:<9} 影={x['shadow']:<4} 月={x['nmon']:>2}{str(x['mon']):<28} "
              f"段={t} wmax={x['wmax']:>4.0f} wavg={x['wavg']:>4.1f} ¥{x['price']:<6} {x['atype']}")
    p()

# ---------------- 4. 关键校验 ----------------
p("=" * 78)
p("【4】校验：标注稀有度 vs 真实权重 / 影子 / 窗口")
p("=" * 78)
p(f"  r(标注稀有度, 最高权重)  全部 = {pear([RI[x['rarity']] for x in ALL], [x['wmax'] for x in ALL]):.3f}")
for tag in ["河", "海"]:
    g = [x for x in ALL if x["seg"] == tag]
    p(f"     {tag}系 r = {pear([RI[x['rarity']] for x in g], [x['wmax'] for x in g]):.3f}  (n={len(g)})")
p(f"  r(标注稀有度, 价格)      全部 = {pear([RI[x['rarity']] for x in ALL], [x['price'] for x in ALL]):.3f}")
SIZE = {"SS": 1, "S": 2, "M": 3, "L": 4, "LL": 5, "LLL": 6, "J": 6, "K": 4, "U": 4}
p(f"  r(影子尺寸, 价格)        全部 = {pear([SIZE[x['shadow']] for x in ALL], [x['price'] for x in ALL]):.3f}")
p(f"  r(影子尺寸, 最高权重)    全部 = {pear([SIZE[x['shadow']] for x in ALL], [x['wmax'] for x in ALL]):.3f}")
p(f"  r(标注稀有度, 活跃月数)  全部 = {pear([RI[x['rarity']] for x in ALL], [x['nmon'] for x in ALL]):.3f}")
p()

# 档 × 影子 交叉
p("  --- 稀有度 × 影子档 交叉表 ---")
p(f"  {'稀有度':<11}" + "".join(f"{s:>6}" for s in ["SS","S","M","L","LL","LLL","J","K","U"]))
for r in ["Common", "Uncommon", "Rare", "Ultra-rare"]:
    row = collections.Counter(x["shadow"] for x in ALL if x["rarity"] == r)
    p(f"  {r:<11}" + "".join(f"{row.get(s,0):>6}" for s in ["SS","S","M","L","LL","LLL","J","K","U"]))
p()

# ---------------- 5. 未知鱼卵 ----------------
p("=" * 78)
p("【5】非鱼道具（FishStatusParam 中不属于 80 种鱼）")
p("=" * 78)
for i in junk:
    s = status[i]
    inr, ins = i in ri, i in si
    ws = []
    if inr:
        ws += list(R.get(i, {}).get("w", {}).values())
    if ins:
        ws += list(S.get(i, {}).get("w", {}).values())
    p(f"  ItemID={i:<6} {s['label']:<10} {s['jp']:<12} 影={s['shadow']:<4} "
      f"类型={s['atype']:<16} 河参数={'有' if inr else '无'} 海参数={'有' if ins else '无'} "
      f"权重max={max(ws) if ws else 0:.0f} 活跃月={len(R.get(i,{}).get('months',set()) | S.get(i,{}).get('months',set()))}")
p()

io.open(os.path.join(HERE, "deep9.txt"), "w", encoding="utf-8").write("\n".join(OUT))
print(f"\n[saved] analysis/deep9.txt ({len(OUT)} 行)")
