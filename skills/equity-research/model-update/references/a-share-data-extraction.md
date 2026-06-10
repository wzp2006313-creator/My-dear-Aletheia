# A-Share Financial Data Extraction

Chinese financial websites (10jqka, eastmoney, sina finance, cls.cn) commonly block `web_extract` with "Blocked: URL targets a private or internal network address". Use these fallback techniques instead.

## 同花顺 (10jqka) F10 Product Breakdown

Best source for product-level revenue/cost/profit/gross margin data.

URL pattern: `http://basic.10jqka.com.cn/{CODE}/operate.html`

**Technique**: browser_navigate → browser_console JavaScript extraction

```js
// Find the revenue breakdown table and extract all rows
(() => {
  const tables = document.querySelectorAll('table');
  for (let i = 0; i < tables.length; i++) {
    const rows = tables[i].querySelectorAll('tr');
    if (rows.length > 3) {
      const headers = [];
      rows[0].querySelectorAll('th, td').forEach(h => headers.push(h.textContent.trim()));
      if (headers.some(h => h.includes('营业收入') || h.includes('毛利率'))) {
        const data = [];
        rows.forEach(r => {
          const cells = r.querySelectorAll('th, td');
          data.push([...cells].map(c => c.textContent.trim()).join(' | '));
        });
        return JSON.stringify(data.slice(0, 12), null, 2);
      }
    }
  }
  return 'not found';
})()
```

The table contains columns: 业务名称 | 营业收入 | 收入比例 | 营业成本 | 成本比例 | 主营利润 | 利润比例 | 毛利率

Click "利润比例" tab to ensure the profit column is visible before extracting.

## Key data points to capture

- 分产品: 超硬刀具 / 硬质合金刀具 / 超硬材料 / 其他 → revenue, cost, profit, gross margin, profit share
- 分地区: 国内 / 国外 → revenue, cost, gross margin
- 分行业: 制造业 / 其他业务

## Other blocked sites

- **新浪财经 annual reports**: `money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?stockid={CODE}` → try `web_search` for AI-generated summaries instead
- **东方财富**: `emweb.eastmoney.com` → often blocked; use 10jqka as alternative
- **财联社**: `cls.cn` → blocked; use web_search snippets
- **搜狐证券**: `q.stock.sohu.com` → sometimes accessible, has revenue breakdown

## Search query patterns for Chinese financial data

- Product segmentation: `"{stock_name}" "2025" 年报 "分产品" "营收" "毛利率"`
- Regional breakdown: `"{stock_name}" 境外收入 海外 毛利率 历年`
- Historical revenue: `"{stock_name}" 历年营收 2016 2017 2018 ... 年均报`
- Profit by product: `"{stock_name}" "利润比例" "超硬刀具" "硬质合金" 2025`
