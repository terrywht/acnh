# -*- coding: utf-8 -*-
"""
add_time_to_wps.py
在《动森鱼虫合集》「鱼结论记录」页签的 F(AppearType) 与 G(月份总数) 之间
插入一列「活动时间」，内容为每种鱼的时段组合名。

6 种组合（已校验，与用户列举完全一致）：
  白天+晨昏+夜晚  -> 全天
  白天            -> 白天
  夜晚+晨昏       -> 非白天   (= 全天 - 白天)
  夜晚            -> 夜间
  白天+晨昏       -> 非夜间   (= 全天 - 夜晚)
  夜晚+白天       -> 非晨昏   (= 全天 - 晨昏)

数据来源：「鱼分析表」页签，取每鱼所有 Weight>0 的行对应的 Time 列集合。
"""
import io, os, shutil, datetime
import openpyxl

SRC = r'C:/Users/Administrator/Documents/WPSDrive/344975910/WPS云盘/动森鱼虫合集.xlsx'
OUT = r'C:/Users/Administrator/WorkBuddy/acnh/待替换_动森鱼虫合集_含时间列.xlsx'
BAK = r'C:/Users/Administrator/WorkBuddy/acnh/backup'

# 组合名映射（frozenset of 时段）
NAME = {
    frozenset(['白天', '晨昏', '夜晚']): '全天',
    frozenset(['白天']): '白天',
    frozenset(['夜晚', '晨昏']): '非白天',
    frozenset(['夜晚']): '夜间',
    frozenset(['白天', '晨昏']): '非夜间',
    frozenset(['夜晚', '白天']): '非晨昏',
}

def main():
    wb = openpyxl.load_workbook(SRC)

    # ---- 1. 从「鱼分析表」构建 ItemID -> 时段组合名 ----
    wa = wb['鱼分析表']
    slots = {}   # iid -> set of Time (Weight>0)
    names = {}
    for r in range(3, wa.max_row + 1):
        iid = wa.cell(row=r, column=1).value
        if iid is None:
            continue
        iid = int(iid)
        names[iid] = wa.cell(row=r, column=2).value
        t = wa.cell(row=r, column=7).value
        w = wa.cell(row=r, column=8).value
        slots.setdefault(iid, set())
        if w and w > 0:
            slots[iid].add(t)

    iid2time = {}
    unmatched = []
    for iid, s in slots.items():
        key = frozenset(s)
        if key in NAME:
            iid2time[iid] = NAME[key]
        else:
            unmatched.append((iid, names.get(iid), sorted(s)))

    # ---- 2. 备份 ----
    os.makedirs(BAK, exist_ok=True)
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    bak = os.path.join(BAK, f'动森鱼虫合集_备份_{ts}.xlsx')
    shutil.copy2(SRC, bak)

    # ---- 3. 在「鱼结论记录」F 与 G 之间插入一列 ----
    ws = wb['鱼结论记录']
    ws.insert_cols(7)            # 在第 7 列（G）位置插入，原 G..J 右移为 H..K

    # 表头
    c = ws.cell(row=1, column=7, value='活动时间')
    c.font = openpyxl.styles.Font(name='宋体', size=11, bold=True)
    c.alignment = openpyxl.styles.Alignment(horizontal='left', vertical='center')
    ws.column_dimensions['G'].width = 10

    # 数据
    miss = []
    for r in range(2, ws.max_row + 1):
        iid = ws.cell(row=r, column=1).value
        if iid is None:
            continue
        val = iid2time.get(int(iid))
        if val is None:
            miss.append((r, iid, ws.cell(row=r, column=2).value))
        cell = ws.cell(row=r, column=7, value=val)
        cell.font = openpyxl.styles.Font(name='宋体', size=11)
        cell.alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center')

    # autofilter 扩到 K（原 A1:J89 -> A1:K89）
    ws.auto_filter.ref = f'A1:K{ws.max_row}'

    # ---- 4. 输出 ----
    wb.save(OUT)

    print(f'备份: {bak}')
    print(f'输出: {OUT}')
    print(f'插入列: 第7列「活动时间」，原 G-K 右移')
    print(f'autofilter: {ws.auto_filter.ref}')
    print(f'维度: {ws.max_row} x {ws.max_column}')
    print()
    print('=== 写入分布 ===')
    import collections
    cc = collections.Counter()
    for r in range(2, ws.max_row + 1):
        cc[ws.cell(row=r, column=7).value] += 1
    for k, v in cc.items():
        print(f'  {k}: {v}')
    print()
    print('=== 未匹配（应为空） ===')
    for r, iid, nm in miss:
        print(f'  r{r} id={iid} {nm}')
    if unmatched:
        print('=== 组合不在 6 类中（应为空） ===')
        for iid, nm, s in unmatched:
            print(f'  {nm} {s}')
    if not miss and not unmatched:
        print('  全部命中 6 类之一 ✓')

if __name__ == '__main__':
    main()
