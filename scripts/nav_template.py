"""Shared three-column navigation markup for AiToollab pages."""

NAV_HTML = '''<nav class="site-topnav" style="position:sticky;top:0;z-index:100;display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);align-items:center;padding:10px 24px;background:rgba(13,17,23,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--border,#30363d);font-size:14px;">
    <a href="/" style="grid-column:1;justify-self:start;display:flex;align-items:center;gap:8px;text-decoration:none;color:var(--text,#e6edf3);font-weight:700;font-size:16px;white-space:nowrap;">
        <span style="font-size:20px;">🧰</span><span>AiToollab</span>
    </a>
    <div style="grid-column:2;display:flex;align-items:center;justify-content:center;gap:18px;white-space:nowrap;">
        <a href="/" style="color:var(--muted,#8b949e);text-decoration:none;">首页</a>
        <a href="/tutorials/" style="color:var(--muted,#8b949e);text-decoration:none;">教程</a>
        <a href="/articles/cases/" style="color:var(--muted,#8b949e);text-decoration:none;">案例</a>
        <a href="/projects/" style="color:var(--muted,#8b949e);text-decoration:none;"><span data-ab-slot="projects-nav">项目库</span></a>
    </div>
    <a href="/projects/" style="grid-column:3;justify-self:end;padding:4px 14px;border-radius:6px;background:linear-gradient(135deg,#58a6ff,#3fb950);color:#fff;text-decoration:none;font-weight:600;white-space:nowrap;"><span data-ab-slot="projects-nav">项目库</span></a>
</nav>'''
