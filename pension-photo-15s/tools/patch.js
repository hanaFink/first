// Usage: node tools/patch.js <in> <out> '<json params>'
const path = require('path'), fs = require('fs'), { chromium } = require('playwright');
(async () => {
  const [inp, out, json] = process.argv.slice(2);
  const P = JSON.parse(json);
  const b = await chromium.launch(), p = await b.newPage();
  await p.goto('file://' + path.resolve(__dirname, 'patch.html'));
  const src = 'data:image/webp;base64,' + fs.readFileSync(inp).toString('base64');
  const url = await p.evaluate(([s, P]) => window.patch(s, P), [src, P]);
  fs.writeFileSync(out, Buffer.from(url.split(',')[1], 'base64'));
  await b.close();
})();
