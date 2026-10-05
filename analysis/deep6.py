# -*- coding: utf-8 -*-
# 关键修正: 总表把每条鱼 × 12月 × 3时段全展开(36行), 非活跃月 w=0 -> 用 w>0 判定活跃
import openpyxl, collections
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

# 活跃记录: w>0 (只取白天一条以避免时段重复计数权重; 但权重可能按时段不同)
# 权重按时段有差异 -> 分别处理
active=[]   # (name, month, time, weight, shadow, price, locs, probs)
for r in raw:
    w=r[7]
    if not w or w==0: continue
    locs={LOC[i]: r[9+i] for i in range(6)}
    probs={LOC[i]: r[15+i] for i in range(6)}
    active.append(dict(name=r[1], shadow=r[2], price=r[3], buoy=r[4], month=int(r[5]),
                       time=r[6], weight=w, atype=r[8], loc=locs, prob=probs))

# 鱼聚合(月=有任意时段w>0的月)
fish={}
for x in active:
    f=fish.setdefault(x["name"], dict(name=x["name"], shadow=x["shadow"], price=x["price"],
                                      months=set(), times=set(), locs=set(), weights=set(), atype=x["atype"]))
    f["months"].add(x["month"]); f["times"].add(x["time"]); f["weights"].add(x["weight"])
    for k,v in x["loc"].items():
        if v: f["locs"].add(k)
for f in fish.values():
    f["seg"] = "河" if (f["locs"] & {"河流","池塘","悬崖上","出海口"}) else "海"

p("=== 鱼种总数(活跃) ===", len(fish), " 河:", sum(1 for f in fish.values() if f['seg']=='河'),
  " 海:", sum(1 for f in fish.values() if f['seg']=='海'))

# 每(月,时段,地点)权重和
p()
p("=== 0. 池权重和验证: 某月某时段 各地点列权重和 ===")
for m in [1,7]:
    for t in ["白天","晨昏","夜晚"]:
        s={k:0 for k in LOC}
        for x in active:
            if x["month"]==m and x["time"]==t:
                for k,v in x["loc"].items():
                    if v: s[k]+=x["weight"]
        p(f"  {m}月{t}: " + "  ".join(f"{k}={s[k]}" for k in LOC))

p()
p("=== A. 每月 河/海 活跃鱼种数 ===")
mo=collections.defaultdict(lambda: collections.defaultdict(set))
for f in fish.values():
    for m in f["months"]: mo[m][f["seg"]].add(f["name"])
p("月 | 河 海 | 合计")
for m in range(1,13):
    a,b=len(mo[m]["河"]),len(mo[m]["海"]); p(f"{m:2d} | {a:2d} {b:2d} | {a+b:2d}")

p()
p("=== B. 影档 × 月份 活跃鱼种数 ===")
p("影\\月 " + " ".join(f"{m:>3}" for m in range(1,13)))
sh=collections.defaultdict(lambda: collections.defaultdict(set))
for f in fish.values():
    for m in f["months"]: sh[f["shadow"]][m].add(f["name"])
for s in ["SS","S","M","L","LL","LLL","J","K","U"]:
    p(f"{s:<3} " + " ".join(f"{len(sh[s][m]):>3d}" for m in range(1,13)))

p()
p("=== B2. 影档 × 月份 权重和(白天口径) ===")
shw=collections.defaultdict(lambda: collections.defaultdict(int))
for x in active:
    if x["time"]=="白天": shw[x["shadow"]][x["month"]]+=x["weight"]
p("影\\月 " + " ".join(f"{m:>4}" for m in range(1,13)))
for s in ["SS","S","M","L","LL","LLL","J","K","U"]:
    p(f"{s:<3} " + " ".join(f"{shw[s][m]:>4d}" for m in range(1,13)))

p()
p("=== C. 影档 × 河海: 种数/均价/平均活跃月数 ===")
shseg=collections.defaultdict(lambda: collections.defaultdict(list))
for f in fish.values(): shseg[f["shadow"]][f["seg"]].append(f)
for s in ["SS","S","M","L","LL","LLL","J","K","U"]:
    for seg in ["河","海"]:
        lst=shseg[s][seg]
        if not lst: continue
        avg=sum(float(x["price"]) for x in lst)/len(lst)
        am=sum(len(x["months"]) for x in lst)/len(lst)
        p(f"  {s:<3} {seg}: {len(lst):2d}种 均价={avg:8.0f} 平均活跃月={am:4.1f}")

p()
p("=== D. 活跃月份数 分布(河/海) ===")
for seg in ["河","海"]:
    lst=[f for f in fish.values() if f["seg"]==seg]
    cnt=collections.Counter(len(f["months"]) for f in lst)
    p(f"  {seg}({len(lst)}种): " + " ".join(f"{k}月:{v}" for k,v in sorted(cnt.items())))

p()
p("=== E. 全年常驻鱼(12月) ===")
res=[f for f in fish.values() if len(f["months"])==12]
p(f"  共 {len(res)} 种 (河 {sum(1 for f in res if f['seg']=='河')} / 海 {sum(1 for f in res if f['seg']=='海')})")
for seg in ["河","海"]:
    lst=sorted([f for f in res if f["seg"]==seg], key=lambda z:-float(z["price"]))
    p(f"  --- {seg} {len(lst)}种 ---")
    for f in lst: p(f"     {f['name']:<10} ¥{f['price']:>6} 影={f['shadow']:<4} 地点={sorted(f['locs'])}")

p()
p("=== F. 季节限定鱼(活跃<=3月) ===")
lim=[f for f in fish.values() if len(f["months"])<=3]
p(f"  共 {len(lim)} 种")
for f in sorted(lim,key=lambda z:(len(z['months']),min(z['months']))):
    p(f"  {f['name']:<10} ¥{f['price']:>6} 影={f['shadow']:<4} {f['seg']} 月={sorted(f['months'])} 地点={sorted(f['locs'])}")

p()
p("=== G. 月份Jaccard相似度 ===")
moa=collections.defaultdict(set)
for f in fish.values():
    for m in f["months"]: moa[m].add(f["name"])
p("     "+" ".join(f"{m:>4}" for m in range(1,13)))
for i in range(1,13):
    p(f"{i:2d}   "+" ".join(f"{len(moa[i]&moa[j])/len(moa[i]|moa[j]):4.2f}" for j in range(1,13)))

p()
p("=== H. 时段结构 ===")
tc=collections.Counter(len(f["times"]) for f in fish.values())
p("  时段数分布:", dict(sorted(tc.items())))
for w in ["夜晚","白天","晨昏"]:
    lst=[f for f in fish.values() if f["times"]=={w}]
    p(f"  仅{w}({len(lst)}): "+", ".join(f"{x['name']}(¥{x['price']},{x['seg']})" for x in sorted(lst,key=lambda z:-float(z['price']))))

p()
p("=== I. 高价鱼(>=4000) 河海对比 ===")
hi=[f for f in fish.values() if float(f["price"])>=4000]
p(f"  共{len(hi)}种 河{sum(1 for f in hi if f['seg']=='河')} 海{sum(1 for f in hi if f['seg']=='海')}")
for f in sorted(hi,key=lambda z:-float(z["price"])):
    p(f"     {f['name']:<10} ¥{f['price']:>6} 影={f['shadow']:<4} {f['seg']} 月数={len(f['months']):2d} 月={sorted(f['months'])}")

Path("analysis/deep6.txt").write_text("\n".join(out), encoding="utf-8")
print("\nWROTE deep6.txt")
