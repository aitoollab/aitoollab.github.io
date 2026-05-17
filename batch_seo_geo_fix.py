#!/usr/bin/env python3
import os
import re
import json
from collections import defaultdict

# 配置
ARTICLES_DIR = "./articles"
CATEGORY_MAPPING = {
    "cases": "赚钱案例",
    "news": "AI新闻",
    "seo": "副业教程",
    "startup-100": "AI工具测评"
}
ENGLISH_META_TEMPLATE = '''
<meta property="og:title:en" content="{en_title}" />
<meta property="og:description:en" content="{en_desc}" />
<meta name="description:en" content="{en_desc}" />
'''
RELATED_ARTICLES_TEMPLATE = '''
<div class="related-articles" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border);">
    <h3 style="color: var(--text); margin-bottom: 16px;">相关推荐</h3>
    <ul style="list-style: none; padding: 0; margin: 0;">
        {related_links}
    </ul>
</div>
'''
LINK_TEMPLATE = '<li style="margin-bottom: 8px;"><a href="/{path}" style="color: var(--accent); text-decoration: none;">{title}</a></li>'

# 加载所有文章的元数据
def load_articles_metadata():
    articles = []
    for root, _, files in os.walk(ARTICLES_DIR):
        for file in files:
            if file == "index.html" and root != ARTICLES_DIR:
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 提取title和description
                title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
                desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
                if title_match and desc_match:
                    title = title_match.group(1).strip()
                    desc = desc_match.group(1).strip()
                    category = root.split('/')[1]
                    articles.append({
                        "path": root.lstrip('./'),
                        "title": title,
                        "desc": desc,
                        "category": category
                    })
    # 按分类分组
    category_articles = defaultdict(list)
    for art in articles:
        category_articles[art['category']].append(art)
    return articles, category_articles

# 生成英文标题和描述（简单翻译适配，后续可优化为AI翻译）
def generate_en_meta(title, desc):
    # 简单关键词替换，后续可以接入翻译API
    en_title = title.replace("AI", "AI").replace("副业", "Side Hustle").replace("教程", "Tutorial").replace("案例", "Case Study").replace("工具", "Tool").replace("测评", "Review")
    en_desc = desc.replace("AI", "AI").replace("赚钱", "Make Money").replace("被动收入", "Passive Income").replace("提示词", "Prompt")
    # 截断到合适长度
    if len(en_title) > 60:
        en_title = en_title[:57] + "..."
    if len(en_desc) > 160:
        en_desc = en_desc[:157] + "..."
    return en_title, en_desc

# 给单个页面添加英文meta和相关推荐
def process_page(page_path, article_data, category_articles):
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 添加英文meta标签（在现有meta标签之后，style标签之前）
    en_title, en_desc = generate_en_meta(article_data['title'], article_data['desc'])
    en_meta = ENGLISH_META_TEMPLATE.format(en_title=en_title, en_desc=en_desc)
    # 查找插入位置：在</head>之前，且不在已有英文meta
    if 'og:title:en' not in content:
        content = re.sub(r'(</head>)', f'{en_meta}\\1', content)
    
    # 2. 添加相关文章推荐（在正文结束，cta之前，如果没有cta就在footer之前）
    if 'related-articles' not in content:
        # 找同分类的其他文章，最多3篇
        same_category = [a for a in category_articles[article_data['category']] if a['path'] != article_data['path']][:3]
        if not same_category:
            # 如果同分类没有，找全站点其他文章
            same_category = [a for a in category_articles['seo'] + category_articles['cases'] if a['path'] != article_data['path']][:3]
        related_links = '\n'.join([LINK_TEMPLATE.format(path=a['path'], title=a['title']) for a in same_category])
        related_html = RELATED_ARTICLES_TEMPLATE.format(related_links=related_links)
        # 插入到</article>之前或者footer之前
        if '</article>' in content:
            content = re.sub(r'(</article>)', f'{related_html}\\1', content)
        else:
            content = re.sub(r'(<footer)', f'{related_html}\\1', content)
    
    # 3. 保存修改
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已处理: {page_path}")

def main():
    print("=== 开始批量SEO/GEO优化 ===")
    articles, category_articles = load_articles_metadata()
    print(f"总计加载 {len(articles)} 篇文章元数据")
    
    for art in articles:
        page_path = os.path.join(art['path'], 'index.html')
        if os.path.exists(page_path):
            process_page(page_path, art, category_articles)
    
    print("=== 优化完成 ===")
    print("接下来需要执行：")
    print("1. git add . && git commit -m '批量优化：添加英文meta标签和相关文章内链'")
    print("2. git push 同步到线上")

if __name__ == "__main__":
    main()
