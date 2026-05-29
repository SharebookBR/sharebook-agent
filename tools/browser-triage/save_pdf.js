const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const url = process.argv[2];
  const outPath = process.argv[3];
  if (!url || !outPath) {
    console.error('usage: node save_pdf.js <url> <outPath>');
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    acceptDownloads: true,
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  let pdfResponse = null;
  page.on('response', async (res) => {
    try {
      const ct = res.headers()['content-type'] || '';
      if (ct.includes('application/pdf')) {
        pdfResponse = res;
      }
    } catch {}
  });

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);

    if (!pdfResponse) {
      throw new Error('no pdf response detected');
    }

    const body = await pdfResponse.body();
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, body);

    console.log(JSON.stringify({
      ok: true,
      finalUrl: page.url(),
      pdfUrl: pdfResponse.url(),
      outPath,
      size: body.length,
      magic: body.subarray(0, 8).toString('latin1')
    }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
