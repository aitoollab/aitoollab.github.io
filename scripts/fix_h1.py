#!/usr/bin/env python3
"""为缺失H1标签的文章补上H1（从title提取）"""
import os, glob, re

SITE_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"

def fix_h1(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if '<h1>' in content:
        return False
    
    # Extract title
    title_m = re.search(r'<title>(.*?)</title>', content)
    if not title_m:
        return False
    
    title = title_m.group(1).strip()
    # Clean title: remove site suffix if present
    title = re.sub(r'\s*[-–—|]\s*AiToollab.*$', '', title)
    
    # Find the first <h2> and insert <h1> before it
    # Or find the article content area
    h1_tag = f'<h1>{title}</h1>\n\n    '
    
    # Insert after first <p class="date"> or after article opening
    patterns = [
        (r'(<article[^>]*>\s*)', r'\1' + h1_tag),
    ]
    
    for pattern, replacement in patterns:
        m = re.search(pattern, content)
        if m:
            content = re.sub(pattern, replacement, content, count=1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    
    # Fallback: insert after <main> or <div class="container"> or <body>
    for tag in ['<main>', '<main class="container">', '<div class="article-container">']:
        if tag in content:
            content = content.replace(tag, tag + '\n    ' + h1_tag, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    
    return False

def main():
    dirs = ["articles/cases", "articles/news", "articles/seo", "articles/startup-100", "tutorials"]
    count = 0
    for d in dirs:
        for f in glob.glob(os.path.join(SITE_DIR, d, "*/index.html")):
            if fix_h1(f):
                count += 1
                print(f"  ✅ {os.path.relpath(f, SITE_DIR)}")
    print(f"\n修复H1: {count} 篇")

if __name__ == "__main__":
    main()
