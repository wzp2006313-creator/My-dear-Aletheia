---
name: research-memo
description: 将调研录音/转写文本整理为机构调研纪要（Q&A格式Word文档）。触发场景：用户提供调研录音、转写文字、或飞书妙记链接，要求生成纪要。
---

# 调研纪要生成

## 输入

- 调研录音文件（mp3/wav/m4a）或飞书妙记链接
- 或用户直接粘贴的转写文本

## 输出

一份楷体排版的 .docx 调研纪要，格式如下。

## 格式规范

### 字体

全文使用 **楷体**。正文不加粗；标题、元信息、问题、回答中的小标签加粗。

### 文档结构

```
标题：36pt 楷体 加粗 居中
调研时间：21pt 楷体 加粗 居中
调研对象：21pt 楷体 加粗 居中
调研地点：21pt 楷体 加粗 居中

1. 问题一（23pt 加粗）
客户：（22pt 加粗）
正文（22pt 楷体 不加粗）
  关键标签：内容（标签加粗，正文不加粗）

2. 问题二
...
```

### 回答内小标签规则

只在**真正重要的数据节点**加粗标签，不要让每个句子都带标签。参考范例：

- ✅ 好的用法：`价格：`, `毛利率：`, `产能利用率：`, `供需拐点：`, `定增进度：`, `城市油田战略：`
- ❌ 过度拆分：每句话都搞一个加粗标签

大段内容自然写，不加标签也不打断。

### 生成方式

```bash
cd /tmp && npm install docx  # 如果没有的话
```

然后用 docx-js 生成，参考模板如下（复制到 `/tmp/gen_memo.js` 修改内容执行）：

```javascript
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType } = require("docx");

const KAI = "楷体";
function bold(text, size = 22) { return new TextRun({ text, size, font: KAI, bold: true }); }
function body(text, size = 22) { return new TextRun({ text, size, font: KAI, bold: false }); }

const qa = [
  {
    q: "问题内容",
    a: [
      { text: "普通文字段落..." },
      { label: "关键标签：", text: "标签后的内容..." },
    ],
  },
  // ...更多QA
];

const children = [];
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [bold("标题", 36)] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [bold("调研时间：...", 21)] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [bold("调研对象：...", 21)] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [bold("调研地点：线下交流访谈", 21)] }));

qa.forEach((item, idx) => {
  children.push(new Paragraph({ spacing: { before: 280, after: 120 }, children: [bold(`${idx + 1}. ${item.q}`, 23)] }));
  children.push(new Paragraph({ spacing: { after: 100 }, children: [bold("客户：")] }));
  item.a.forEach(seg => {
    if (seg.label) {
      children.push(new Paragraph({ spacing: { after: 100 }, children: [bold(seg.label), body(seg.text)] }));
    } else {
      children.push(new Paragraph({ spacing: { after: 100 }, children: [body(seg.text)] }));
    }
  });
});

children.push(new Paragraph({ spacing: { before: 400 }, children: [body("免责声明：本纪要为调研交流记录整理，仅供参考，不构成投资建议。", 18)] }));

const doc = new Document({
  styles: { default: { document: { run: { font: KAI, size: 22 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/Users/eason/Downloads/调研纪要_<公司名>_<日期>.docx", buf);
  console.log("OK");
});
```

## 内容处理要点

1. 从对话中识别出所有问题，提炼为简洁的书面语
2. 回答保持原意，去除口语填充词（"就是说"、"那个"、"对吧"等）、去重、合并散落的相关内容
3. 将回答中的关键数据点用加粗标签标出（产能利用率：、价格：、毛利率：等）
4. 不要在回答末尾加分析评论，保持纪要的客观记录属性
5. 每个回答尽量控制在合理篇幅，过长的回答适当分段

## 注意事项

- 如果输入是录音文件，先加载 `whisper` skill 转写
- 如果输入是飞书妙记链接，用 `feishu_doc_read` 读取
- 生成前确认公司名、日期、调研对象等信息准确
