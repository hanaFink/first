// Renders scene.html frame by frame with headless Chromium.
// Usage: node render.js <outDir> [fps=30] [duration=15] [t1,t2,... preview times]
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const outDir = process.argv[2] || 'frames';
  const fps = Number(process.argv[3] || 30);
  const duration = Number(process.argv[4] || 15);
  const preview = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(__dirname, 'scene.html'));
  await page.evaluate(() => window.sceneReady);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => Promise.all([...document.fonts].map(f => f.load())));

  const times = preview || Array.from({ length: Math.round(fps * duration) }, (_, i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(t => window.render(t), times[i]);
    const name = preview ? `t${times[i].toFixed(2)}.png` : `${String(i).padStart(4, '0')}.png`;
    await page.screenshot({ path: path.join(outDir, name) });
    if (!preview && i % 30 === 0) process.stdout.write(`frame ${i}/${times.length}\n`);
  }
  await browser.close();
})();
