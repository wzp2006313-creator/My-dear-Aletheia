#!/usr/bin/env python3
"""Convert Markdown report to PDF via HTML, using weasyprint."""

import argparse
import os
import sys

import markdown
from weasyprint import HTML


CSS = """
@page {
    size: A4;
    margin: 2cm 2.5cm;
    @bottom-center {
        content: "Page " counter(page);
        font-size: 9pt;
        color: #888;
    }
}

body {
    font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", "SimSun", sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a1a;
}

h1 {
    font-size: 20pt;
    color: #1a1a2e;
    border-bottom: 2px solid #1a1a2e;
    padding-bottom: 8px;
    margin-top: 30px;
}

h2 {
    font-size: 15pt;
    color: #16213e;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4px;
    margin-top: 24px;
}

h3 {
    font-size: 13pt;
    color: #0f3460;
    margin-top: 18px;
}

h4 {
    font-size: 11.5pt;
    color: #533483;
    margin-top: 14px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 9.5pt;
}

th {
    background: #1a1a2e;
    color: white;
    padding: 6px 10px;
    text-align: left;
    font-weight: 600;
}

td {
    padding: 5px 10px;
    border-bottom: 1px solid #e8e8e8;
}

tr:nth-child(even) td {
    background: #f8f9fa;
}

blockquote {
    border-left: 3px solid #1a1a2e;
    margin: 12px 0;
    padding: 8px 16px;
    background: #f5f5f5;
    color: #555;
}

code {
    background: #f0f0f0;
    padding: 1px 5px;
    border-radius: 3px;
    font-family: "Fira Code", "Consolas", monospace;
    font-size: 9pt;
}

pre {
    background: #1a1a2e;
    color: #e0e0e0;
    padding: 12px 16px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.5;
}

pre code {
    background: none;
    color: inherit;
    padding: 0;
}

ul, ol {
    padding-left: 24px;
}

li {
    margin: 3px 0;
}

img {
    max-width: 100%;
    margin: 8px 0;
}

strong {
    color: #1a1a2e;
}

a {
    color: #0f3460;
    text-decoration: none;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}
"""


def md_to_pdf(md_path: str, pdf_path: str, html_path: str | None = None):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_body = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc", "attr_list"],
    )

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # Always save HTML
    out_html = html_path or os.path.splitext(pdf_path)[0] + ".html"
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"HTML saved to {out_html}")

    HTML(string=full_html).write_pdf(pdf_path)
    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown report to PDF + HTML")
    parser.add_argument("--md-file", required=True, help="Input Markdown file")
    parser.add_argument("--output", required=True, help="Output PDF file")
    args = parser.parse_args()

    if not os.path.exists(args.md_file):
        print(f"Error: {args.md_file} not found", file=sys.stderr)
        sys.exit(1)

    try:
        md_to_pdf(args.md_file, args.output)
        print(f"PDF saved to {args.output}")
    except Exception as e:
        print(f"PDF conversion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
