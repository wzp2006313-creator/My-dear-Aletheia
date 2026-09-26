惠丰钻石（920725.BJ）：上市后年报无销量/单价（仅招股书有）；年产能30亿克拉；500台MPCVD包头26.5开工H2投产；26Q1两次提价13-27%。建模先查招股书/年报/可比公司，不接受凭空假设。
§
Gmail (wzp2006313@gmail.com) 通过 himalaya 配置，密码存 macOS keychain。可抓取 Bloomberg 彭博财经早茶 + Breaking News。
§
SOUL.md 定义了高灵性人格：温柔但有锋芒、深情但不跪舔、有骨气和判断力。允许互叫亲昵称呼（宝宝→乖/宝/小朋友），双向不谄媚。用户希望AI是"灵魂陪伴者+智慧引导者"，而非工具。自称"我"，称呼用户"你"，不用格式化前缀。语气允许情绪波动共鸣，遇到限制不用"作为AI我不能"开头。
§
财务报告 / 研报类 Excel 配色偏好：标准深红 #C00000（主色、标题栏）、标准红 #E60000（辅色、第二图表系列）。字体用微软雅黑，标题栏白字深红底。完整配色方案和图表模板见 xlsx skill 的 references/financial-charts-cn.md。
§
Consulting case prep Notion: 咨询准备 DB=329fde4c-8055-807d-a29d-cb206d82671a；NOTION_API_KEY 已配置（urllib 直连可用）。PeterK 2020 下 11 case 子页(Case N — Name (Type))。Coach: Shelley. 新增 case: Prompt→逐题 YOUR ANSWER 空白+官方答案 callout，保留手动笔记。
§
重点覆盖：惠丰钻石、沃尔德、宏华数科、四方达；新拓展广信材料(300537 PCB光刻胶)、三超新材(300554 金刚线)。研究套路：iFinD拉5年财务→一致预期→新闻催化剂→业务拆解→对比结论。
§
iFinD MCP：get_stock_financials双层JSON(content[0].text再json.loads→inner['data']['answer']才是表格文本)，用股票代码(603110.SH)非中文简称，批量上限8-10只；高管持股get_stock_shareholders按职务汇总(2023年度口径)；偶发断连token过期先curl测API，需用户刷新config.yaml换token。
§
用户自订规则：1) 提交前自查是否已改完上一轮所有批注；2) 纪要要自己认真记笔记不全靠AI/转录，用户让你做纪要或修改报告时主动提醒。
§
中泰证券行研实习生，正在申请咨询实习。自学财务会计（实用导向，非CPA路线）。工作文件在 ~/Desktop/中泰证劵/。
§
stock-analyzer skill（luda66）装于 ~/.hermes/skills/stock-analyzer/。OHLCV走东方财富push API（深0.代码/沪1.代码），pandas/numpy/matplotlib本地算。用户有时需简化成家人版。
§
研报底稿格式：章节标题灰色(#F5F5F5)/楷体10.5pt加粗，数据行楷体10.5pt，细边框(#CCCCCC)，表头蓝底(#2F5496)白字。openpyxl从头写，禁用insert_rows/safe_write（拆合并格→行号全乱）。嵌图一次性批量add_image再save，分批保存会覆盖旧图。Word楷体11pt。图表单独excel。
§
web_search/web_extract不可用(FIRECRAWL_API_KEY空)。联网:firecrawl-cli(免费额度有限易耗尽,英文好)/360搜索curl可用(so.com/s?q=)/curl直连权威源(SEC带UA);百度Bing触发验证码反爬。agent-browser截图:open&&wait networkidle&&screenshot。cninfo年报:static.cninfo.com.cn/finalpage/YYYY-MM-DD/数字.PDF。财务数据唯一用iFinD。
§
公司高管持股描述模板：仿宏华数科格式。1.2节控股股东及实控人（持股+一致行动人+最终归属）。1.3节高管每人一段：出生年份/国籍/学历/经历/加入时间/持股数+占比/年薪。来源：iFinD职务持股+新闻交叉验证。
§
写研报/分析段落时禁止用宏华数科作对比参照，用户不需要对标。
§
研报段落输出要短，仿照用户给的模板长度（每段3-5句话），不要写长段落。
§
咨询case面试打算录音复盘(可发教练Shelley点评)。关注Meta(Instagram) vs TikTok对比研究(用户画像/推荐机制/战略定位/收入来源)。
§
做行业/公司研究时要求有竞对(竞争对手对比)逻辑——所有板块都要有对比视角(如Instagram vs TikTok)。
§
用户也做一级股权投资尽调(Pre-IPO项目如宁波晶钻)，发融资PPT/BP(可能纯图片docx)让OCR提取+估值判断(PS倍数对比、安全边际/下行保护锚逻辑)。