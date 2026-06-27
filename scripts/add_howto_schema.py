#!/usr/bin/env python3
"""为教程类文章添加 HowTo Schema 结构化数据"""
import os, glob, re, json
from datetime import datetime

SITE_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"
COUNT = {"howto": 0, "skipped": 0}

def add_howto_schema(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Skip if already has HowTo
    if '"HowTo"' in content or 'HowTo' in content:
        COUNT["skipped"] += 1
        return False
    
    # Extract title
    title_m = re.search(r'<title>(.*?)</title>', content)
    if not title_m:
        COUNT["skipped"] += 1
        return False
    title = title_m.group(1)
    
    # Extract description
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', content)
    description = desc_m.group(1) if desc_m else ""
    
    # Check if this looks like a tutorial (has "how to"/"如何"/steps in title or h2s)
    is_tutorial = bool(re.search(r'(如何|怎么做|怎么用|步骤|教程|指南|实操|step|how.to|how-to|完整流程)', title, re.I))
    
    # Extract H2 headings
    h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', content)
    
    # Need at least 3 H2s or tutorial indicators
    if not is_tutorial and len(h2s) < 4:
        COUNT["skipped"] += 1
        return False
    
    # Build steps from H2s (skip FAQ, 相关推荐, etc.)
    skip_keywords = ['常见问题', '相关推荐', 'faq', 'conclusion', '写在最后', '总结', 'Q&A']
    steps = []
    for h2 in h2s[:8]:  # max 8 steps
        clean_h2 = re.sub(r'<[^>]+>', '', h2).strip()
        if any(kw in clean_h2.lower() for kw in skip_keywords):
            continue
        
        # Extract first paragraph after this H2 as step description
        escaped_h2 = re.escape(h2)
        p_m = re.search(
            escaped_h2 + r'</h2>\s*<p>(.*?)</p>',
            content, re.DOTALL
        )
        step_desc = ""
        if p_m:
            step_desc = re.sub(r'<[^>]+>', '', p_m.group(1)).strip()
            step_desc = step_desc[:200]  # truncate
        
        steps.append({
            "@type": "HowToStep",
            "name": clean_h2[:80],
            "text": step_desc or f"详见本文关于「{clean_h2[:50]}」的详细讲解。"
        })
    
    if len(steps) < 2:
        COUNT["skipped"] += 1
        return False
    
    # Build HowTo schema
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": title[:110],
        "description": description[:200],
        "step": steps
    }
    
    # Also estimate total time based on step count
    if len(steps) <= 3:
        howto["totalTime"] = "PT10M"
    elif len(steps) <= 6:
        howto["totalTime"] = "PT20M"
    else:
        howto["totalTime"] = "PT30M"
    
    howto_html = '\n    <script type="application/ld+json">\n' + \
                 json.dumps(howto, ensure_ascii=False, indent=2) + \
                 '\n    </script>'
    
    # Insert before </head>
    if '</head>' in content:
        content = content.replace('</head>', howto_html + '\n    </head>', 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        COUNT["howto"] += 1
        return True
    
    return False

def main():
    dirs = ["articles/cases", "articles/news", "articles/seo", "articles/startup-100", "tutorials"]
    total = 0
    for d in dirs:
        for f in glob.glob(os.path.join(SITE_DIR, d, "*/index.html")):
            total += 1
            if add_howto_schema(f):
                rel = os.path.relpath(f, SITE_DIR)
                print(f"  ✅ {rel}")
    
    print(f"\n总计: {total} 篇文章")
    print(f"新增 HowTo: {COUNT['howto']} 篇")
    print(f"跳过(无步骤结构): {COUNT['skipped']} 篇")

if __name__ == "__main__":
    main()
