#!/usr/bin/env python3
"""
每日更新首页：自动扫描最新文章，刷新首页"最新文章"区域，更新统计数字。
每天07:00由cron自动执行。
"""
import os, re, json
from datetime import datetime

REPO_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"
INDEX_PATH = os.path.join(REPO_DIR, "index.html")
ARTICLES_DIR = os.path.join(REPO_DIR, "articles")

# 文章类型映射
CATEGORY_MAP = {
    "news": {"name": "热点", "icon": "🔥"},
    "seo": {"name": "教程", "icon": "💡"},
    "cases": {"name": "案例", "icon": "💰"},
    "startup-100": {"name": "实验", "icon": "🧪"},
}

def get_latest_articles(limit=6):
    """从所有分类目录获取最新文章，按发布日期排序"""
    articles = []
    for cat_key, cat_info in CATEGORY_MAP.items():
        cat_dir = os.path.join(ARTICLES_DIR, cat_key)
        if not os.path.isdir(cat_dir):
            continue
        for entry in os.listdir(cat_dir):
            entry_path = os.path.join(cat_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            article_html = os.path.join(entry_path, "index.html")
            if not os.path.exists(article_html):
                continue
            with open(article_html, 'r', encoding='utf-8') as f:
                content = f.read()
            # 提取标题和描述
            title_match = re.search(r'<title>(.*?)</title>', content)
            desc_match = re.search(r'<meta name="description" content="(.*?)"[>]', content)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
            if title_match and date_match:
                title = title_match.group(1).split('｜')[0].strip()
                desc = desc_match.group(1) if desc_match else ""
                if len(desc) > 60:
                    desc = desc[:60] + "。。"
                date = date_match.group(1)
                articles.append({
                    "title": title,
                    "desc": desc,
                    "date": date,
                    "url": f"/articles/{cat_key}/{entry}/",
                    "tag": cat_info["name"],
                })
    # 按日期从新到旧排序
    articles.sort(key=lambda x: x["date"], reverse=True)
    return articles[:limit]

def count_articles():
    """统计各分类文章数量"""
    counts = {"tutorials": 0, "cases": 0, "news": 0, "startup-100": 0}
    for cat in counts:
        cat_dir = os.path.join(ARTICLES_DIR, cat)
        if os.path.isdir(cat_dir):
            for entry in os.listdir(cat_dir):
                if os.path.isdir(os.path.join(cat_dir, entry)) and \
                   os.path.exists(os.path.join(cat_dir, entry, "index.html")):
                    counts[cat] += 1
    total = sum(counts.values())
    return total, counts

def update_homepage():
    """更新首页的'最新文章'区域"""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 更新最新文章区域
    articles = get_latest_articles(6)
    today = datetime.now().strftime("%Y-%m-%d")
    
    cards_html = ""
    for i, article in enumerate(articles[:6]):
        cards_html += f'''            <a href="{article['url']}" class="article-card">
                <span class="card-tag">{article['tag']}</span>
                <h3>{article['title']}</h3>
                <p>{article['desc']}</p>
                <span class="card-date">{article['date']}</span>
            </a>
'''
    
    # 找到"最新文章"区域并替换
    start_marker = '        <div class="article-grid">\n'
    end_marker = '        </div>\n        <div class="section-more">'
    
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ 找不到最新文章区域")
        return False
    
    new_section = start_marker + cards_html + '        </div>'
    old_section = html[start_idx:end_idx + len(end_marker)]
    
    # 确保精确匹配
    if start_marker in old_section:
        html = html.replace(old_section, new_section + '\n        <div class="section-more">', 1)
    else:
        print("❌ 替换区域不匹配")
        return False

    # 2. 更新日期标识
    html = re.sub(r'<div class="hero-badge">.*?</div>', 
                  f'<div class="hero-badge">{today} · 持续更新</div>', html, 1)
    
    # 3. 更新统计数字
    total, counts = count_articles()
    # 找到stats-row并更新第三个数字
    html = re.sub(
        r'(<span class="stat-num">)持续(</span>\s*<span class="stat-label">每周更新内容</span>)',
        f'\\g<1>{total}篇\\g<2>', html, 1
    )
    
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 首页已更新：{today}")
    print(f"   - 最新文章：{len(articles)}篇 (来自news/seo/cases/startup)")
    print(f"   - 文章总数：{total}篇")
    for title in [a["title"] for a in articles]:
        print(f"     • {title}")
    return True

if __name__ == "__main__":
    success = update_homepage()
    if success:
        # git commit and push
        os.system(f'cd {REPO_DIR} && git add index.html && git commit -m "feat: 每日首页更新 - {datetime.now().strftime("%m-%d")}" && git push')
        print("✅ 已提交并推送")
    else:
        print("❌ 更新失败")
