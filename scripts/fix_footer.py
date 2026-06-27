#!/usr/bin/env python3
"""补全旧版页脚 - 替换成包含信任页链接的统一页脚"""
import os, glob

SITE_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"
NEW_FOOTER = '''    <div class="footer" style="text-align:center;margin-top:48px;padding-top:24px;border-top:1px solid var(--border);color:var(--muted);font-size:13px;">
        <p>
            <a href="/about/" style="color:var(--muted);text-decoration:underline;">关于我们</a> ·
            <a href="/disclaimer/" style="color:var(--muted);text-decoration:underline;">免责声明</a> ·
            <a href="/privacy/" style="color:var(--muted);text-decoration:underline;">隐私政策</a> ·
            <a href="/prompt-pack/" style="color:var(--muted);text-decoration:underline;">提示词包</a>
        </p>
        <p style="margin-top:6px;">© 2026 AiToollab · 内容仅供参考，不构成投资建议</p>
    </div>
'''

def update_footer(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Skip if already has new footer with disclaimer link
    if '/disclaimer/' in content:
        return False
    
    changed = False
    
    # Replace old minimal footer
    old_footer1 = '<div class="footer">\n        <p>&copy; 2026 AiToollab. All rights reserved.</p>\n    </div>'
    if old_footer1 in content:
        content = content.replace(old_footer1, NEW_FOOTER)
        changed = True
    
    # Add footer if none exists
    if not changed and 'class="footer"' not in content:
        content = content.replace("</body>", NEW_FOOTER + "</body>", 1)
        changed = True
    
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return changed

def main():
    dirs = ["articles/cases", "articles/news", "articles/seo", "articles/startup-100", "tutorials"]
    updated = 0
    for d in dirs:
        for f in glob.glob(os.path.join(SITE_DIR, d, "*/index.html")):
            if update_footer(f):
                updated += 1
                rel = os.path.relpath(f, SITE_DIR)
                print(f"  ✅ {rel}")
    print(f"\n更新: {updated} 篇")

if __name__ == "__main__":
    main()
