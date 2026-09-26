// 小红书搜索结果页笔记提取脚本（agent-browser eval 用）
// 用法: agent-browser eval "$(cat scripts/extract_xhs.js)"
// 输出: JSON 数组 [{id, href, title, author, date, like, raw}]
JSON.stringify(
  [...document.querySelectorAll('section.note-item, section[class*=note]')]
    .map((c) => {
      const a = c.querySelector('a[href*="/explore/"]');
      if (!a) return null;
      const m = (a.href.match(/explore\/([0-9a-f]+)/) || [])[1];
      if (!m) return null;
      const t = c.innerText.split('\n').filter((x) => x.trim());
      return {
        id: m,
        href: a.href,
        title: t[0] || '',
        author: t[1] || '',
        date: t[2] || '',
        like: t[3] || '',
        raw: c.innerText.slice(0, 180).replace(/\n/g, ' | '),
      };
    })
    .filter(Boolean)
);
