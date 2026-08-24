#!/usr/bin/env python3
"""
全站文章页顶部导航批量注入
- 给所有文章页（articles/*/、tutorials/*/）在 <body> 后注入统一顶部导航
- 包含：logo（返回首页）、首页、教程、案例、提示词包
- 幂等：已有 nav 则跳过
"""
import os
import re
import glob

BASE = "/home/agentuser/.hermes/hermes-agent/aitoollab"

NAV_HTML = """<nav class="site-topnav" style="position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:16px;padding:10px 24px;background:rgba(13,17,23,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--border,#30363d);font-size:14px;">
    <a href="/" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:var(--text,#e6edf3);font-weight:700;font-size:16px;">
        <span style="font-size:20px;">🧰</span><span>AiToollab</span>
    </a>
    <a href="/" style="color:var(--muted,#8b949e);text-decoration:none;">首页</a>
    <a href="/tutorials/" style="color:var(--muted,#8b949e);text-decoration:none;">教程</a>
    <a href="/articles/cases/" style="color:var(--muted,#8b949e);text-decoration:none;">案例</a>
    <a href="/prompt-pack/?src=anav" style="color:var(--muted,#8b949e);text-decoration:none;">AI副业工具箱</a>
    <a href="/prompt-pack/" style="margin-left:auto;padding:4px 14px;border-radius:6px;background:linear-gradient(135deg,#58a6ff,#3fb950);color:#fff;text-decoration:none;font-weight:600;">¥39 立即获取</a>
</nav>"""


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if 'site-topnav' in content:
        return False  # 已有导航

    # 在 <body> 后插入导航
    if '<body>' in content:
        content = content.replace('<body>', '<body>\n' + NAV_HTML, 1)
    elif '<body ' in content:
        content = re.sub(r'(<body[^>]*>)', r'\1\n' + NAV_HTML, content, count=1)
    else:
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    files = []
    for pattern in ['articles/cases/*/index.html', 'articles/news/*/index.html',
                    'articles/seo/*/index.html', 'articles/startup-100/*/index.html',
                    'tutorials/*/index.html']:
        files.extend(glob.glob(os.path.join(BASE, pattern)))

    # 排除已处理的
    done = 0
    skipped = 0
    for f in sorted(files):
        if process_file(f):
            done += 1
        else:
            skipped += 1
    print(f"注入导航: {done} 页, 跳过(已有/非文章): {skipped} 页, 总扫描: {len(files)}")


if __name__ == "__main__":
    main()
