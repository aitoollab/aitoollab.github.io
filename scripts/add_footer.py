#!/usr/bin/env python3
"""批量给文章添加统一页脚（信任页链接 + 版权声明）"""
import os, glob, re

SITE_DIR = "/home/agentuser/.hermes/hermes-agent/aitoollab"
FOOTER_HTML = """    <section class="conversion-bridge" data-conversion-bridge style="margin:40px 0;padding:24px;border:1px solid var(--border,#30363d);border-radius:12px;background:rgba(37,99,235,.08);text-align:center;">
        <strong>先拿一个可执行的结果</strong>
        <p>这篇教程解决一个具体问题。想继续找方向、拿模板或和正在实操的人交流，可以先免费加入「人工智能掘金」交流群；需要成套提示词时，再查看 ¥39 实战包。</p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;">
            <a href="/" style="padding:8px 14px;border:1px solid var(--border,#30363d);border-radius:7px;">回首页看产品路径</a>
            <a href="/prompt-pack/?src=article" style="padding:8px 14px;background:#2563eb;color:#fff;border-radius:7px;">查看 ¥39 实战包</a>
        </div>
        <p style="margin-top:10px;font-size:12px;color:var(--muted,#8b949e);">扫码入口在首页；如果你已经试过这篇方法，欢迎把结果或卡点发到 contact@aitoollab.top。</p>
    </section>
"""

def process_article(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 清理历史上无法核验的社会证明，不用虚构数字换转化
    old_content = content
    content = content.replace('已帮助800+小伙伴提升效率 你的对手可能已经在用了', '页面不放未经核验的用户评价；先看免费内容，再决定是否购买。')
    changed = content != old_content
    if 'data-conversion-bridge' in content:
        normalized = re.sub(
            r'<section class="conversion-bridge" data-conversion-bridge(?: style="[^"]*")?>',
            '<section class="conversion-bridge" data-conversion-bridge style="margin:40px 0;padding:24px;border:1px solid var(--border,#30363d);border-radius:12px;background:rgba(37,99,235,.08);text-align:center;">',
            content, count=1)
        changed = normalized != content or changed
        content = normalized
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    # 优先插入已有 footer 前；没有 footer 则插入 body 前
    if '<div class="footer"' in content:
        new_content = content.replace('<div class="footer"', FOOTER_HTML + '    <div class="footer"', 1)
    else:
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
