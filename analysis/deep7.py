# -*- coding: utf-8 -*-
# 补算: 归类法一(活跃月份数分组)完整数据 + Jaccard细节 + 逐月池子变化 + 影子档低高级分布
import openpyxl, collections, itertools, json
from pathlib import Path

DESK = Path(r"C:/Users/admin/Desktop")
wb = openpyxl.load_workbook(DESK/"动森钓鱼概率总表.xlsx", data_only=True)
ws = wb["Sheet1"]
rows = list(ws.iter_rows(values_only=True))
raw = [r for r in rows[1:] if r[0] is not None and str(r[5]).isdigit()]

LOC = ["河流","池塘","悬崖上","出海口","大海","栈桥"]
out=[]
def p(*a):
    s=" ".join(str(t) for t in a); out.append(s); print(s)

active=[]
for r in raw:
    if not r[7] or r[7]==0: continue
    locs={LOC[i]: r[9+i] for i in range(6)}
    active.append(dict(name=r[1], shadow=r[2], price=r[3], buoy=r[4], month=int(r[5]),
                       time=r[6], w=r[7], atype=r[8], loc=locs))

fish={}
for x in active:
    f=fish.setdefault(x["name"], dict(name=x["name"], shadow=x["shadow"], price=x["price"],
                                      months=set(), times=set(), locs=set(), atype=x["atype"]))
    f["months"].add(x["month"]); f["times"].add(x["time"])
    for k,v in x["loc"].items():
        if v: f["locs"].add(k)
for f in fish.values():
    f["seg"] = "河" if (f["locs"] & {"河流","池塘","悬崖上","出海口"}) else "海"

# ============ 1. 归类法一 完整数据 ============
p("="*70)
p("【1】归类法一: 按活跃月份数分组 —— 完整数据")
p("="*70)
buckets=collections.defaultdict(list)
for f in fish.values():
    n=len(f["months"])
    key = "1月 (单月鱼)" if n==1 else ("2-3月 (超短季)" if n<=3 else
          ("4-6月 (中季)" if n<=6 else ("7-9月 (长季)" if n<=9 else "10-12月 (常驻/准常驻)")))
    buckets[key].append(f)

order=["1月 (单月鱼)","2-3月 (超短季)","4-6月 (中季)","7-9月 (长季)","10-12月 (常驻/准常驻)"]
p(f"{'段位':<22}{'总数':>4}{'河':>4}{'海':>4}{'河均价':>9}{'海均价':>9}{'河最高价':>9}{'海最高价':>9}")
tot_all=0
for k in order:
    lst=buckets[k]; tot_all+=len(lst)
    h=[f for f in lst if f["seg"]=="河"]; s=[f for f in lst if f["seg"]=="海"]
    ha=sum(float(f["price"]) for f in h)/len(h) if h else 0
    sa=sum(float(f["price"]) for f in s)/len(s) if s else 0
    hmax=max((float(f["price"]) for f in h), default=0)
    smax=max((float(f["price"]) for f in s), default=0)
    p(f"{k:<22}{len(lst):>4}{len(h):>4}{len(s):>4}{ha:>9.0f}{sa:>9.0f}{hmax:>9.0f}{smax:>9.0f}")
p(f"{'合计':<22}{tot_all:>4}")

p()
p("--- 各段位 完整鱼名单 (河) ---")
for k in order:
    h=sorted([f for f in buckets[k] if f["seg"]=="河"], key=lambda z:-float(z["price"]))
    if not h: p(f"  [{k}] 无河鱼"); continue
    p(f"  [{k}] {len(h)}条: " + " | ".join(f"{f['name']}¥{f['price']}({f['shadow']},{len(f['months'])}月)" for f in h))
p()
p("--- 各段位 完整鱼名单 (海) ---")
for k in order:
    s=sorted([f for f in buckets[k] if f["seg"]=="海"], key=lambda z:-float(z["price"]))
    if not s: p(f"  [{k}] 无海鱼"); continue
    p(f"  [{k}] {len(s)}条: " + " | ".join(f"{f['name']}¥{f['price']}({f['shadow']},{len(f['months'])}月)" for f in s))

# 按精确月份数分布
p()
p("--- 精确活跃月份数 x 河海 交叉表 ---")
p(f"{'月数':>4}{'河':>4}{'海':>4}{'合计':>5}   河鱼名")
for n in range(1,13):
    h=[f for f in fish.values() if f["seg"]=="河" and len(f["months"])==n]
    s=[f for f in fish.values() if f["seg"]=="海" and len(f["months"])==n]
    if not h and not s: continue
    p(f"{n:>4}{len(h):>4}{len(s):>4}{len(h)+len(s):>5}   " + (", ".join(f["name"] for f in h[:8]) + ("..." if len(h)>8 else "")))

# ============ 2. Jaccard 细节 ============
p()
p("="*70)
p("【2】月度 Jaccard 相似度 —— 完整计算细节")
p("="*70)
moa={m:set() for m in range(1,13)}
for f in fish.values():
    for m in f["months"]: moa[m].add(f["name"])
p("--- 各月鱼种集合大小 ---")
for m in range(1,13): p(f"  {m:2d}月: |S|={len(moa[m]):2d} 种")
p()
p("--- 交集/并集明细 (相邻月) ---")
for m in range(1,12):
    a,b=moa[m],moa[m+1]
    inter=sorted(a&b); union=a|b
    p(f"  {m}月 vs {m+1}月: |A|={len(a)} |B|={len(b)} |A∩B|={len(inter)} |A∪B|={len(union)} J={len(inter)/len(union):.4f}")
p()
p("--- 全部月份对 Jaccard 排名 (前20高 / 前20低) ---")
pairs=[]
for i,j in itertools.combinations(range(1,13),2):
    a,b=moa[i],moa[j]; pairs.append((len(a&b)/len(a|b),i,j,len(a&b),len(a|b)))
pairs.sort(reverse=True)
p("  最高相似 Top10:")
for v,i,j,ii,uu in pairs[:10]:
    p(f"    {i:2d}月-{j:2d}月  J={v:.4f}  (交{ii}/并{uu})")
p("  最低相似 Top10:")
for v,i,j,ii,uu in pairs[-10:]:
    p(f"    {i:2d}月-{j:2d}月  J={v:.4f}  (交{ii}/并{uu})")

# ============ 3. 逐月池子变化 ============
p()
p("="*70)
p("【3】逐月河海池子变化 (环比上月)")
p("="*70)

def segset(m, seg):
    return {f["name"] for f in fish.values() if f["seg"]==seg and m in f["months"]}

# 总表口径: 每月每(月,时段)权重和=100 -> 计算每条鱼的"月度权重份额(口径B)"并取平均时段
def month_weight(m, seg):
    d=collections.defaultdict(lambda: collections.defaultdict(float))
    for x in active:
        if x["month"]!=m: continue
        s = "河" if (x["loc"] and any(x["loc"][k] for k in ["河流","池塘","悬崖上","出海口"])) else "海"
        if s!=seg: continue
        d[x["name"]][x["time"]] = x["w"]
    # 每鱼3时段均值
    return {k: sum(v.values())/len(v) for k,v in d.items()}

for seg in ["河","海"]:
    p()
    p(f"{'#'*30} {seg}系 {'#'*30}")
    for m in range(1,13):
        prev = 12 if m==1 else m-1
        cur_set = segset(m, seg); prev_set = segset(prev, seg)
        added = cur_set - prev_set; removed = prev_set - cur_set
        cw = month_weight(m, seg); pw = month_weight(prev, seg)
        # 权重变化最大的鱼(仅在双方都存在的鱼里比)
        common = cur_set & prev_set
        wdelta = sorted([(cw.get(n,0)-pw.get(n,0), n) for n in common], key=lambda z:z[0])
        # 份额(口径B: w/100)
        def fmt(lst): return ", ".join(f"{n}({d:+.0f})" for d,n in lst if d!=0) or "—"
        p(f"  {m:2d}月 (环比{prev:2d}月): 池子 {len(prev_set)}→{len(cur_set)} 种")
        p(f"      新增({len(added)}): " + (", ".join(sorted(added)) or "—"))
        p(f"      移除({len(removed)}): " + (", ".join(sorted(removed)) or "—"))
        p(f"      权重↑最大: " + ", ".join(f"{n}(w{pw.get(n,0):.0f}→{cw.get(n,0):.0f})" for d,n in wdelta[-4:][::-1] if d!=0))
        p(f"      权重↓最大: " + ", ".join(f"{n}(w{pw.get(n,0):.0f}→{cw.get(n,0):.0f})" for d,n in wdelta[:4] if d!=0))

# 每月 池子构成占比 (河: 3个河地点合并 & 海)
p()
p("--- 每月 河系/海系 鱼种数 & 权重和(口径B, 白天) ---")
p(f"{'月':>3}{'河种数':>7}{'河权重和':>8}{'海种数':>7}{'海权重和':>8}")
for m in range(1,13):
    rw = collections.defaultdict(float); sw = collections.defaultdict(float)
    for x in active:
        if x["month"]!=m: continue
        s = "河" if (any(x["loc"][k] for k in ["河流","池塘","悬崖上","出海口"])) else "海"
        (rw if s=="河" else sw)[x["name"]] = x["w"]
    p(f"{m:>3}{len(rw):>7}{sum(rw.values()):>8.0f}{len(sw):>7}{sum(sw.values()):>8.0f}")

# ============ 4. 影子档 低高级分布 ============
p()
p("="*70)
p("【4】影子档分布 (9档: SS/S/M/L/LL/LLL/J/K/U)")
p("="*70)
SH=["SS","S","M","L","LL","LLL","J","K","U"]
p("--- 每档: 种数/河海/均价/价格区间/平均活跃月/价格中位 ---")
for s in SH:
    lst=[f for f in fish.values() if f["shadow"]==s]
    if not lst: p(f"  {s:<4} 无"); continue
    h=[f for f in lst if f["seg"]=="河"]; se=[f for f in lst if f["seg"]=="海"]
    prices=sorted(float(f["price"]) for f in lst)
    avg=sum(prices)/len(prices); med=prices[len(prices)//2]
    am=sum(len(f["months"]) for f in lst)/len(lst)
    p(f"  {s:<4} 共{len(lst):2d} (河{len(h)}/海{len(se)}) 均价={avg:8.0f} 中位={med:7.0f} 区间=[{prices[0]:.0f},{prices[-1]:.0f}] 平均活跃月={am:4.1f}")
    p(f"        河: " + (", ".join(f"{f['name']}(¥{f['price']})" for f in sorted(h,key=lambda z:-float(z['price']))) or "—"))
    p(f"        海: " + (", ".join(f"{f['name']}(¥{f['price']})" for f in sorted(se,key=lambda z:-float(z['price']))) or "—"))

p()
p("--- 低级档(SS+S+M) vs 高级档(LL+LLL+J+K+U) 对比 ---")
low=[f for f in fish.values() if f["shadow"] in ["SS","S","M"]]
mid=[f for f in fish.values() if f["shadow"] in ["L"]]
high=[f for f in fish.values() if f["shadow"] in ["LL","LLL","J","K","U"]]
for nm,g in [("低级(SS/S/M)",low),("中级(L)",mid),("高级(LL/LLL/J/K/U)",high)]:
    prices=[float(f["price"]) for f in g]
    am=sum(len(f["months"]) for f in g)/len(g)
    h=sum(1 for f in g if f["seg"]=="河"); s=sum(1 for f in g if f["seg"]=="海")
    p(f"  {nm:<20} {len(g):2d}种 (河{h}/海{s}) 均价={sum(prices)/len(prices):8.0f} 中位={sorted(prices)[len(prices)//2]:7.0f} 平均活跃月={am:4.1f}")

Path("analysis/deep7.txt").write_text("\n".join(out), encoding="utf-8")
print("\nWROTE deep7.txt")
