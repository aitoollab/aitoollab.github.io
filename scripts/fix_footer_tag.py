#!/usr/bin/env python3
"""统一替换所有<footer>或旧版页脚为新标准"""
import os, glob, re

SITE_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"
NEW_FOOTER = '''    <div class="footer" style="text-align:center;margin-top:48px;padding-top:24px;border-top:1px solid var(--border);color:var(--muted);font-size:13px;">
        <p>
            <a href="/about/" style="color:var(--muted);text-decoration:underline;">关于我们</a> ·
            <a href="/disclaimer/" style="color:var(--muted);text-decoration:underline;">免责声明</a> ·
            <a href="/privacy/" style="color:var(--muted);text-decoration:underline;">隐私政策</a> ·
            <a href="/prompt-pack/" style="color:var(--muted);text-decoration:underline;">提示词包</a>
        </p>
        <p style="margin-top:6px;">© 2026 AiToollab · 内容仅供参考，不构成投资建议</p>
    </div>'''

count = 0
for d in ["articles/cases", "articles/news", "articles/seo", "articles/startup-100", "tutorials"]:
    for f in glob.glob(os.path.join(SITE_DIR, d, "*/index.html")):
        with open(f, "r", encoding="utf-8") as fh:
            content = fh.read()
        
        if '/disclaimer/' in content:
            continue
        
        # Replace <footer...>...</footer> blocks
        content_new = re.sub(
            r'\s*<footer[^>]*>.*?</footer>\s*',
            '\n' + NEW_FOOTER + '\n',
            content,
            flags=re.DOTALL
        )
        
        if content_new != content:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(content_new)
            count += 1
            print(f"  ✅ {os.path.relpath(f, SITE_DIR)}")

print(f"\n更新: {count} 篇")
