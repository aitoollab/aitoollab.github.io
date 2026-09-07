#!/usr/bin/env python3
"""全站页面框架统一：site-topnav + 返回顶部按钮 + 统一页脚。幂等，可重复跑。
- 无 site-topnav 的页面：在 <body> 后注入统一导航（同时剥离 projects 的自制窄导航避免双nav）
- 无 back-to-top 的页面：注入统一返回顶部组件
- 无 footer 的正文页：注入统一页脚（首页/项目库/教程/案例/免责声明/隐私）
排除：验证文件、index_old、tools/ 内部工具页。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TOPNAV = '''<nav class="site-topnav" style="position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:16px;padding:10px 24px;background:rgba(13,17,23,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--border,#30363d);font-size:14px;">
    <a href="/" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:var(--text,#e6edf3);font-weight:700;font-size:16px;">
        <span style="font-size:20px;">🧰</span><span>AiToollab</span>
    </a>
    <a href="/" style="color:var(--muted,#8b949e);text-decoration:none;">首页</a>
    <a href="/tutorials/" style="color:var(--muted,#8b949e);text-decoration:none;">教程</a>
    <a href="/articles/cases/" style="color:var(--muted,#8b949e);text-decoration:none;">案例</a>
    <a href="/projects/" style="color:var(--muted,#8b949e);text-decoration:none;">项目库</a>
    <a href="/projects/wechat-sticker/" style="margin-left:auto;padding:4px 14px;border-radius:6px;background:linear-gradient(135deg,#58a6ff,#3fb950);color:#fff;text-decoration:none;font-weight:600;">公众号贴图项目</a>
</nav>'''

BACKTOP = '''<button id="back-to-top" onclick="window.scrollTo({top:0,behavior:'smooth'})" aria-label="返回顶部">↑</button>
<style>#back-to-top{position:fixed;bottom:24px;right:24px;width:44px;height:44px;border-radius:50%;background:#2563eb;color:#fff;border:none;cursor:pointer;font-size:18px;opacity:0;transition:opacity .3s;z-index:999;pointer-events:none}#back-to-top.show{opacity:.85;pointer-events:auto}#back-to-top:hover{opacity:1}</style>
<script>window.addEventListener('scroll',function(){var b=document.getElementById('back-to-top');if(b)b.classList.toggle('show',window.scrollY>400);});</script>'''

FOOTER = '''<div class="footer" style="margin-top:48px;padding:28px 20px;border-top:1px solid var(--border,#30363d);text-align:center;font-size:13px;color:var(--muted,#8b949e);">
    <p style="margin:0 0 6px;"><strong style="color:var(--text,#e6edf3);">AiToollab</strong> · AI副业项目库</p>
    <p style="margin:0;"><a href="/">首页</a> · <a href="/projects/">项目库</a> · <a href="/tutorials/">教程</a> · <a href="/articles/cases/">案例</a> · <a href="/about/">关于我们</a> · <a href="/disclaimer/">免责声明</a> · <a href="/privacy/">隐私政策</a></p>
    <p style="margin:8px 0 0;font-size:12px;">© 2026 AiToollab · 内容仅供参考，不构成投资建议；项目规则以合作方确认为准</p>
</div>'''

SKIP = {'baidu_verify_codeva-HMCN4wOmUc.html', 'google06ea2c88965e9881.html',
        'yandex_157676615a4f7dcd.html', 'yandex_d66173062a3839fb.html',
        'baidu_verify_codeva.html', 'index_old.html'}

stat = {'nav': 0, 'top': 0, 'foot': 0}
for f in sorted(ROOT.rglob('*.html')):
    if '.git' in f.parts or 'tools' in f.relative_to(ROOT).parts:
        continue
    rel = f.relative_to(ROOT)
    if f.name in SKIP:
        continue
    s = f.read_text(errors='ignore')
    if '<body' not in s:
        continue
    # 首页已有 main-nav，不重复注入导航
    if 'site-topnav' not in s and 'main-nav' not in s:
        s2 = re.sub(r'<nav class="nav"[^>]*>.*?</nav>\s*', '', s, count=1, flags=re.S)  # projects 自制窄导航
        s = re.sub(r'(<body[^>]*>)', r'\1\n' + TOPNAV, s2, count=1)
        stat['nav'] += 1
    if 'back-to-top' not in s:
        s = s.replace('</body>', BACKTOP + '\n</body>', 1)
        stat['top'] += 1
    if 'class="footer"' not in s and '<footer' not in s:
        s = s.replace('</body>', FOOTER + '\n</body>', 1)
        stat['foot'] += 1
    f.write_text(s)
print('注入导航:', stat['nav'], '| 返回顶部:', stat['top'], '| 页脚:', stat['foot'])
