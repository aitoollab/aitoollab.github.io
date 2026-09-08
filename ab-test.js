/**
 * 入口词 A/B 测试（极轻量，无依赖）
 * - 每个实验槽（slot）有若干候选词（variant），按会话稳定分组（localStorage 记住分组，避免同用户来回变）
 * - 页面加载后上报 show；用户点击带 data-ab-click 的入口时上报 click
 * - 数据落在韩国服 /var/www/img.aitoollab.top/_ab/events.jsonl，聚合看 /_ab/report
 *
 * 使用：给入口元素加 data-ab-slot="projects-nav" data-ab-click 属性，
 * 本脚本会把元素文本替换为分到的变体词并自动埋点。
 */
(function () {
  var API = 'https://img.aitoollab.top/_ab';
  var EXP = {
    // 槽位: 候选词数组（A 恒为当前默认词，保证对照）
    'projects-nav': ['项目库', '已跑通项目库', '在赚项目'],
    'projects-cta': ['项目库', '已跑通项目库', '看真实项目'],
    'projects-hero-btn': ['查看当前项目', '看已跑通的项目', '看真实在做的项目'],
    'projects-bridge-btn': ['查看当前项目', '看这个项目的真实数据', '看已跑通的项目']
  };

  function variant(slot) {
    var words = EXP[slot];
    if (!words) return null;
    var k = 'ab_' + slot;
    var v = null;
    try { v = localStorage.getItem(k); } catch (e) {}
    if (!v || words.indexOf(v) === -1) {
      v = words[Math.floor(Math.random() * words.length)];
      try { localStorage.setItem(k, v); } catch (e) {}
    }
    return v;
  }

  function report(slot, v, e) {
    try {
      fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slot: slot, v: v, e: e }),
        keepalive: true
      });
    } catch (err) {}
  }

  document.querySelectorAll('[data-ab-slot]').forEach(function (el) {
    var slot = el.getAttribute('data-ab-slot');
    var v = variant(slot);
    if (!v) return;
    var original = el.textContent;
    el.textContent = v;
    report(slot, v, 'show');
    el.addEventListener('click', function () { report(slot, v, 'click'); }, { passive: true });
  });

  /* ---- 全站点击追踪：任何链接点击都记一条（页面类型+目标+是否A/B入口）---- */
  function pageKind() {
    var p = location.pathname;
    if (p === '/' || p === '/index.html') return 'home';
    if (p.indexOf('/projects/') === 0) return 'project';
    if (p.indexOf('/tutorials/') === 0) return 'tutorial';
    if (p.indexOf('/articles/news/') === 0) return 'news';
    if (p.indexOf('/articles/cases/') === 0) return 'case';
    if (p.indexOf('/articles/') === 0) return 'article';
    return 'other';
  }
  function destKind(href) {
    if (!href) return 'void';
    if (href.indexOf(location.origin) !== 0 && href.indexOf('/') !== 0 && href.indexOf('#') !== 0) return 'external';
    if (href.indexOf('/projects/') === 0) return 'projects';
    if (href.indexOf('/tutorials/') === 0) return 'tutorials';
    if (href.indexOf('/articles/news/') === 0) return 'news';
    if (href.indexOf('/articles/cases/') === 0) return 'cases';
    if (href.indexOf('/articles/') === 0) return 'articles';
    if (href === '/' || href.indexOf('#') === 0) return 'home';
    return 'other';
  }
  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a') : null;
    if (!a) return;
    var tracked = a.hasAttribute('data-ab-slot') || !!a.querySelector('[data-ab-slot]');
    if (tracked) return; // A/B 入口已由上面的槽位逻辑上报，避免重复计数
    var pos = 'nav';
    if (a.closest('.article-grid, .category-grid, .grid')) pos = 'card';
    else if (a.closest('.cta-box, .conversion-bridge, [data-conversion-bridge]')) pos = 'cta';
    else if (a.closest('.footer')) pos = 'footer';
    else if (a.closest('.student-results')) pos = 'results';
    else if (a.closest('article')) pos = 'body';
    report('link:' + pageKind(), destKind(a.getAttribute('href')) + '@' + pos, 'click');
  }, { passive: true });
})();
