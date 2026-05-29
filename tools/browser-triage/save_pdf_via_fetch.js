const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const url = process.argv[2];
  const outPath = process.argv[3];
  if (!url || !outPath) {
    console.error('usage: node save_pdf_via_fetch.js <url> <outPath>');
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    acceptDownloads: true,
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);

    const result = await page.evaluate(async (targetUrl) => {
      const res = await fetch(targetUrl, { credentials: 'include' });
      const buf = await res.arrayBuffer();
      const bytes = Array.from(new Uint8Array(buf));
      return {
        ok: res.ok,
        status: res.status,
        contentType: res.headers.get('content-type') || '',
        bytes,
      };
    }, url);

    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, Buffer.from(result.bytes));

    console.log(JSON.stringify({
      ok: true,
      finalUrl: page.url(),
      outPath,
      status: result.status,
      contentType: result.contentType,
      size: result.bytes.length,
      magic: Buffer.from(result.bytes).subarray(0, 8).toString('latin1')
    }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
