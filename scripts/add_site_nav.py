#!/usr/bin/env python3
"""
全站文章页顶部导航批量注入
- 给所有文章页（articles/*/、tutorials/*/）在 <body> 后注入统一顶部导航
- 包含：logo（返回首页）、首页、教程、案例、项目库
- 幂等：已有 nav 则跳过
"""
import os
import re
import glob

BASE = "/home/agentuser/.hermes/hermes-agent/aitoollab"

from nav_template import NAV_HTML


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 先删除文章自带 header nav（toc/breadcrumb/section-nav 保留），防止双导航
    def strip_dup(m):
        tag = m.group(0)
        if any(k in tag[:120] for k in ('toc', 'breadcrumb', 'section-nav', 'site-topnav')):
            return tag
        return ''
    content = re.sub(r'\s*<nav(?![^>]*site-topnav)[^>]*>.*?</nav>', strip_dup, content, flags=re.S)

    if 'site-topnav' in content:
        updated = re.sub(r'<nav class="site-topnav".*?</nav>', NAV_HTML, content, count=1, flags=re.DOTALL)
        if updated != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)
            return True
        return False  # 已有最新导航

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
