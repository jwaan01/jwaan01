// Layout QA for the generated SVGs: run `node scripts/check_layout.js assets/*.svg` (needs playwright).
// Checks final-state glyph boxes for frame overflow, container overflow (data-box) and text overlap.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({viewport:{width:1100,height:700}});
  let total = 0;
  for (const f of process.argv.slice(2)) {
    await p.goto('file://' + require('path').resolve(f));
    await p.evaluate(() => { const s = document.createElementNS('http://www.w3.org/2000/svg','style'); s.textContent='*{animation:none!important}'; document.documentElement.appendChild(s); });
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(250);
    const issues = await p.evaluate((name) => {
      const svg = document.documentElement, W = +svg.getAttribute('width'), H = +svg.getAttribute('height');
      const o = svg.getBoundingClientRect();
      const framed = !/divider|contact-(github|email|linkedin)/.test(name), m = framed ? 15 : 0;
      const out = [];
      // fonts really loaded?
      for (const fam of ['HTSfx','HTHead','HTLabel','HTBody','HTBodySemi']) {
        const used = [...document.querySelectorAll('text')].some(t => getComputedStyle(t).fontFamily.startsWith(fam));
        if (used && ![...document.fonts].some(ff => ff.family.replace(/"/g,'') === fam && ff.status === 'loaded')) out.push('FONT NOT LOADED ' + fam);
      }
      // inkRect is hoisted below
      const T = [...document.querySelectorAll('text')].filter(t => !t.dataset.dup && !t.dataset.skip).map(t => {
        const r = inkRect(t), pad = +(t.dataset.pad || 0);
        return { t, s: t.textContent, alt: t.dataset.alt, x0: r.x0 - pad, y0: r.y0 - pad, x1: r.x1 + pad, y1: r.y1 + pad };
      });
      const f1 = v => v.toFixed(0);
      function inkRect(t) {
        const r = t.getBoundingClientRect(), h = r.height;
        const [ti, bi] = (t.dataset.ink || '0 0').split(' ').map(Number);
        return { x0: r.left - o.left, x1: r.right - o.left, y0: r.top - o.top + ti * h, y1: r.bottom - o.top - bi * h };
      }
      for (const a of T) {
        if (a.x0 < m || a.y0 < m || a.x1 > W - m || a.y1 > H - m) out.push(`OUT OF FRAME "${a.s}" [${f1(a.x0)},${f1(a.y0)} → ${f1(a.x1)},${f1(a.y1)}] page ${W}x${H}`);
        if (a.t.dataset.box) {
          const [bx0, by0, bx1, by1] = a.t.dataset.box.split(' ').map(Number);
          const g = inkRect(a.t);
          if (g.x0 < bx0 || g.x1 > bx1 || g.y0 < by0 || g.y1 > by1) out.push(`OVERFLOWS BOX "${a.s}" text [${f1(g.x0)},${f1(g.y0)} → ${f1(g.x1)},${f1(g.y1)}] box [${bx0},${by0} → ${bx1},${by1}]`);
        }
      }
      for (let i = 0; i < T.length; i++) for (let j = i + 1; j < T.length; j++) {
        const a = T[i], c = T[j];
        if (a.alt && a.alt === c.alt) continue;
        const ix = Math.min(a.x1, c.x1) - Math.max(a.x0, c.x0), iy = Math.min(a.y1, c.y1) - Math.max(a.y0, c.y0);
        if (ix > 1 && iy > 1) out.push(`TEXT OVERLAP "${a.s}" × "${c.s}" (${f1(ix)}x${f1(iy)}px)`);
      }
      return out;
    }, f);
    console.log((issues.length ? '✗ ' : '✓ ') + f.split('/').pop() + (issues.length ? '\n   ' + issues.join('\n   ') : ''));
    total += issues.length;
  }
  console.log(total ? `${total} issue(s)` : 'ALL CLEAN');
  await b.close();
})();
