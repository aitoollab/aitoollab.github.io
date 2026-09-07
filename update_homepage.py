#!/usr/bin/env python3
"""
每日更新首页：自动扫描最新文章，刷新首页"最新文章"区域，更新统计数字。
每天07:00由cron自动执行。

卡片包含：封面图（复用仓库已生成的 og 图）、分类标签、收入数字徽章、标题、摘要、日期。
新增文章只要按现有命名放好 og-<slug>.jpg，首页卡片就会自动带上封面，无需改本脚本。
"""
import os, re, json
from datetime import datetime

# 服务器上的仓库路径；本地验证可用环境变量覆盖：REPO_DIR=/path/to/repo python3 update_homepage.py
REPO_DIR = os.environ.get("REPO_DIR", "/home/agentuser/.hermes/hermes-agent/aitoollab")
INDEX_PATH = os.path.join(REPO_DIR, "index.html")
ARTICLES_DIR = os.path.join(REPO_DIR, "articles")
TUTORIALS_DIR = os.path.join(REPO_DIR, "tutorials")

# 文章类型映射
CATEGORY_MAP = {
    "news": {"name": "热点", "icon": "🔥"},
    "seo": {"name": "教程", "icon": "💡"},
    "cases": {"name": "案例", "icon": "💰"},
    "startup-100": {"name": "实验", "icon": "🧪"},
}

# og 封面图的命名前缀（按仓库实际命名习惯依次尝试）
COVER_PREFIXES = ("og-", "og-daily-", "og-cases-", "og-news-", "og-seo-")

# 收入数字：只从标题/摘要里"提取"，提取不到就不显示，绝不编造数字
MONEY_RE = re.compile(
    r'(\d[\d,]*到\d[\d,]*元|一单\d[\d,]*到\d[\d,]*元|月入\d[\d,]*元|'
    r'\d[\d,]*元/单|\d[\d,]*元/月|¥\d[\d,]*元)')


def _read(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


def _extract_title(content):
    m = re.search(r'<title>(.*?)</title>', content, re.S)
    if not m:
        return None
    t = m.group(1).strip()
    # 去掉品牌后缀：这批文章标题混用了 "｜AiToollab"、" — AiToollab"、" - AiToollab" 三种写法
    t = t.split('｜')[0]
    t = re.sub(r'\s*[—–-]{1,2}\s*AiToollab\s*$', '', t, flags=re.I)
    t = re.sub(r'\s*[—–-]{1,2}\s*AI副业[^—–-]*$', '', t)
    return t.strip()


def _extract_desc(content):
    m = re.search(r'<meta name="description" content="(.*?)"[>]', content, re.S)
    desc = m.group(1) if m else ""
    if len(desc) > 60:
        # 在60字附近按句号/分号截断，不加"。。"
        cut = desc[:70]
        for punct in ("。", "；", "，", "、"):
            pos = cut.rfind(punct)
            if pos >= 30:
                return cut[:pos].rstrip(punct)
        return cut.rstrip()
    return desc.rstrip()


def _extract_date(content, slug=""):
    m = re.search(r'(\d{4}-\d{2}-\d{2})', content)
    if m:
        return m.group(1)
    m = re.search(r'(20\d{2})(\d{2})(\d{2})', slug)      # 目录名里的 20260907
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def find_cover(slug):
    """按命名规则在仓库根目录找该文章的 og 封面图，找不到返回 None。"""
    for prefix in COVER_PREFIXES:
        cand = f"{prefix}{slug}.jpg"
        if os.path.exists(os.path.join(REPO_DIR, cand)):
            return "/" + cand
    return None


def find_money(title, desc=""):
    """提炼收入数字做成徽章，如 '300到2000/单'。"""
    m = MONEY_RE.search(title) or MONEY_RE.search(desc)
    if not m:
        return None
    text = m.group(1).replace('一单', '').replace('¥', '')
    if '到' in text:
        return text.replace('元', '') + '/单'
    if '月入' in text:
        return text.replace('月入', '¥') + '/月'
    return text


def collect_articles():
    """收集全部候选文章（articles 四个分类 + tutorials），按发布日期倒序。"""
    articles = []

    for cat_key, cat_info in CATEGORY_MAP.items():
        cat_dir = os.path.join(ARTICLES_DIR, cat_key)
        if not os.path.isdir(cat_dir):
            continue
        for entry in os.listdir(cat_dir):
            html_path = os.path.join(cat_dir, entry, "index.html")
            if not os.path.isdir(os.path.join(cat_dir, entry)) or not os.path.exists(html_path):
                continue
            content = _read(html_path)
            title, date = _extract_title(content), _extract_date(content, entry)
            if not (title and date):
                continue
            articles.append({
                "title": title,
                "desc": _extract_desc(content),
                "date": date,
                "url": f"/articles/{cat_key}/{entry}/",
                "tag": cat_info["name"],
                "slug": entry,
            })

    # tutorials：首页一直在展示教程卡，必须纳入扫描，否则每次运行会把教程卡挤掉
    if os.path.isdir(TUTORIALS_DIR):
        for entry in os.listdir(TUTORIALS_DIR):
            html_path = os.path.join(TUTORIALS_DIR, entry, "index.html")
            if not os.path.isdir(os.path.join(TUTORIALS_DIR, entry)) or not os.path.exists(html_path):
                continue
            content = _read(html_path)
            title, date = _extract_title(content), _extract_date(content, entry)
            if not (title and date):
                continue
            articles.append({
                "title": title,
                "desc": _extract_desc(content),
                "date": date,
                "url": f"/tutorials/{entry}/",
                "tag": "教程",
                "slug": entry,
            })

    articles.sort(key=lambda x: x["date"], reverse=True)
    for a in articles:
        a["cover"] = find_cover(a["slug"])
        a["money"] = find_money(a["title"], a["desc"])
    return articles


def get_latest_articles(limit=6):
    """从所有分类目录（含 tutorials）获取最新文章，按发布日期排序"""
    return collect_articles()[:limit]


def count_articles():
    """统计各分类文章数量（修正：tutorials 在仓库根目录，不在 articles/ 下）"""
    counts = {"tutorials": 0, "cases": 0, "news": 0, "startup-100": 0}
    for cat in ("cases", "news", "startup-100"):
        cat_dir = os.path.join(ARTICLES_DIR, cat)
        if os.path.isdir(cat_dir):
            for entry in os.listdir(cat_dir):
                if os.path.isdir(os.path.join(cat_dir, entry)) and \
                   os.path.exists(os.path.join(cat_dir, entry, "index.html")):
                    counts[cat] += 1
    if os.path.isdir(TUTORIALS_DIR):
        for entry in os.listdir(TUTORIALS_DIR):
            if os.path.isdir(os.path.join(TUTORIALS_DIR, entry)) and \
               os.path.exists(os.path.join(TUTORIALS_DIR, entry, "index.html")):
                counts["tutorials"] += 1
    total = sum(counts.values())
    return total, counts


# 分类色（与 index.html 卡片数据条一致）
TAG_COLORS = {'热点': '#f0883e', '案例': '#3fb950', '教程': '#58a6ff', '实验': '#a371f7'}


def render_card(article):
    """单张卡片：数据条（分类徽章 + 收入徽章 + 日期）+ 标题 + 摘要。

    样式依赖 index.html <style> 里的 .card-strip / .card-money 规则，
    那些规则不在本脚本的替换范围内，所以重跑不会丢样式。
    """
    color = TAG_COLORS.get(article['tag'], '#58a6ff')
    money = f'<span class="card-money">¥{article["money"]}</span>' if article.get("money") else ""
    return f'''            <a href="{article['url']}" class="article-card">
                <div class="card-strip"><span class="strip-cat" style="color:{color};border:1px solid {color}55;background:{color}18;">{article['tag']}</span>{money}<span class="strip-date">{article['date']}</span></div>
                <h3>{article['title']}</h3>
                <p>{article['desc']}</p>
            </a>
'''


def update_homepage():
    """更新首页的'最新文章'区域"""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 更新最新文章区域
    candidates = collect_articles()
    articles = candidates[:6]
    today = datetime.now().strftime("%Y-%m-%d")

    cards_html = "".join(render_card(a) for a in articles[:6])

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

    with_money = sum(1 for a in articles[:6] if a.get("money"))
    print(f"✅ 首页已更新：{today}")
    print(f"   - 候选文章：{len(candidates)}篇 (news/seo/cases/startup + tutorials)")
    print(f"   - 展示 6 篇：带收入徽章 {with_money}/6")
    print(f"   - 文章总数：{total}篇 {counts}")
    for a in articles[:6]:
        print(f"     • [{a['tag']}] {a['title'][:40]:42} 徽章={a.get('money') or '—'}")
    return True


if __name__ == "__main__":
    success = update_homepage()
    if success:
        # git commit and push
        os.system(f'cd {REPO_DIR} && git add index.html && git commit -m "feat: 每日首页更新 - {datetime.now().strftime("%m-%d")}" && git push')
        print("✅ 已提交并推送")
    else:
        print("❌ 更新失败")
