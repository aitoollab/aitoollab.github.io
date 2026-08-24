#!/usr/bin/env python3
"""批量修复 meta description 太短的问题（GSC 报告：<70字符）。

读 CSV 里的 URL 列表，对每个页面：
1. 提取正文前几段的关键内容
2. 生成 100-150 字符的 description
3. 替换 meta description + og:description

用法：python3 fix_short_desc.py /path/to/csv.csv
"""
import csv, os, re, sys, html as html_mod

REPO = "/home/agentuser/.hermes/hermes-agent/aitoollab"

def load_urls(csv_path):
    urls = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if row and row[0].startswith("http"):
                urls.append(row[0])
    return urls

def extract_text_from_html(fpath):
    with open(fpath, encoding="utf-8") as f:
        c = f.read()
    # 去 script/style
    c = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", c, flags=re.S)
    # 正文 = h1 之后 到 cta-box / related / footer 之前（跳过 meta 信息区）
    m = re.search(r"<h1[^>]*>(.*?)</h1>\s*<div class=\"(?:meta|article-meta)\">.*?</div>\s*</header>\s*(.*?)(?:<div class=\"(?:cta-box|cta|related|related-articles)\"|</body>)", c, flags=re.S)
    if not m:
        # 回退1: h1 直接到 cta
        m = re.search(r"<h1[^>]*>(.*?)</h1>(.*?)(?:<div class=\"(?:cta-box|cta|related|related-articles)\"|</body>)", c, flags=re.S)
    if m:
        h1 = m.group(1)
        body = m.group(2)
    else:
        m2 = re.search(r"<div class=\"content\">(.*?)(?:<div class=\"(?:cta-box|cta|related|related-articles)\"|</body>)", c, flags=re.S)
        h1 = ""
        body = m2.group(1) if m2 else c
    # 去标签
    text = re.sub(r"<[^>]+>", " ", body)
    text = html_mod.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def make_desc(title, text, max_len=140):
    """生成 description：标题核心 + 正文关键信息，截断到 max_len"""
    # 去掉标题里的 SEO 修饰词
    t = title.replace(" - AiToollab", "").replace("｜AiToollab", "").strip()
    # 找正文第一句有信息量的（>30字符）
    sentences = re.split(r"[。！？!?]", text)
    body_part = ""
    for s in sentences:
        s = s.strip()
        if len(s) < 25:
            continue
        if s.startswith(("本文", "这篇文章", "欢迎", "首页", "教程", "发布于", "分类", "阅读约")):
            continue
        if any(k in s for k in ("｜", "|", "发布于", "分类：", "首页 副业", "提示词全家桶", "导航", "社交媒体运营", "副业赚钱 社交媒体", "面包屑")):
            continue
        if t and (t in s or s in t):
            continue
        body_part = s
        break
    desc = f"{t}。{body_part}" if body_part else t
    desc = desc[:max_len]
    # 避免截断到一半
    if len(desc) == max_len:
        cut = max(desc.rfind("。"), desc.rfind(","), desc.rfind("，"))
        if cut > 60:
            desc = desc[:cut+1]
    return desc

def fix_file(fpath, url, force=False):
    with open(fpath, encoding="utf-8") as f:
        c = f.read()
    # 标题
    tm = re.search(r"<title>(.*?)</title>", c, flags=re.S)
    title = tm.group(1).strip() if tm else ""
    text = extract_text_from_html(fpath)
    new_desc = make_desc(title, text)
    # 检查当前 description 是否已达标
    cur = re.search(r'<meta name="description" content="([^"]*)"', c)
    cur_len = len(cur.group(1)) if cur else 0
    if not force and cur_len >= 70:
        return None, cur_len
    if len(new_desc) < 70:
        # 不够长就再拼正文第二句
        sentences = re.split(r"[。！？!?]", text)
        extra = "".join(s.strip() for s in sentences[1:3] if s.strip())
        new_desc = (new_desc + "。" + extra)[:150]
    # 替换 description（含 HTML 实体转义）
    esc = new_desc.replace("&", "&amp;").replace('"', "&quot;")
    n1 = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{esc}"', c, count=1)
    n2 = re.sub(r'<meta property="og:description" content="[^"]*"', f'<meta property="og:description" content="{esc}"', n1, count=1)
    if n2 == c:
        return None, 0
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(n2)
    return new_desc, len(new_desc)

def main():
    args = sys.argv[1:]
    force = "--force" in args
    csv_path = next((a for a in args if a.endswith(".csv")), None)
    if not csv_path:
        print("用法: python3 fix_short_desc.py /path/to.csv [--force]")
        return
    urls = load_urls(csv_path)
    print(f"待处理: {len(urls)} 个URL (force={force})")
    fixed, skipped, errs = 0, 0, []
    for url in urls:
        path = url.replace("https://www.aitoollab.top/", "")
        fpath = os.path.join(REPO, path, "index.html")
        if not os.path.exists(fpath):
            errs.append((url, "文件不存在"))
            continue
        desc, ln = fix_file(fpath, url, force=force)
        if desc is None:
            skipped += 1
        else:
            fixed += 1
            print(f"  ✅ {path[:60]} -> {ln}字符")
    print(f"\n完成: 修复{fixed} 跳过{skipped} 错误{len(errs)}")
    for u, e in errs[:5]:
        print(f"  ❌ {u} ({e})")

if __name__ == "__main__":
    main()
