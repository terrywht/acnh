# -*- coding: utf-8 -*-
"""
deep8_crossmap.py
交叉验证：桌面 fish.json (ACNHAPI 数据集, 80 条) vs 既有拆解结论 (analysis/deep7.txt, 84 条含 4 垃圾)

用途：
  1. 把旧影子档 (SS/S/M/L/LL/LLL/J/K/U) 映射到新文件的数字影子编码 (Smallest(1)..Narrow)
  2. 校验 price-cj / rarity / location / time-array 等新字段
  3. 独立复算季节结构 (月份集合 + Jaccard) 以交叉验证旧结论

用法：python deep8_crossmap.py [fish.json 路径]
"""
import json, io, os, re, sys, collections, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_JSON = r"C:\Users\Administrator\Desktop\fish.json"
DEEP7 = os.path.join(HERE, "deep7.txt")


def load_json(p):
    return json.load(io.open(p, encoding="utf-8"))


def parse_old_tiers(p):
    """从 deep7.txt 解析旧影子档 -> [(zh_name, price), ...]"""
    tiers = collections.OrderedDict()
    cur = None
    key_re = re.compile(r"^\s{2}([A-Z]{1,3})\s+共\s*(\d+)\s*\(河(\d+)/海(\d+)\)")
    fish_re = re.compile(r"([^,()｜|]+?)\(¥(\d+)\)")
    for line in io.open(p, encoding="utf-8"):
        m = key_re.match(line)
        if m:
            cur = m.group(1)
            tiers.setdefault(cur, [])
            continue
        if cur and re.match(r"^\s+(河|海):", line):
            body = line.split(":", 1)[1]
            for name, price in fish_re.findall(body):
                tiers[cur].append((name.strip(), int(price)))
    return tiers


def main():
    jp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JSON
    fish = load_json(jp)
    tiers = parse_old_tiers(DEEP7)

    # 新文件: zh 名 -> 记录
    by_zh = {}
    for k, v in fish.items():
        zh = v["name"].get("name-CNzh")
        by_zh[zh] = v

    print("=" * 78)
    print("【A】旧影子档  ->  新文件影子编码  映射矩阵")
    print("=" * 78)
    matrix = collections.defaultdict(collections.Counter)
    unmatched = []
    for tier, items in tiers.items():
        for name, price in items:
            v = by_zh.get(name)
            if v is None:
                unmatched.append((tier, name, price))
                continue
            matrix[tier][v["shadow"]] += 1
    new_shadows = sorted({v["shadow"] for v in fish.values()})
    print(f"{'旧档':<5} | " + " | ".join(f"{s:<20}" for s in new_shadows))
    for tier in tiers:
        row = " | ".join(f"{matrix[tier][s]:<20}" for s in new_shadows)
        print(f"{tier:<5} | {row}")
    print()
    if unmatched:
        print("未匹配(新文件中不存在):", unmatched)
    print()

    # 每档 -> 唯一对应
    print("--- 一一映射结论 ---")
    for tier in tiers:
        c = matrix[tier]
        top = c.most_common()
        if top:
            print(f"  {tier:<4} -> {top[0][0]}  (占 {top[0][1]}/{sum(c.values())})")
    print()

    print("=" * 78)
    print("【B】新字段校验")
    print("=" * 78)
    # price-cj 比例
    ratios = collections.Counter(round(v["price-cj"] / v["price"], 4) for v in fish.values())
    print("price-cj / price 比值分布:", dict(ratios))
    print()

    # rarity 分布 x 影子
    print("--- rarity(官方标签) x shadow ---")
    rc = collections.Counter(v["availability"]["rarity"] for v in fish.values())
    print("rarity 计数:", dict(rc))
    rt = collections.defaultdict(collections.Counter)
    for v in fish.values():
        rt[v["availability"]["rarity"]][v["shadow"]] += 1
    for r in ["Common", "Uncommon", "Rare", "Ultra-rare"]:
        print(f"  {r:<12}: {dict(rt[r])}")
    print()

    # rarity x 价格
    print("--- rarity x 价格 ---")
    for r in ["Common", "Uncommon", "Rare", "Ultra-rare"]:
        ps = [v["price"] for v in fish.values() if v["availability"]["rarity"] == r]
        if ps:
            print(f"  {r:<12}: n={len(ps):<3} 均价=¥{sum(ps)//len(ps):<6} 区间=¥{min(ps)}–{max(ps)}")
    print()

    # location
    print("--- location 分布 ---")
    for k, c in sorted(collections.Counter(v["availability"]["location"] for v in fish.values()).items()):
        print(f"  {k:<32}: {c}")
    print()

    # 天气门槛
    rain = [v["name"]["name-CNzh"] for v in fish.values()
            if "rain" in v["availability"]["location"]]
    print("天气限定鱼:", rain)
    print()

    # 多地点
    multi = [v["name"]["name-CNzh"] for v in fish.values()
             if "&" in v["availability"]["location"]]
    print("跨地点鱼:", multi)
    print()

    # 时段
    night_only, day_only = [], []
    for v in fish.values():
        ta = v["availability"]["time-array"]
        if not ta or len(ta) == 24:
            continue
        s = set(ta)
        if s <= set(range(21, 24)) | set(range(0, 5)):
            night_only.append(v["name"]["name-CNzh"])
        elif s <= set(range(4, 21)):
            day_only.append(v["name"]["name-CNzh"])
    print("仅夜间:", night_only)
    print("仅白天:", day_only)
    print()

    # 月份集合 & Jaccard（北半球）
    print("=" * 78)
    print("【C】独立复算季节结构（新文件, 北半球）")
    print("=" * 78)
    mon = {m: set() for m in range(1, 13)}
    for zh, v in by_zh.items():
        for m in v["availability"]["month-array-northern"]:
            mon[m].add(zh)
    for m in range(1, 13):
        print(f"  {m:>2}月: {len(mon[m]):>2} 种")
    print()
    print("--- 相邻月 Jaccard ---")
    for m in range(1, 12):
        A, B = mon[m], mon[m + 1]
        J = len(A & B) / len(A | B)
        print(f"  {m:>2}->{m+1:<2}月  J={J:.4f}  (交{len(A&B)}/并{len(A|B)})")
    print()
    # 常驻
    allm = set().union(*mon.values())
    always = [z for z in allm if all(z in mon[m] for m in range(1, 13))]
    print(f"全年常驻鱼 {len(always)} 条: {sorted(always)}")
    print()

    # isAllDay / isAllYear 一致性
    bad = []
    for v in fish.values():
        a = v["availability"]
        if a["isAllDay"] != (len(a["time-array"]) == 24):
            bad.append(v["name"]["name-CNzh"])
    print("isAllDay 与 time-array 不一致:", bad or "无")
    print()

    # 语言覆盖
    langs = set()
    for v in fish.values():
        langs |= set(v["name"].keys())
    print(f"name 语言字段 {len(langs)} 种:", sorted(langs))


if __name__ == "__main__":
    main()
