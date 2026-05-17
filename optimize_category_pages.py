#!/usr/bin/env python3
import os
import json
import re

# 分类配置
CATEGORY_CONFIG = {
    "seo": {
        "name": "💡 教程攻略",
        "title": "AI副业实战教程｜AiToollab",
        "desc": "从0到1的AI副业实战教程，覆盖工具使用、操作步骤、变现路径，普通人照着做就能赚到第一笔AI副业收入",
        "en_title": "AI Side Hustle Tutorials | AiToollab",
        "en_desc": "Practical AI side hustle tutorials for beginners, including tool guides, step-by-step instructions, and monetization paths to help you make your first AI income",
        "intro": '''
<div class="category-intro" style="background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 32px;">
    <h2 style="margin-bottom: 16px; font-size: 20px;">📚 本分类包含什么内容？</h2>
    <p style="margin-bottom: 12px; color: var(--text);">这里是所有AI副业实战教程的合集，覆盖AI工具使用、变现路径实操、副业避坑指南，所有内容都经过实测验证，普通人照着做就能落地。</p>
    <ul style="margin: 16px 0 0 20px; color: var(--muted);">
        <li style="margin-bottom: 8px;">✅ 所有教程都是亲自实测验证，真实可落地</li>
        <li style="margin-bottom: 8px;">✅ 包含具体工具、操作步骤、收益数据，没有空话</li>
        <li style="margin-bottom: 8px;">✅ 每周更新2篇最新的AI副业玩法教程</li>
    </ul>
</div>
        ''',
        "faq": '''
<div class="category-faq" style="margin-top: 40px; padding: 24px; background: var(--card); border: 1px solid var(--border); border-radius: 12px;">
    <h2 style="margin-bottom: 20px; font-size: 20px;">❓ 常见问题</h2>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：没有技术基础能做AI副业吗？</h3>
        <p style="color: var(--muted);">A：完全可以，90%的AI副业都不需要编程基础，只要会用电脑、会打字就能做，本分类的教程都是面向零基础用户的。</p>
    </div>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：做AI副业需要投入多少钱？</h3>
        <p style="color: var(--muted);">A：大部分AI副业的启动成本都在100元以内，主要是购买AI工具会员，不需要其他投入，属于低风险轻资产创业。</p>
    </div>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：多久能赚到第一笔收入？</h3>
        <p style="color: var(--muted);">A：按照教程实操，通常2-4周就能见到第一笔收入，收入多少取决于投入的时间和执行力，大部分人第一个月能赚到3000-5000元。</p>
    </div>
</div>
        '''
    },
    "news": {
        "name": "🔥 热点资讯",
        "title": "AI行业热点资讯｜AiToollab",
        "desc": "最新AI行业动态、热点事件解读、新工具发布消息，第一时间掌握AI行业赚钱机会",
        "en_title": "AI Industry News | AiToollab",
        "en_desc": "Latest AI industry trends, hot event analysis, new tool release news, help you seize AI industry money-making opportunities first",
        "intro": '''
<div class="category-intro" style="background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 32px;">
    <h2 style="margin-bottom: 16px; font-size: 20px;">📰 本分类包含什么内容？</h2>
    <p style="margin-bottom: 12px; color: var(--text);">这里是最新AI行业动态的合集，包括热点事件解读、新工具发布、行业政策变化，帮你第一时间掌握AI行业的赚钱机会。</p>
    <ul style="margin: 16px 0 0 20px; color: var(--muted);">
        <li style="margin-bottom: 8px;">✅ 每天更新最新的AI行业热点和新工具发布消息</li>
        <li style="margin-bottom: 8px;">✅ 深度解读热点事件背后的赚钱机会和行业趋势</li>
        <li style="margin-bottom: 8px;">✅ 所有内容都是原创分析，不是复制粘贴的新闻通稿</li>
    </ul>
</div>
        ''',
        "faq": '''
<div class="category-faq" style="margin-top: 40px; padding: 24px; background: var(--card); border: 1px solid var(--border); border-radius: 12px;">
    <h2 style="margin-bottom: 20px; font-size: 20px;">❓ 常见问题</h2>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：为什么要关注AI行业动态？</h3>
        <p style="color: var(--muted);">A：AI行业变化非常快，新的工具、新的玩法、新的赚钱机会每天都在出现，提前掌握信息才能抓住红利期，比别人更早赚到钱。</p>
    </div>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：这些资讯对普通人做副业有什么用？</h3>
        <p style="color: var(--muted);">A：每一次新工具发布、每一个热点事件背后都藏着赚钱机会，比如新AI工具发布可以做教程、做代运营、做定制服务，热点可以做内容引流。</p>
    </div>
</div>
        '''
    },
    "cases": {
        "name": "💰 赚钱案例",
        "title": "AI副业真实案例｜AiToollab",
        "desc": "真实的AI副业赚钱案例拆解，包括项目玩法、投入成本、收益数据、可复制的操作方法",
        "en_title": "AI Side Hustle Case Studies | AiToollab",
        "en_desc": "Real AI side hustle money-making case studies, including project gameplay, input cost, revenue data, and reproducible operation methods",
        "intro": '''
<div class="category-intro" style="background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 32px;">
    <h2 style="margin-bottom: 16px; font-size: 20px;">💼 本分类包含什么内容？</h2>
    <p style="margin-bottom: 12px; color: var(--text);">这里是AI副业真实赚钱案例的合集，所有案例都是真实存在的，包含项目玩法、投入成本、收益数据、可复制的操作方法，你可以直接照搬落地。</p>
    <ul style="margin: 16px 0 0 20px; color: var(--muted);">
        <li style="margin-bottom: 8px;">✅ 所有案例都是真实存在的，有具体数据支撑，不是虚构的</li>
        <li style="margin-bottom: 8px;">✅ 包含可复制的操作步骤，你可以直接照搬落地赚钱</li>
        <li style="margin-bottom: 8px;">✅ 每周更新最新的AI赚钱案例，带你发现新的机会</li>
    </ul>
</div>
        ''',
        "faq": '''
<div class="category-faq" style="margin-top: 40px; padding: 24px; background: var(--card); border: 1px solid var(--border); border-radius: 12px;">
    <h2 style="margin-bottom: 20px; font-size: 20px;">❓ 常见问题</h2>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：这些案例普通人能复制吗？</h3>
        <p style="color: var(--muted);">A：大部分案例都可以复制，我们在拆解的时候会重点说明普通人可以照搬的操作步骤，以及需要避开的坑，不需要你自己摸索。</p>
    </div>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：我没有资源能做这些项目吗？</h3>
        <p style="color: var(--muted);">A：我们拆解的案例都是普通人可以做的，不需要资源、不需要人脉、不需要资金投入，只要有时间和执行力就可以做。</p>
    </div>
</div>
        '''
    },
    "startup-100": {
        "name": "🧪 实验测评",
        "title": "AI工具真实测评｜AiToollab",
        "desc": "最新AI工具的真实测评，包括功能体验、价格对比、优缺点分析，帮你找到适合自己的AI工具，不花冤枉钱",
        "en_title": "AI Tool Reviews | AiToollab",
        "en_desc": "Real reviews of the latest AI tools, including function experience, price comparison, advantages and disadvantages analysis, help you find suitable AI tools and avoid wasting money",
        "intro": '''
<div class="category-intro" style="background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 32px;">
    <h2 style="margin-bottom: 16px; font-size: 20px;">🔬 本分类包含什么内容？</h2>
    <p style="margin-bottom: 12px; color: var(--text);">这里是最新AI工具的真实测评合集，所有工具我们都亲自付费使用过，包括功能体验、价格对比、优缺点分析，帮你找到适合自己的AI工具，不花冤枉钱。</p>
    <ul style="margin: 16px 0 0 20px; color: var(--muted);">
        <li style="margin-bottom: 8px;">✅ 所有工具都亲自付费实测，真实体验没有广告</li>
        <li style="margin-bottom: 8px;">✅ 包含价格对比、优缺点分析，帮你做购买决策</li>
        <li style="margin-bottom: 8px;">✅ 每周更新最新的AI工具测评，帮你掌握新工具</li>
    </ul>
</div>
        ''',
        "faq": '''
<div class="category-faq" style="margin-top: 40px; padding: 24px; background: var(--card); border: 1px solid var(--border); border-radius: 12px;">
    <h2 style="margin-bottom: 20px; font-size: 20px;">❓ 常见问题</h2>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：测评的工具都是免费的吗？</h3>
        <p style="color: var(--muted);">A：有免费的也有付费的，我们会明确标注价格和是否有免费版，以及性价比分析，帮你判断值不值得买。</p>
    </div>
    <div style="margin-bottom: 16px;">
        <h3 style="margin-bottom: 8px; font-size: 16px;">Q：有没有适合普通人的AI工具推荐？</h3>
        <p style="color: var(--muted);">A：我们会优先测评普通人能用、可以用来赚钱的AI工具，重点关注性价比和实用性，不会推荐华而不实的工具。</p>
    </div>
</div>
        '''
    }
}

# 提取页面里的文章列表，生成Schema的itemListElement
def extract_articles_from_page(content):
    items = []
    # 匹配所有文章卡片里的链接和标题
    matches = re.findall(r'<a href="([^"]+)">([^<]+)</a>', content)
    for url, title in matches:
        if url.startswith('/') and (url.endswith('/') or '.html' in url) and not '#' in url:
            full_url = f"https://www.aitoollab.top{url}" if url.startswith('/') else url
            items.append({
                "@type": "ListItem",
                "position": len(items) + 1,
                "url": full_url,
                "name": title.strip()
            })
    return items

# 处理单个分类页
def process_category_page(category_key):
    config = CATEGORY_CONFIG[category_key]
    page_path = f"./articles/{category_key}/index.html"
    if not os.path.exists(page_path):
        print(f"❌ 页面不存在: {page_path}")
        return False
    
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 更新英文meta标签
    old_en_meta = re.search(r'<meta property="og:title:en" .*?<meta name="description:en" .*?>', content, re.DOTALL)
    if old_en_meta:
        new_en_meta = f'''
<meta property="og:title:en" content="{config['en_title']}" />
<meta property="og:description:en" content="{config['en_desc']}" />
<meta name="description:en" content="{config['en_desc']}" />
        '''
        content = content.replace(old_en_meta.group(0), new_en_meta)
    
    # 2. 添加分类介绍模块（在nav之后，container的开头）
    if 'category-intro' not in content:
        content = re.sub(r'(<div class="container">)', f'\\1{config["intro"]}', content)
    
    # 3. 添加FAQ模块（在article-grid之后，back-link之前）
    if 'category-faq' not in content:
        content = re.sub(r'(<div class="back-link">)', f'{config["faq"]}\\1', content)
    
    # 4. 完善Schema的itemListElement
    articles = extract_articles_from_page(content)
    if articles:
        # 找到Schema的JSON部分
        schema_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
        if schema_match:
            schema_str = schema_match.group(1).strip()
            try:
                schema = json.loads(schema_str)
                if 'mainEntity' in schema and 'itemListElement' in schema['mainEntity']:
                    schema['mainEntity']['itemListElement'] = articles
                    # 更新Schema
                    new_schema_str = json.dumps(schema, ensure_ascii=False, indent=4)
                    new_schema = f'<script type="application/ld+json">\n{new_schema_str}\n</script>'
                    content = content.replace(schema_match.group(0), new_schema)
            except:
                print(f"⚠️  Schema解析失败: {page_path}")
    
    # 保存修改
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已优化分类页: {category_key}")
    return True

def main():
    print("=== 开始优化分类页 ===")
    categories = ["seo", "news", "cases", "startup-100"]
    success_count = 0
    for cat in categories:
        if process_category_page(cat):
            success_count +=1
    
    print(f"=== 优化完成，成功处理 {success_count}/4 个分类页 ===")
    print("接下来执行：")
    print("git add . && git commit -m '优化分类页：添加介绍/FAQ模块，完善Schema结构化数据'")
    print("git push 同步到线上")

if __name__ == "__main__":
    main()
