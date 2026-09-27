# kdocs.cn (WPS 在线文档)

## 摘要
WPS 在线文档使用 Canvas 渲染，浏览器自动化（翻页/文本抓取）均无效。不要浪费时间尝试。直接请用户从 WPS 导出为 .docx 文件发送。

## 症状
- browser_navigate 可以加载页面
- browser_snapshot 可以获取大纲/工具栏等 UI 元素
- 文档主体内容在 Canvas 中渲染，DOM 中不可见
- browser_scroll / PageDown / End 等翻页操作无效（始终停留在第一页）
- browser_console 执行 innerText 只能获取工具栏文字，无法获取文档正文

## 有效方案
1. 请用户在 WPS 中点击「下载」→ 导出为 .docx
2. 将 .docx 文件直接通过飞书发送
3. 使用 docx skill 读取内容

## 无效方案（已试过）
- browser_vision 截图获取内容（每次截图看到的是同一页）
- browser_console JS 提取（Canvas 内容不可脚本提取）
- 多次 PageDown + browser_vision 循环（无效）
