#!/usr/bin/env python3
"""为所有文章批量注入作者框（支持多种文章结构变体）"""
import os, glob, re

SITE_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"

AUTHOR_BOX = '''    <div class="author-box" style="display:flex;align-items:center;gap:12px;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 20px;margin-bottom:24px;font-size:14px;">
        <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#58a6ff,#3fb950);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;">🛠️</div>
        <div>
            <p style="font-weight:600;color:var(--text);margin:0;">AiToollab 实战导师</p>
            <p style="color:var(--muted);margin:4px 0 0;font-size:13px;">3年 AI 工具链实战经验 · 每一篇内容都来自真实操作</p>
        </div>
    </div>
'''

count = 0
for d in ["articles/cases", "articles/news", "articles/seo", "articles/startup-100", "tutorials"]:
    for f in glob.glob(os.path.join(SITE_DIR, d, "*/index.html")):
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()
        
        if 'author-box' in content:
            continue
        
        # Insert after the first <article> tag (handle various structures)
        # Find <article...> and insert after it (before the next block)
        m = re.search(r'(<article[^>]*>\s*\n)', content)
        if m:
            pos = m.end()
            content = content[:pos] + AUTHOR_BOX + '\n' + content[pos:]
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(content)
            count += 1
    
    print(f"  {d}: done")

print(f"\n注入作者框: {count} 篇")
