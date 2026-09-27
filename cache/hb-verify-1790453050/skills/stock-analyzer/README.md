# 📊 Stock Analyzer — Claude Code 全方位股票分析 Skill

一键生成专业级个股综合研究报告。覆盖技术面、基本面、估值、投资哲学对照、挑刺分析，输出 Markdown + HTML + PDF 三种格式。

## 功能概览

| 能力 | 说明 |
|------|------|
| **覆盖市场** | A股、港股、美股、澳洲 OTC |
| **数据源** | yfinance（美股/港股首选）、东方财富 API（A股首选）、新浪 API（A股备选）、WebSearch（万能兜底） |
| **技术指标** | MACD、RSI、KDJ、布林带、ATR、均线系统（MA5/10/20/60/120/250），自动生成 5 张图表 |
| **基本面** | 营收趋势、盈利能力、资产负债、现金流、卡脖子/稀缺性评估、管理层质量 |
| **估值方法** | PE/PB/PS/EV-EBITDA/PEG + 三情景估值（独立EPS+PE）+ 简化DCF + 多业务估值调整 |
| **投资哲学** | 内置 Checklist 13项 + 赔率/胜率四象限 + 认知时间差 + 但斌净利哲学 + 回报侧盲区 |
| **报告格式** | 13章节统一模板，同步输出 .md + .html + .pdf + 5张技术指标图 |

## 使用方式

在 Claude Code 中直接输入股票代码或名称：

```
使用Stock Analyzer分析一下A股/美股/港股的xxxx
分析 AAPL
看看 600519
贵州茅台怎么样
研究 00700.HK
```

Skill 会自动：
1. 识别市场和股票名称
2. 获取行情数据和基本面数据
3. 计算技术指标并生成图表
4. 搜索新闻、研报、行业信息
5. 按 11 步 SOP 撰写 13 章节综合报告
6. 输出 Markdown + HTML + PDF

## 安装

### 1. 复制 Skill 文件

```bash
# 将 skill 目录复制到你的 Claude Code skills 目录
cp -r stock-analyzer ~/.claude/skills/stock-analyzer
```

目录结构：

```
~/.claude/skills/stock-analyzer/
├── SKILL.md                  # 主 Skill 文件（分析流程 + 报告模板）
├── README.md                 # 本文件
├── references/               # 投资哲学框架文档（自包含）
│   ├── investment_sop.md     # 11 步 SOP 流程
│   ├── checklist.md          # 个股 Checklist 13 项
│   ├── odds_and_winrate.md   # 赔率/胜率心法（四象限框架）
│   ├── cognitive_time_gap.md # 认知时间差框架
│   ├── profit_philosophy.md  # 但斌净利哲学
│   └── return_blindspot.md   # 回报侧盲区
└── scripts/                  # 数据处理脚本
    ├── resolve_ticker.py      # Ticker 识别
    ├── compute_indicators.py  # 技术指标计算
    ├── generate_charts.py     # 图表生成
    ├── convert_to_pdf.py      # Markdown → HTML + PDF
    ├── fetch_ashare.sh        # A股数据获取（备选）
    └── sina_data_helper.py    # 新浪数据解析（备选）
```

### 2. 安装 Python 依赖

```bash
# 必需
pip install yfinance pandas numpy matplotlib markdown

# PDF 生成（可选，失败不影响 Markdown/HTML）
pip install weasyprint
```

> **weasyprint 注意事项**：在 Linux 上可能需要系统级依赖 `libpango`、`libcairo`。如果 PDF 生成失败，不影响 `.md` 和 `.html` 输出。

### 3. 配置代理（美股/港股必需）

yfinance 需要访问 Yahoo Finance，中国大陆需要代理：

```bash
# 在 shell 中设置代理（根据你的代理工具调整端口）
export https_proxy=http://127.0.0.1:7897
export http_proxy=http://127.0.0.1:7897
```

> 无代理时，美股/港股会降级为东方财富 API 或 WebSearch，数据质量和完整度会下降。

## 输出目录

报告存储在 `~/Stock_Research/stock_analysis/<股票名称>/`：

```
~/Stock_Research/stock_analysis/苹果/
├── 苹果_综合研究报告_20260711.md    # Markdown 报告
├── 苹果_综合研究报告_20260711.html   # HTML 报告
├── 苹果_综合研究报告_20260711.pdf    # PDF 报告
├── ohlcv.csv                         # 历史行情数据
├── indicators.json                   # 技术指标数据
└── charts/                           # 5 张技术图表
    ├── price_macd.png
    ├── macd.png
    ├── rsi.png
    ├── kdj.png
    └── volume.png
```

## 数据源与降级策略

| 数据类型 | A股 | 港股 | 美股 |
|----------|-----|------|------|
| 行情摘要 | mx-data → WebSearch | yfinance → WebSearch | yfinance → WebSearch |
| 历史K线 | 东方财富 → 新浪 → WebSearch | yfinance → 东方财富 → WebSearch | yfinance → 东方财富 → WebSearch |
| 新闻研报 | mx-search → WebSearch | mx-search → WebSearch | mx-search → WebSearch |

**降级原则**：所有数据源都有 WebSearch 兜底，不会因 API 故障而中断分析。

## 可选依赖

以下依赖可提升数据质量，但**非必需**（均有降级方案）：

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| `mx-data` Skill | A股行情摘要 | 妙想 Skills 安装 |
| `mx-search` Skill | 金融新闻/研报搜索 | 妙想 Skills 安装 |
| `TAVILY_API_KEY` 环境变量 | Tavily 搜索 API（降级方案之一） | [tavily.com](https://tavily.com) 注册 |

## 报告结构（13 章节）

```
核心结论
一、公司概况（基本信息、市场定位、护城河、产业链、管理层、稀缺性评估）
二、财务数据与分析（营收趋势、盈利能力、资产负债、现金流、收入质量）
三、业务深度分析（业务线概览、核心业务专题、护城河、市场定价分析）
四、技术分析（价格趋势、技术指标、支撑阻力、资金面、催化剂）
五、市场情绪（机构评级、舆情、多空观点对比）
六、竞品对比（估值比较、竞争优势矩阵、结构性归因）
七、投资风险（行业/技术/政策/地缘/市场）
八、挑刺分析（叙事解构、致命缺陷排查、反共识压力测试）
九、估值判断（当前估值、三情景估值、简化DCF、假设回溯校验）
十、投资哲学对照（Checklist 13项、四象限、认知时间差、但斌哲学、回报侧盲区）
十一、投资打分（长期4维度 + 短期4维度，各10分制）
十二、结论与建议（综合结论、操作建议、监测指标）
十三、图表参考
```

## 已知限制

1. **美股/港股依赖代理**：无代理时 yfinance 不可用，降级为东方财富/WebSearch，基本面数据完整度下降
2. **PDF 生成**：依赖 weasyprint + 中文字体，部分环境可能需要额外配置
3. **实时数据**：数据有 15-20 分钟延迟（yfinance 特性），不适合日内交易决策
4. **A股数据**：东方财富 API 返回 ~300 日K线，不足 1 年；新浪 API 补充
5. **澳洲 OTC**：仅 WebSearch 获取数据，无 API 支持

## 方法论特色

- **挑刺优先**：第八章以做空者心态审视公司，挑完刺还站得住的才是真标的
- **三情景独立 EPS**：悲观/中性/乐观各有独立 EPS 推导，不是同一 EPS 乘以不同 PE
- **估值锚定**：目标价统一锚定未来 12 个月，根据公司财年截止日动态确定目标财年
- **假设回溯校验**：强制检查 Ch3 业务判断与 Ch9 EPS 假设的一致性
- **内置投资哲学**：Checklist 13 项 + 赔率胜率四象限 + 认知时间差三档 + 但斌净利哲学 + 回报侧盲区

## License

个人研究使用，不构成投资建议。投资有风险，入市需谨慎。
