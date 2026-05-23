#!/usr/bin/env python3
"""
AiToollab 全站批量 GEO+SEO 优化脚本

功能：
1. 去除HTML行号（cron生成bug修复）
2. 修复损坏的JSON-LD（中文引号断JSON、missing comma等）
3. 增强JSON-LD字段（image, mainEntityOfPage）
4. 添加英文GEO meta标签（og:title:en, og:description:en）
5. 添加FAQPage Schema（从文章h2/h3自动提取）
6. 添加相关文章推荐模块

用法：
  cd /path/to/aitoollab
  python3 scripts/batch_seo_geo_fix.py [--dry-run] [--verbose]
"""

import os, re, json, sys, glob
from datetime import datetime

SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIRS = [
    "articles/cases",
    "articles/news",
    "articles/seo",
    "articles/startup-100",
    "tutorials",
]

DRY_RUN = "--dry-run" in sys.argv
VERBOSE = "--verbose" in sys.argv


# ── Helpers ──────────────────────────────────────────────────────────

def log(msg, level="info"):
    if level == "verbose" and not VERBOSE:
        return
    prefix = {"info": "  ", "ok": "  ✅", "warn": "  ⚠️", "skip": "  -"}.get(level, "  ")
    print(f"{prefix} {msg}")


def get_all_articles():
    """扫描所有文章目录，返回index.html路径列表"""
    articles = []
    for section in ARTICLES_DIRS:
        section_dir = os.path.join(SITE_DIR, section)
        if not os.path.isdir(section_dir):
            continue
        for item in sorted(os.listdir(section_dir)):
            idx = os.path.join(section_dir, item, "index.html")
            if os.path.isfile(idx):
                articles.append(idx)
    return articles


# ── Fix 1: Strip line numbers ────────────────────────────────────────
# 问题：cron生成文章时带了 "    41|    {" 这种行号前缀
# √ 已修复 2026-05-23：cron prompt加了强制指令，但已生成的文章需要批量修复

def strip_line_numbers(content):
    """去掉每行开头的行号（数字+竖线）"""
    lines = content.split("\n")
    fixed = []
    changed = False
    for line in lines:
        m = re.match(r"^( *)\d+\|(.*)", line)
        if m:
            fixed.append(m.group(1) + m.group(2))
            changed = True
        else:
            fixed.append(line)
    return "\n".join(fixed), changed


# ── Fix 2: Fix broken JSON-LD ────────────────────────────────────────
# 问题1：中文引号 "xxx" 在JSON字符串里用的是ASCII双引号(U+0022)，
#        导致JSON解析到一半就断掉
# 问题2：JSON值里包含未转义的换行
# 问题3：逗号遗漏
# √ 已修复：扫描全文JSON-LD块，用json.loads验证，失败的采用逐步修复策略

def fix_broken_json_ld(content):
    """修复所有损坏的JSON-LD块"""
    def fix_one(match):
        raw = match.group(1)
        try:
            json.loads(raw)
            return match.group(0)  # Already valid
        except json.JSONDecodeError:
            pass

        fixed = _repair_json(raw)
        try:
            json.loads(fixed)
            result = f'<script type="application/ld+json">\n{fixed}\n    </script>'
            return result
        except json.JSONDecodeError as e:
            log(f"JSON-LD still broken: {e}", "warn")
            return match.group(0)

    return re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        fix_one,
        content,
        flags=re.DOTALL,
    )


def _repair_json(raw):
    """尝试多种策略修复损坏的JSON"""
    # Strategy 1: 中文引号修复
    # 匹配 "中文" 或 "英文word" 出现在JSON值内部的情况
    # 只在: "value" 内部替换，不动key的引号
    strategy_count = 0
    
    for strategy in [_fix_cjk_quotes, _fix_missing_commas, _fix_trailing_comma]:
        try:
            json.loads(raw)
            return raw
        except json.JSONDecodeError:
            fixed = strategy(raw)
            if fixed != raw:
                strategy_count += 1
                raw = fixed
    
    return raw


def _fix_cjk_quotes(s):
    """修复JSON值中未转义的中文引号
    模式：CJK文字"内容"CJK文字 → CJK文字'内容'CJK文字
    """
    # 只能在JSON value内部替换
    result = []
    i = 0
    in_key = False
    in_value = False
    depth = 0
    
    while i < len(s):
        ch = s[i]
        
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        elif ch == '"' and (i == 0 or s[i-1] != '\\'):
            # Check if this is a key or value opening/closing
            # Simple heuristic: after : it's a value start
            pass
        
        result.append(ch)
        i += 1
    
    # Simpler approach: just fix common patterns
    # 提出"xxx"概念 → 提出'xxx'概念  (in value strings)
    s = re.sub(r'([\u4e00-\u9fff])"([\u4e00-\u9fff\w\s，。、：；！？（）]+)"', r"\1\u2018\2\u2019", s)
    s = re.sub(r'"([\u4e00-\u9fff\w\s，。、：；！？（）]+)"([\u4e00-\u9fff])', r"\u2018\1\u2019\2", s)
    
    return s


def _fix_missing_commas(s):
    """修复JSON中遗漏的逗号
    模式：}" 后没有逗号直接跟 " 的情况
    """
    # Fix: }"   ->   },"
    s = re.sub(r'}"\s*"', '}",\n      "', s)
    # Fix: ]"   ->   ],"
    s = re.sub(r']"\s*"', ']",\n      "', s)
    return s


def _fix_trailing_comma(s):
    """去掉JSON对象/数组中最后一个元素后的多余逗号"""
    s = re.sub(r',\s*}', '\n}', s)
    s = re.sub(r',\s*]', '\n]', s)
    return s


# ── Fix 3: Enhance JSON-LD ──────────────────────────────────────────
# 添加 image, mainEntityOfPage 等字段提升GEO表现

def enhance_json_ld(content):
    """增强JSON-LD字段"""
    def enhance(match):
        raw = match.group(1)
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        
        obj_type = obj.get("@type")
        if obj_type not in ("Article", "NewsArticle", "BlogPosting"):
            return match.group(0)
        
        changed = False
        
        # Add image from OG tag if missing
        if not obj.get("image"):
            img = re.search(r'<meta property="og:image" content="([^"]+)"', content)
            if img:
                obj["image"] = img.group(1)
                changed = True
        
        # Add mainEntityOfPage
        if not obj.get("mainEntityOfPage"):
            can = re.search(r'<link rel="canonical" href="([^"]+)"', content)
            if can:
                obj["mainEntityOfPage"] = {
                    "@type": "WebPage",
                    "@id": can.group(1),
                }
                changed = True
        
        if changed:
            return f'<script type="application/ld+json">\n{json.dumps(obj, ensure_ascii=False, indent=4)}\n    </script>'
        return match.group(0)
    
    return re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        enhance,
        content,
        flags=re.DOTALL,
    )


# ── Fix 4: Add English GEO meta tags ─────────────────────────────────
# 为AI搜索引擎添加英文meta标签，提升双语GEO表现

def add_english_geo_tags(content):
    """添加英文GEO meta标签（如果还没有）"""
    if "og:description:en" in content:
        return content, False
    
    title_m = re.search(r"<title>(.*?)</title>", content)
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', content)
    if not title_m or not desc_m:
        return content, False
    
    en_geo = (
        '\n    <!-- GEO: Bilingual meta for AI search engines (English) -->\n'
        f'    <meta name="description:en" content="{desc_m.group(1)}" />\n'
        f'    <meta property="og:description:en" content="{desc_m.group(1)}" />\n'
        f'    <meta property="og:title:en" content="{title_m.group(1)}" />\n'
    )
    content = content.replace("</head>", en_geo + "    </head>", 1)
    return content, True


# ── Fix 5: Add FAQPage Schema ────────────────────────────────────────
# 从文章h2/h3自动提取FAQ，AI搜索引擎喜欢从FAQ抓取答案

def add_faq_schema(content):
    """添加FAQPage Schema（如果还没有且文章有合适的h2/h3）"""
    if "FAQPage" in content:
        return content, False
    
    # 收集h2/h3标题
    headings = re.findall(r"<h[23][^>]*>(.*?)</h[23]>", content)
    
    # 筛选有问答特征的标题
    faq_headings = [
        h for h in headings
        if len(h) > 6 and (
            "?" in h or "？" in h or
            "如何" in h or "怎么" in h or "怎样" in h or
            "多少" in h or "什么" in h or "哪些" in h or
            "是不是" in h or "能不能" in h or "要不要" in h or
            "步骤" in h or "方法" in h or "操作" in h or "技巧" in h
        )
    ]
    
    if len(faq_headings) < 2:
        return content, False
    
    # 提取每个标题后的第一个段落作为答案
    faq_items = []
    for h in faq_headings[:6]:  # 最多6个
        escaped = re.escape(h)
        m = re.search(
            escaped + r"</h[23]>.*?<p>(.*?)</p>",
            content, re.DOTALL
        )
        answer = m.group(1)[:200] if m else f"详见本文关于「{h}」的详细讲解。"
        # 去掉答案里的HTML标签
        answer = re.sub(r"<[^>]+>", "", answer)
        faq_items.append({"question": h, "answer": answer})
    
    if not faq_items:
        return content, False
    
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
            for item in faq_items
        ],
    }
    
    faq_html = (
        '\n    <script type="application/ld+json">\n'
        f'{json.dumps(faq_schema, ensure_ascii=False, indent=4)}\n'
        '    </script>\n'
    )
    
    content = content.replace("</head>", faq_html + "    </head>", 1)
    return content, True


# ── Fix 6: Add related article recommendations ───────────────────────

def add_related_articles(content, current_slug, section):
    """在文章底部添加相关推荐模块"""
    if 'related-articles' in content or '相关推荐' in content:
        return content, False
    
    # 找同分类下其他文章
    section_dir = os.path.join(SITE_DIR, section)
    if not os.path.isdir(section_dir):
        return content, False
    
    related = []
    for item in os.listdir(section_dir):
        if item == current_slug:
            continue
        idx_path = os.path.join(section_dir, item, "index.html")
        if not os.path.isfile(idx_path):
            continue
        # 读文章标题
        with open(idx_path) as f:
            idx_content = f.read(2000)
        title_m = re.search(r"<title>(.*?)</title>", idx_content)
        if title_m:
            related.append((item, title_m.group(1)))
    
    if len(related) < 2:
        # 从其他分类凑
        for other in ARTICLES_DIRS:
            if other == section:
                continue
            other_dir = os.path.join(SITE_DIR, other)
            if not os.path.isdir(other_dir):
                continue
            for item in os.listdir(other_dir):
                if len(related) >= 3:
                    break
                if item == current_slug:
                    continue
                idx_path = os.path.join(other_dir, item, "index.html")
                if not os.path.isfile(idx_path):
                    continue
                with open(idx_path) as f:
                    idx_content = f.read(2000)
                title_m = re.search(r"<title>(.*?)</title>", idx_content)
                if title_m:
                    related.append((item, title_m.group(1)))
            if len(related) >= 3:
                break
    
    if len(related) < 2:
        return content, False
    
    # 截取标题
    def short_title(t):
        return t[:40] + "..." if len(t) > 40 else t
    
    related_html = (
        '\n\n    <!-- related-articles -->\n'
        '    <div class="related-articles">\n'
        '        <h2>📖 相关推荐</h2>\n'
        '        <div class="related-grid">\n'
    )
    for slug, title in related[:4]:
        rel_path = f"/{section}/{slug}/" if not slug.startswith(section) else f"/{slug}/"
        related_html += (
            f'            <a href="{rel_path}" class="related-card">\n'
            f'                <span>{short_title(title)}</span>\n'
            f'            </a>\n'
        )
    related_html += (
        "        </div>\n"
        "    </div>\n"
    )
    
    # 在</article>前插入
    content = content.replace("</article>", related_html + "</article>", 1)
    return content, True


# ── Main ─────────────────────────────────────────────────────────────

def process_article(path):
    """处理单篇文章，返回修改统计"""
    stats = {"line_nums": 0, "json_ld": 0, "enhanced": 0, "geo": 0, "faq": 0, "related": 0}
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    
    # 1. Strip line numbers
    content, changed = strip_line_numbers(content)
    if changed:
        stats["line_nums"] = 1
    
    # 2. Fix broken JSON-LD
    content = fix_broken_json_ld(content)
    if content != original and stats["line_nums"] == 0:
        stats["json_ld"] = 1
    
    # 3. Enhance JSON-LD fields
    content = enhance_json_ld(content)
    if content != original:
        stats["enhanced"] = 1
    
    # 4. Add English GEO tags
    content, geo_added = add_english_geo_tags(content)
    if geo_added:
        stats["geo"] = 1
    
    # 5. Add FAQ schema
    content, faq_added = add_faq_schema(content)
    if faq_added:
        stats["faq"] = 1
    
    # 6. Add related articles
    rel = os.path.relpath(path, SITE_DIR)
    section = os.path.dirname(os.path.dirname(rel))
    slug = os.path.basename(os.path.dirname(rel))
    content, related_added = add_related_articles(content, slug, section)
    if related_added:
        stats["related"] = 1
    
    # Write if changed
    if content != original:
        if DRY_RUN:
            log(f"Would write: {rel}", "ok")
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            log(f"Updated: {rel}", "ok")
    else:
        log(f"Clean: {rel}", "skip")
    
    return stats


def main():
    print(f"🔧 AiToollab 全站 GEO+SEO 批量优化")
    print(f"   目录: {SITE_DIR}")
    print(f"   模式: {'🔍 DRY RUN (不会写文件)' if DRY_RUN else '✅ LIVE'}")
    print()
    
    articles = get_all_articles()
    print(f"📚 扫描到 {len(articles)} 篇文章\n")
    
    totals = {"line_nums": 0, "json_ld": 0, "enhanced": 0, "geo": 0, "faq": 0, "related": 0}
    
    for path in articles:
        rel = os.path.relpath(path, SITE_DIR)
        log(f"── {rel}", "info")
        stats = process_article(path)
        for k, v in stats.items():
            totals[k] += v
    
    print(f"\n=== 统计 ===")
    print(f"  行号修复:    {totals['line_nums']}")
    print(f"  JSON-LD修复: {totals['json_ld']}")
    print(f"  JSON-LD增强: {totals['enhanced']}")
    print(f"  GEO标签新增: {totals['geo']}")
    print(f"  FAQ Schema:  {totals['faq']}")
    print(f"  相关推荐:    {totals['related']}")
    print(f"  总处理文章:  {len(articles)}")
    
    if DRY_RUN:
        print("\n🔍 DRY RUN 完成。去掉 --dry-run 执行实际写入。")
    else:
        print("\n✅ 完成！建议执行 git diff 确认变更，然后commit push。")


if __name__ == "__main__":
    main()
