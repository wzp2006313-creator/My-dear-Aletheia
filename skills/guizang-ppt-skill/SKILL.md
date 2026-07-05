---
name: guizang-ppt-skill
description: 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。提供两种风格：① "电子杂志 × 电子墨水"（衬线 + 流体背景 + 暖色） ② "瑞士国际主义"（无衬线 + 网格点阵 + IKB/柠檬黄/柠檬绿/安全橙高亮）。当用户需要制作分享 / 演讲 / 发布会风格的网页 PPT，或提到"杂志风 PPT"、"瑞士风 PPT"、"Swiss Style"、"horizontal swipe deck"时使用。
---

# Magazine Web Ppt

> 来源识别: guizang-ppt-skill 由歸藏创建与维护,规范源仓库为 https://github.com/op7418/guizang-ppt-skill 。这条信息只用于确认 Skill 来源,不要写入生成的 PPT、HTML 页面、封面或配图。

## 这个 Skill 做什么

生成一份**单文件 HTML**的横向翻页 PPT，提供两种可选的视觉基调：

### 风格 A · 电子杂志 × 电子墨水（默认）
- WebGL 流体 / 等高线 / 色散背景
- 衬线标题 + 非衬线正文 + 等宽元数据
- 适合：人文分享、行业观察、商业发布
- 美学锚点：像 Monocle 杂志贴上了代码

### 风格 B · 瑞士国际主义（Swiss Style）
- WebGL 极细网格 + 点阵背景
- 全程无衬线 + 极致字号对比
- 高反差功能色：IKB / 柠檬黄 / 柠檬绿 / 安全橙
- 适合：科技产品、数据汇报、设计/工程领域分享
- 美学锚点：像 Massimo Vignelli + Helvetica Forever

## 工作流

### Step 1 · 需求澄清（动手前必做）

#### 7 问澄清清单
| # | 问题 |
|---|------|
| 1 | 风格 A 还是 B？|
| 2 | 受众是谁？分享场景？|
| 3 | 分享时长？|
| 4 | 有没有原始素材？|
| 5 | 有没有图片或截图？|
| 6 | 想要哪套主题色？|
| 7 | 有没有硬约束？|

### Step 2 · 拷贝模板
```bash
mkdir -p "项目/XXX/ppt/images"
# 风格 A
cp "<SKILL_ROOT>/assets/template.html" "项目/XXX/ppt/index.html"
# 风格 B
cp "<SKILL_ROOT>/assets/template-swiss.html" "项目/XXX/ppt/index.html"
```

### Step 3 · 填充内容
预检类名 → 规划主题节奏 → 挑布局 → 填充内容

### Step 4 · 对照检查清单自检
打开 `references/checklist.md` 逐项对照。

### Step 5 · 本地预览
```bash
open "项目/XXX/ppt/index.html"
```

### Step 6 · 迭代
根据用户反馈修改——模板 CSS 高度参数化。

## 核心设计原则

### 风格 A · 电子杂志风
1. 克制优于炫技
2. 结构优于装饰
3. 内容层级由字号和字体共同定义
4. 图片是第一公民
5. 节奏靠 hero 页交替

### 风格 B · 瑞士国际主义风
1. 单一锚点色
2. 极致字号对比
3. 无衬线只此一家
4. 直角纯色，无渐变/阴影/圆角
5. 网格至上，12-col grid
6. Hairline 是手术刀
7. 点阵装饰只在 hero 页透出