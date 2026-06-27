#!/usr/bin/env python3
"""批量给文章添加统一页脚（信任页链接 + 版权声明）"""
import os, glob, re

SITE_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"
FOOTER_HTML = """    <div class="footer" style="text-align:center;margin-top:48px;padding-top:24px;border-top:1px solid var(--border);color:var(--muted);font-size:13px;">
        <p>
            <a href="/about/" style="color:var(--muted);text-decoration:underline;">关于我们</a> ·
            <a href="/disclaimer/" style="color:var(--muted);text-decoration:underline;">免责声明</a> ·
            <a href="/privacy/" style="color:var(--muted);text-decoration:underline;">隐私政策</a> ·
            <a href="/prompt-pack/" style="color:var(--muted);text-decoration:underline;">提示词包</a>
        </p>
        <p style="margin-top:6px;">© 2026 AiToollab · 内容仅供参考，不构成投资建议</p>
    </div>
"""

def process_article(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if 'class="footer"' in content:
        return False  # already has footer
    
    # Insert before </body>
    new_content = content.replace("</body>", FOOTER_HTML + "</body>", 1)
    if new_content == content:
        return False
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True

def main():
    dirs = ["articles/cases", "articles/news", "articles/seo", "articles/startup-100", "tutorials"]
    total = 0
    updated = 0
    for d in dirs:
        for f in glob.glob(os.path.join(SITE_DIR, d, "*/index.html")):
            total += 1
            if process_article(f):
                updated += 1
                rel = os.path.relpath(f, SITE_DIR)
                print(f"  ✅ {rel}")
    print(f"\n总文章: {total}, 更新页脚: {updated}")

if __name__ == "__main__":
    main()
