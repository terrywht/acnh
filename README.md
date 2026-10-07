# acnh — 《动物森友会》钓鱼数值系统拆解

对 ACNH 钓鱼数值表的深度拆解与设计思路推导。**所有机制结论以官方参数表为准**，社区数据仅作标注层参考。

## 内容

| 文件 | 说明 |
|---|---|
| [`docs/总结-动森钓鱼数值拆解.md`](docs/总结-动森钓鱼数值拆解.md) | **完整总结**：5 轮分析全部结论 |
| [`docs/分析-稀有度与河海模板规律.md`](docs/分析-稀有度与河海模板规律.md) | **新增**：4 档稀有度 × 河海 逐档模板规律（河系"时间稀缺" vs 海系"概率稀缺"） |
| [`docs/对比-fish.json新增信息与机制.md`](docs/对比-fish.json新增信息与机制.md) | `fish.json` 的参考价值与边界（旧资料为权威口径） |
| [`docs/handoff-20261007-233922.md`](docs/handoff-20261007-233922.md) | **交接文档**：第 6–8 轮（数据源重建 / 稀有度分析 / WPS 写入） |
| [`docs/handoff-20261005-120604.md`](docs/handoff-20261005-120604.md) | 交接文档（第 1–5 轮） |
| [`analysis/`](analysis/) | 分析脚本与计算原始输出 |
| [`data/`](data/) | 官方参数表归档（3 张 CSV） |

## 落地交付

「鱼结论记录」页签（WPS《动森鱼虫合集.xlsx》）已写入三列：`H 稀有度`（80 鱼有值）、`I 刷鱼概率均值`、`J 刷鱼概率最大值`（88 行全有值，取自「鱼分析表」V/W 列）。

写入脚本：`analysis/add_rarity_to_wps.py`、`analysis/add_prob_to_wps.py`。
**注意 I/J 为静态值非活公式** —— 原始权重变更后需重跑脚本。

## 核心发现速览

- **机制**：六钓点加权轮盘（河流/池塘/悬崖上/出海口/大海/栈桥）；`AppearType` 实为 7 档枚举；Area 0/1 = 南北半球。
- **Σw=100 的真相**：只是引擎归一化约定（整数配额），不是概率接口。
- **时段**：原表 `Daytime` / `MorningAndEvening` / `Night` 三档 8 小时制（白天 9–16 / 夜晚 18–4 / 晨昏 5–8 & 17–20），组合出 6 种模式。
- **三维解耦**：排期（Month 开关）/ 稀有度（Weight 份数）/ 经济（Price）三者独立调参。
- **河海对比**：同构骨架 + 四差异；河系"稀有=窗口短"，海系"稀有=概率低但窗口长"；J/K/U 三档海系专属。
- **季节结构**：两大主体块（12-1-2-3 冬春块 / 6-7-8-9 夏季块）+ 两条过渡带（4-5月、10-11月）；1月=2月（Jaccard=1.00）。
- **影子档**：原表 `ShadowType` 实测 9 档（SS/S/M/L/LL/LLL/J/K/U）；影子档 ≠ 价格档。
- **稀有度（新增）**：4 档标注稀有度是独立第三层，`r(稀有度,价格)=0.902` 而 `r(稀有度,权重)=−0.607`。
- **模板化**：三层解耦 + 恒定权重和 + 垃圾道具全覆盖 + 影子作视觉编码器 + 月度招牌鱼轮换。

## 概率口径说明

| 口径 | 定义 |
|---|---|
| A · 池内概率 | 权重 ÷ 该钓点列权重和（最贴近玩家体验） |
| B · 原表份额 | 权重 ÷ 100 |
| C · 全年最高概率 | 该鱼在所有（月×地点）中的最大值 |

## 数据源

官方参数表（`FishAppearRiverParam` / `FishAppearSeaParam` / `FishStatusParam`）来自
<https://wuffs.org/acnh/bcsv_130/csv/>，已归档至 [`data/`](data/)。

社区数据 `fish.json`（ACNHAPI）仅用于提供 4 档稀有度标签与 14 语区名称对齐，**不作为机制依据**。

## 复现

```bash
python analysis/deep6.py   # 河海/月度/鱼影/模板化
python analysis/deep7.py   # 归类法/Jaccard/逐月池子/影子分层
python analysis/deep9_rarity_river_sea.py   # 原表基线重建 + 稀有度×河海分析
python analysis/deep8_crossmap.py           # 与 ACNHAPI fish.json 交叉验证
```

依赖：Python 3.13 + openpyxl（deep6/deep7 读 xlsx）；deep9 仅需标准库（读 `data/*.csv`）。
