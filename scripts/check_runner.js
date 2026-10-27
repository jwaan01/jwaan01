// Night Run QA: popups must never cover the runner at any event time. Usage: node scripts/check_runner.js assets/night-run.svg
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1000, height: 340 } });
  await p.goto('file://' + require('path').resolve(process.argv[2])); await p.evaluate(() => document.fonts.ready);
  for (const t of [3.24, 4.6, 5.95, 6.1, 6.2, 7.74, 9.1, 10.35, 10.5, 10.6]) {
    const r = await p.evaluate(ms => {
      document.getAnimations().forEach(a => { a.pause(); a.currentTime = ms; });
      const run = document.querySelector('.runner-body').getBoundingClientRect();
      const hits = [...document.querySelectorAll('text')].filter(x => { const g = x.closest('g[style*="opacity:0"]'); if (!g) return false; const o = +getComputedStyle(g).opacity; if (o < .05) return false; const q = x.getBoundingClientRect(); return !(q.right < run.left || q.left > run.right || q.bottom < run.top || q.top > run.bottom); }).map(x => x.textContent);
      return hits;
    }, t * 1000);
    console.log(t, r.length ? 'OVER RUNNER: ' + r.join(',') : 'clear');
  }
  await b.close();
})();
