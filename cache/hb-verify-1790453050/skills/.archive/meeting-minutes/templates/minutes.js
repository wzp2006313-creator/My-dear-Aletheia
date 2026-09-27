const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType } = require("docx");

// qaPairs: [{ q: "问题", a: "回答" }, ...]
// title: 标题
// metaLines: ["时间：...", "主讲人：...", "参会方：...", "形式：..."]
// outputPath: 输出路径

function generate(qaPairs, title, metaLines, outputPath) {
  const children = [];

  // Title
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 360 },
    children: [new TextRun({ text: title, bold: true, size: 28, font: "楷体" })]
  }));

  // Meta
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
    children: [new TextRun({ text: "纪要整理：AI辅助生成，经人工核对", size: 18, font: "楷体", italics: true, color: "888888" })]
  }));

  const doc = new Document({
    styles: {
      default: { document: { run: { font: "楷体", size: 22 } } }
    },
    sections: [{
      properties: {
        page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
      },
      children
    }]
  });

  Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(outputPath, buffer);
    console.log(`OK: ${outputPath}`);
  });
}

// Usage:
// const title = "天禄科技 TAC膜国产化项目交流纪要";
// const metaLines = ["时间：2026年", "主讲人：天禄科技董秘", "参会方：买方/卖方研究员", "形式：线上交流"];
// const qaPairs = [{ q: "项目背景是什么？", a: "..." }, ...];
// generate(qaPairs, title, metaLines, "/Users/eason/Desktop/output.docx");

module.exports = { generate };
