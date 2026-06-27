#!/usr/bin/env python3
"""补漏：为无article标签的文章添加作者框"""
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
        
        # Insert after <body> if no <article> tag
        if '<article' not in content:
            content = content.replace('<body>', '<body>\n' + AUTHOR_BOX, 1)
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(content)
            count += 1
            print(f"  ✅ {os.path.relpath(f, SITE_DIR)}")

print(f"\n补漏注入: {count} 篇")
