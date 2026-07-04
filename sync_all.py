#!/usr/bin/env python3
"""
站点全量同步脚本：生成新文章后，自动更新所有分类列表页 + 首页 + 提交上线。
所有内容生成任务的最后一步都调用此脚本。
"""
import os, re, json
from datetime import datetime

REPO_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"
ARTICLES_DIR = os.path.join(REPO_DIR, "articles")

CATEGORY_CONFIG = {
    "news": {
        "title": "热点追踪｜AiToollab",
        "desc": "GitHub趋势、新工具发布、AI行业动态，第一时间追踪报道。涵盖ChatGPT、Claude、Cursor等AI工具的实操动态，助你持续跟进AI浪潮。",
        "name": "🔥 热点追踪",
        "emoji": "🔥",
        "tag": "热点",
        "slug": "news",
    },
    "tutorials": {
        "title": "AI副业实战教程｜AiToollab",
        "desc": "从0到1的AI副业实战教程，覆盖工具使用、操作步骤、变现路径，普通人照着做就能赚到第一笔AI副业收入",
        "name": "💡 教程攻略",
        "emoji": "💡",
        "tag": "教程",
        "slug": "tutorials",
    },
    "cases": {
        "title": "AI副业真实案例｜AiToollab",
        "desc": "真实的AI副业赚钱案例拆解，包括项目玩法、投入成本、收益数据、可复制的操作方法",
        "name": "💰 赚钱案例",
        "emoji": "💰",
        "tag": "案例",
        "slug": "cases",
    },
    "startup-100": {
        "title": "AI工具真实测评｜AiToollab",
        "desc": "最新AI工具的真实测评，包括功能体验、价格对比、优缺点分析，帮你找到适合自己的AI工具",
        "name": "🧪 实验测评",
        "emoji": "🧪",
        "tag": "实验",
        "slug": "startup-100",
    }
}

TEMPLATE_HEAD = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="canonical" href="https://www.aitoollab.top/articles/{slug}/">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <meta name="robots" content="index, follow">
    <link rel="alternate" hreflang="x-default" href="https://www.aitoollab.top/articles/{slug}/">
    <link rel="alternate" hreflang="zh-CN" href="https://www.aitoollab.top/articles/{slug}/">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="https://www.aitoollab.top/og-articles.jpg">
    <meta property="og:url" content="https://www.aitoollab.top/articles/{slug}/">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="https://www.aitoollab.top/og-articles.jpg">
    <meta property="og:title:en" content="{en_title}" />
    <meta property="og:description:en" content="{en_desc}" />
    <meta name="description:en" content="{en_desc}" />
    <style>
        :root {{ --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #e6edf3; --muted: #8b949e; --accent: #f97316; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; font-size: 16px; }}
        a {{ color: var(--accent); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        header.page-header {{ text-align: center; padding: 60px 20px 40px; border-bottom: 1px solid var(--border); }}
        header.page-header h1 {{ font-size: 32px; margin-bottom: 12px; }}
        header.page-header .subtitle {{ color: var(--muted); font-size: 16px; max-width: 600px; margin: 0 auto; }}
        header.page-header .count {{ display: inline-block; background: rgba(255,255,255,0.06); padding: 4px 12px; border-radius: 20px; font-size: 13px; color: var(--muted); margin-top: 12px; }}
        nav.section-nav {{ display: flex; justify-content: center; gap: 4px; padding: 16px 20px; border-bottom: 1px solid var(--border); background: var(--card); position: sticky; top: 0; z-index: 100; }}
        nav.section-nav a {{ color: var(--muted); font-size: 14px; padding: 8px 16px; border-radius: 8px; transition: all .2s; }}
        nav.section-nav a:hover {{ color: var(--text); background: rgba(255,255,255,0.05); text-decoration: none; }}
        nav.section-nav a.active {{ color: var(--text); background: rgba(37,99,235,0.2); }}
        nav.section-nav a[data-section="news"] {{ color: var(--accent); border: 1px solid rgba(255,255,255,0.15); }}
        .container {{ max-width: 860px; margin: 0 auto; padding: 40px 20px; }}
        .article-grid {{ display: flex; flex-direction: column; gap: 16px; }}
        .article-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; transition: border-color .2s; }}
        .article-card:hover {{ border-color: var(--accent); }}
        .article-card .card-title {{ font-size: 17px; font-weight: 600; margin-bottom: 10px; }}
        .article-card .card-title a {{ color: var(--text); }}
        .article-card .card-title a:hover {{ color: var(--accent); text-decoration: none; }}
        .article-card .card-desc {{ color: var(--muted); font-size: 14px; margin-bottom: 12px; line-height: 1.6; }}
        .article-card .card-meta {{ display: flex; gap: 16px; font-size: 13px; color: var(--muted); align-items: center; }}
        .article-card .card-tag {{ background: rgba(255,255,255,0.06); padding: 3px 10px; border-radius: 6px; }}
        .back-link {{ text-align: center; margin-top: 40px; }}
        .back-link a {{ color: var(--muted); font-size: 14px; }}
        #back-to-top{{position:fixed;bottom:24px;right:24px;width:44px;height:44px;border-radius:50%;background:#2563eb;color:#fff;border:none;cursor:pointer;font-size:18px;opacity:0;transition:opacity .3s;z-index:999;pointer-events:none}}
        #back-to-top.show{{opacity:.85;pointer-events:auto}}
        #back-to-top:hover{{opacity:1}}
        @media (max-width: 600px) {{ header.page-header h1 {{ font-size: 26px; }} }}
    </style>
</head>
<body>
<header class="page-header">
    <h1>{emoji} {name}</h1>
    <p class="subtitle">{desc}</p>
    <span class="count">{count}篇</span>
</header>
<nav class="section-nav">
    <a href="/tutorials/">💡 教程</a>
    <a href="/articles/news/" data-section="news">🔥 热点</a>
    <a href="/articles/cases/">💰 案例</a>
    <a href="/articles/startup-100/" data-section="startup-100">🧪 实验</a>
    <a href="/articles/">全部</a>
</nav>
<div class="container">
<div class="category-intro" style="background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 32px;">
    <h2 style="margin-bottom: 16px; font-size: 20px;">📰 本分类包含什么内容？</h2>
    <p style="margin-bottom: 12px; color: var(--text);">{desc}</p>
    <ul style="margin: 16px 0 0 20px; color: var(--muted);">
        <li style="margin-bottom: 8px;">✅ 每天更新最新的AI行业热点和新工具发布消息</li>
        <li style="margin-bottom: 8px;">✅ 深度解读热点事件背后的赚钱机会和行业趋势</li>
        <li style="margin-bottom: 8px;">✅ 所有内容都是原创分析，不是复制粘贴的新闻通稿</li>
    </ul>
</div>
<div class="article-grid">
'''

TEMPLATE_CARD = '''        <div class="article-card"><div class="card-title">
                <a href="{url}">{title}</a>
            </div>
            <div class="card-desc">{desc}</div>
            <div class="card-meta">
                <span class="card-tag">{tag}</span>
                <span>📅 {date}</span>
            </div>
        </div>
'''

TEMPLATE_TAIL = '''    </div>
<div class="back-link">
        <a href="/articles/">← 返回文章总览</a>
    </div>
</div>
<button id="back-to-top" onclick="window.scrollTo({top:0,behavior:'smooth'})" aria-label="返回顶部">↑</button>
<script>
window.addEventListener('scroll',function(){var b=document.getElementById('back-to-top');b.classList.toggle('show',window.scrollY>400);});
</script>
</body>
</html>
'''

def get_articles(category):
    """扫描分类目录，返回所有文章信息按日期降序"""
    articles = []
    # tutorials/ is at repo root, not under articles/
    if category == "tutorials":
        cat_dir = os.path.join(REPO_DIR, "tutorials")
        url_prefix = "/tutorials/"
    else:
        cat_dir = os.path.join(ARTICLES_DIR, category)
        url_prefix = f"/articles/{category}/"
    if not os.path.isdir(cat_dir):
        return articles
    for entry in sorted(os.listdir(cat_dir), reverse=True):
        entry_path = os.path.join(cat_dir, entry)
        html_path = os.path.join(entry_path, "index.html")
        if not os.path.isdir(entry_path) or not os.path.exists(html_path):
            continue
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        title_m = re.search(r'<title>(.*?)</title>', content)
        desc_m = re.search(r'<meta name="description" content="(.*?)"[>]', content)
        date_m = re.search(r'(\d{4}-\d{2}-\d{2})', content)
        if title_m:
            title = title_m.group(1).split('｜')[0].strip()
            title = title.replace(' - AiToollab', '').strip()
            desc = desc_m.group(1)[:60] + "。。" if desc_m and len(desc_m.group(1)) > 60 else (desc_m.group(1) if desc_m else "")
            date = date_m.group(1) if date_m else ""
            articles.append({
                "title": title, "desc": desc, "date": date,
                "url": f"{url_prefix}{entry}/",
            })
    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles

def generate_listing(category, articles):
    """生成完整的分类列表页HTML"""
    cfg = CATEGORY_CONFIG[category]
    # Schema JSON-LD itemListElement
    items = []
    for i, a in enumerate(articles):
        items.append({"@type": "ListItem", "position": i + 4,
                       "url": f"https://www.aitoollab.top{a['url']}", "name": a["title"]})
    # Add nav items
    nav_items = [
        {"@type": "ListItem", "position": 1, "url": "https://www.aitoollab.top/tutorials/", "name": "💡 教程"},
        {"@type": "ListItem", "position": 2, "url": "https://www.aitoollab.top/articles/news/", "name": "🔥 热点"},
        {"@type": "ListItem", "position": 3, "url": "https://www.aitoollab.top/articles/cases/", "name": "💰 案例"},
    ]
    all_items = nav_items + items + [{"@type": "ListItem", "position": len(items) + 4,
                                       "url": "https://www.aitoollab.top/articles/", "name": "← 返回文章总览"}]
    schema_html = f'''    <script type="application/ld+json">
{json.dumps({"@context": "https://schema.org", "@type": "CollectionPage",
    "@id": f"https://www.aitoollab.top/articles/{category}/",
    "url": f"https://www.aitoollab.top/articles/{category}/",
    "name": f"{cfg['name']}｜AiToollab",
    "description": cfg['desc'],
    "isPartOf": {"@id": "https://www.aitoollab.top/"},
    "mainEntity": {"@type": "ItemList", "itemListElement": all_items}
}, ensure_ascii=False, indent=4)}
    </script>
'''
    # Build article cards
    cards = ""
    for a in articles:
        d = a["desc"][:120] + "。。" if len(a["desc"]) > 120 else a["desc"]
        cards += TEMPLATE_CARD.format(url=a["url"], title=a["title"], desc=d, tag=cfg["tag"], date=a["date"])
    # Build full HTML
    html = TEMPLATE_HEAD.format(
        slug=category, title=cfg["title"], desc=cfg["desc"],
        en_title=f"{cfg['name']} | AiToollab",
        en_desc=cfg["desc"],
        emoji=cfg["emoji"], name=cfg["name"], count=len(articles)
    )
    html += schema_html
    html += cards
    html += TEMPLATE_TAIL
    return html

def _rebuild_sitemap(repo_dir):
    """扫描仓库中所有 HTML 文件，重建 sitemap.xml（不遗漏任何页面）"""
    BASE_URL = "https://www.aitoollab.top"
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 收集所有 index.html 路径
    html_files = []
    for root, dirs, files in os.walk(repo_dir):
        if 'node_modules' in root or '.git' in root:
            continue
        if 'index.html' in files:
            rel = os.path.relpath(os.path.join(root, 'index.html'), repo_dir)
            html_files.append(rel)
    html_files.sort()
    
    urls = []
    for f in html_files:
        url = f"{BASE_URL}/{f.replace('/index.html', '/')}"
        urls.append(url)
    
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{url}</loc>')
        lines.append(f'    <lastmod>{today}</lastmod>')
        lines.append('    <changefreq>weekly</changefreq>')
        lines.append('    <priority>1.0</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')
    
    sitemap_path = os.path.join(repo_dir, "sitemap.xml")
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"   🗺️ sitemap rebuilt: {len(urls)} URLs")


def sync_all(commit_msg=None):
    """全量同步：更新所有分类列表 + 首页 + 提交"""
    if not os.path.isdir(REPO_DIR):
        print(f"❌ 路径错误: {REPO_DIR}")
        return False
    os.chdir(REPO_DIR)
    
    # 1. 更新所有分类列表页
    updated = []
    for cat in ["news", "tutorials", "cases", "startup-100"]:
        articles = get_articles(cat)
        html = generate_listing(cat, articles)
        if cat == "tutorials":
            out_path = os.path.join(REPO_DIR, "tutorials", "index.html")
        else:
            out_path = os.path.join(ARTICLES_DIR, cat, "index.html")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        updated.append(f"{cat}: {len(articles)}篇")
    
    # 2. 更新首页
    all_articles = []
    for cat in ["news", "cases", "tutorials", "startup-100"]:
        all_articles.extend(get_articles(cat))
    all_articles.sort(key=lambda x: x["date"], reverse=True)
    top6 = all_articles[:6]
    
    with open(os.path.join(REPO_DIR, "index.html"), 'r', encoding='utf-8') as f:
        home_html = f.read()
    
    # 替换最新文章区域
    cards_html = ""
    CAT_MAP = {"news": "热点", "tutorials": "教程", "cases": "案例", "startup-100": "实验"}
    for a in top6:
        # 推断分类
        cat = a["url"].split("/")[2] if len(a["url"].split("/")) > 2 else "news"
        tag = CAT_MAP.get(cat, "热点")
        d = a["desc"][:80] + "。。" if len(a["desc"]) > 80 else a["desc"]
        cards_html += f'''            <a href="{a['url']}" class="article-card">
                <span class="card-tag">{tag}</span>
                <h3>{a['title']}</h3>
                <p>{d}</p>
                <span class="card-date">{a['date']}</span>
            </a>
'''
    # Find and replace the article-grid section
    start_m = '        <div class="article-grid">\n'
    end_m = '        </div>\n        <div class="section-more">'
    si = home_html.find(start_m)
    ei = home_html.find(end_m, si)
    if si != -1 and ei != -1:
        new_section = start_m + cards_html + '        </div>'
        old_section = home_html[si:ei + len(end_m)]
        home_html = home_html.replace(old_section, new_section + '\n        <div class="section-more">', 1)
    
    # 更新日期标识
    today = datetime.now().strftime("%Y-%m-%d")
    home_html = re.sub(r'<div class="hero-badge">.*?</div>',
                       f'<div class="hero-badge">{today} · 持续更新</div>', home_html, 1)
    # 更新统计数字
    home_html = re.sub(
        r'(<span class="stat-num">)持续(</span>\s*<span class="stat-label">每周更新内容</span>)',
        f'\\g<1>{len(all_articles)}篇\\g<2>', home_html, 1)
    
    with open(os.path.join(REPO_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(home_html)
    
    updated.append(f"homepage: {len(top6)}篇最新")
    updated.append(f"总计: {len(all_articles)}篇")
    
    # 3. 重建 sitemap（扫描所有 HTML 文件，确保无遗漏）
    _rebuild_sitemap(REPO_DIR)
    sitemap_count = sum(1 for _ in open(os.path.join(REPO_DIR, "sitemap.xml")) if '<loc>' in _)
    updated.append(f"sitemap: {sitemap_count}条")
    
    # 4. 提交并推送
    msg = commit_msg or f"feat: 全量同步 - {today}"
    os.system(f'git add . && git commit -m "{msg}" && git push')
    
    print(f"✅ 全量同步完成: {today}")
    for u in updated:
        print(f"   • {u}")
    return True

if __name__ == "__main__":
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    sync_all(msg)
