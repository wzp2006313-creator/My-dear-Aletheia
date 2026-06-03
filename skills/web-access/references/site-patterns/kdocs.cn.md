# kdocs.cn (WPS 在线文档)

## 问题

WPS 在线文档（kdocs.cn）使用 **Canvas/WebGL 渲染**文档内容，而非标准 DOM 文本节点。这导致：

1. `browser_snapshot` 和 `browser_console` 只能抓到零散的 SVG text 元素或空白
2. `browser_scroll` 和键盘翻页（PageDown/ArrowDown/End）大概率无效——页面永远停留在可见的第一页
3. `web_extract` 返回空或 HTML 壳（content 在 canvas 里）

## 症状

- `browser_navigate` 能打开链接，`browser_vision` 能看到部分内容
- 状态栏显示 "页面: 1/7"，但无论怎么滚动/按键，始终停在第 1 页
- 有登录弹窗时可能进一步遮挡内容

## 推荐做法

**直接放弃浏览器抓取。** 请用户从 WPS 导出为 `.docx` 文件，通过飞书/其他渠道发送附件。

如果用户不方便导出，可以用 `browser_vision` 配合多次点击-截图来逐页查看（极其低效，仅作最后手段）。

## 替代入口

如果用户分享的是 WPS "链接分享"模式（可评论/可编辑），可以尝试在 URL 后加 `?format=docx` 或请用户在 WPS 内点「文件 → 下载 → docx」。
