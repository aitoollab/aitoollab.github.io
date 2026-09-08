"""Shared three-column navigation markup for AiToollab pages."""

NAV_HTML = '''<nav class="site-topnav" style="position:sticky;top:0;width:100vw;margin-left:calc(50% - 50vw);z-index:100;background:rgba(13,17,23,0.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--border,#30363d);font-size:14px;">
    <div style="max-width:1120px;margin:0 auto;min-height:56px;display:grid;grid-template-columns:minmax(180px,1fr) auto minmax(180px,1fr);align-items:center;padding:0 20px;">
        <a href="/" style="grid-column:1;justify-self:start;display:flex;align-items:center;gap:8px;text-decoration:none;color:var(--text,#e6edf3);font-weight:700;font-size:16px;white-space:nowrap;">
            <span style="font-size:20px;">🧰</span><span>AiToollab</span>
        </a>
        <div style="grid-column:2;justify-self:start;display:flex;align-items:center;gap:18px;padding-left:28px;white-space:nowrap;">
            <a href="/" style="color:var(--muted,#8b949e);text-decoration:none;">首页</a>
            <a href="/tutorials/" style="color:var(--muted,#8b949e);text-decoration:none;">教程</a>
            <a href="/articles/cases/" style="color:var(--muted,#8b949e);text-decoration:none;">案例</a>
        </div>
        <a href="/projects/" style="grid-column:3;justify-self:end;padding:7px 14px;border-radius:7px;background:linear-gradient(135deg,#58a6ff,#3fb950);color:#fff;text-decoration:none;font-weight:600;white-space:nowrap;"><span data-ab-slot="projects-cta">项目库</span></a>
    </div>
</nav>'''
