---
name: case-prep-notion
description: "整理咨询 case prep 到 Notion：PDF 提取、页面迁移、格式规范。"
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [notion, consulting, case-prep, casebook, productivity]
---

# Case Prep → Notion

整理用户的咨询 case prep 资料（casebook PDF、逐字稿、课程要点）进 Notion。用户（宋瀚清/展鹏）正在准备咨询面试，资料散落在 PDF、Word 逐字稿里，需要结构化地进 Notion。

## 触发场景
- 用户发来 casebook PDF（如 "Peter K 2020"）要按序号整理进 Notion
- 用户要求"把 case 移到 XX 页面"或"整理到 Notion"
- 用户发来会议逐字稿/课程内容要求整理成 case 笔记

## 用户的 Notion 结构（已确认）
- 数据库「咨询准备」DB id = `329fde4c-8055-807d-a29d-cb206d82671a`
- 父页面「PeterK 2020」id = `329fde4c-8055-80b5-9cd0-c19e3be3249c`，其下挂 11 个 case 子页
- 每个 case 一个子页，标题格式 `Case N — Name (Type)`（Type 如 Market entry / Profitability / PE firm / Comparison / Wild card / Revenue growth）

## Case 页面格式（用户偏好）
```
callout：Case Type: X | Source: ... | Time: XX min | Interviewer-driven
分隔线
H2 Prompt + prompt 原文 + Key facts
分隔线 + H2 Case Questions
每题：H3 "Q1: 问题原文" → "YOUR ANSWER HERE" 空白 callout（✏️）→ 官方答案 callout（📋）
```
- 官方答案精炼成要点，保留关键数字和结论；数学题保留完整计算过程和答案
- **务必保留用户手动做的笔记版**（含个人作答和反思），不要覆盖、不要删

## Notion API 关键技巧（本机实测通过）

### 用 Python urllib + `Notion-Version: 2022-06-28`，不要用 curl/subprocess
本机 curl/subprocess 会 SSL 握手超时（LibreSSL），Python urllib 直接可用。用 `2022-06-28`（经典 `/databases/` `/blocks/` `/pages/` 端点），不要用 2026-03-11（那个版本用 data sources + ntn CLI，且 urllib 会 400）。KEY 已在环境配置（`NOTION_API_KEY`）。

### 创建子页面
用 `POST /v1/pages`，`parent: {"type":"page_id","page_id":"..."}` + `properties.title`。**不要用 child_page block**（`PATCH /blocks/{parent}/children` 加 `{"type":"child_page",...}` 会 400 validation_error）。

### 复制/迁移 blocks —— 必须重建，不能原样复用
`GET /v1/blocks/{id}/children` 返回的 block 带只读字段（`id`/`parent`/`created_time`/`annotations`/`text.link:null`），直接回 POST 会 400。每个 block 重建为：
```python
{"object":"block","type":t, t:{"rich_text":[{"type":"text","text":{"content": ...}}]}}
```
- callout 额外加 `icon: {"emoji": ...}`
- divider 用 `{}`
- 跳过源页的 `heading_1`（子页已有自己的标题）
- 每批 20 个 block 一次 `PATCH`

### 归档（不是 DELETE）
`PATCH /v1/pages/{id}` + `{"archived": true}`。DELETE 方法返回 400。

### 图片/图表上传限制
API 不能一步把本地图片插进页面（image block 需要外部 URL 或先走文件上传）。要加图表：用 pymupdf 把 PDF 图表页渲染成 PNG（`doc[i].get_pixmap(dpi=150)`），存本地文件夹，通过飞书 `MEDIA:/path` 发回让用户手动拖进 Notion。图床（catbox/0x0.st）当前不可用，别依赖。

## PDF 提取
用 pymupdf（`import pymupdf; doc = pymupdf.open(path); doc[i].get_text()`）。定位 case 的图表页：grep 文本里的 "Hand-outs" / "Appendix" 关键词，注意 PDF 页码 = casebook 页码 + 1。批量 11 个 case 时用 delegate_task 并行分 3 个子代理（每代理 3-4 个 case），子代理需自己 `sys.path.insert(0,'/tmp')` 读共享 helper。

## 陷阱
- Notion API 写入是 append-only（blocks API 只能加到页尾），不能指定位置
- 子代理迁移时网络波动会导致重复创建子页，完成后要验证子页数量、删重复
- 数据库条目归档会丢失 Case Type 属性，迁移到子页时把类型写进标题（`Case N — Name (Type)`）
