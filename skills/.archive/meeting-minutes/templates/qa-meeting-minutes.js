const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType } = require("docx");

// ============================================================
// Meeting Minutes Q&A Template — 调研纪要格式
// 对标：四方达调研纪要202605 格式
//
// Usage: Copy this file, replace Q&A content in `qaPairs` array,
// update title/meta, then run:
//   NODE_PATH=$(npm root -g) node this-file.js
// ============================================================

const TITLE = "XXXX 交流纪要";
const META = {
  time: "2026年X月",
  speaker: "XXX董秘/IR",
  audience: "买方/卖方研究员",
  format: "线上交流 / 线下访谈",
};

const qaPairs = [
  {
    q: "问题一？",
    a: "回答内容..."
  },
  {
    q: "问题二？",
    a: "回答内容..."
  },
  // Add more Q&A pairs...
];

// --- Do not edit below this line ---

const children = [];

// Title
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 360 },
  children: [new TextRun({ text: TITLE, bold: true, size: 28, font: "楷体" })]
}));

// Meta
const metaLines = [
  `时间：${META.time}`,
  `主讲人：${META.speaker}`,
  `参会方：${META.audience}`,
  `形式：${META.format}`,
];
metaLines.forEach(line => {
  children.push(new Paragraph({
    spacing: { after: 60 },
    children: [new TextRun({ text: line, size: 22, font: "楷体" })]
  }));
});

children.push(new Paragraph({ spacing: { after: 200 }, children: [] }));

// Q&A
qaPairs.forEach((pair, idx) => {
  children.push(new Paragraph({
    spacing: { before: 240, after: 80 },
    children: [
      new TextRun({ text: `${idx + 1}. `, bold: true, size: 22, font: "楷体" }),
      new TextRun({ text: pair.q, bold: true, size: 22, font: "楷体" })
    ]
  }));
  children.push(new Paragraph({
    spacing: { after: 120 },
    indent: { firstLine: 440 },
    children: [new TextRun({ text: pair.a, size: 22, font: "楷体" })]
  }));
});

// Footer
children.push(new Paragraph({ spacing: { before: 400 }, children: [] }));
children.push(new Paragraph({
  alignment: AlignmentType.RIGHT,
  children: [new TextRun({
    text: "纪要整理：AI辅助生成，经人工核对",
    size: 18, font: "楷体", italics: true, color: "888888"
  })]
}));

const doc = new Document({
  styles: {
    default: { document: { run: { font: "楷体", size: 22 } } }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  const outFile = "/Users/eason/Desktop/会议纪要_YYYYMMDD.docx";
  fs.writeFileSync(outFile, buffer);
  console.log(`OK: ${outFile}`);
});
