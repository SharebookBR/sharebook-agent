const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('usage: node download_probe.js <url>');
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    acceptDownloads: true,
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  const seenResponses = [];
  page.on('response', async res => {
    try {
      seenResponses.push({ url: res.url(), status: res.status(), contentType: res.headers()['content-type'] || '' });
    } catch {}
  });

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(4000);

    const link = page.locator('a', { hasText: /pdf|download/i }).first();
    const href = await link.getAttribute('href').catch(() => null);

    let downloadInfo = null;
    if (href) {
      const [ download ] = await Promise.all([
        page.waitForEvent('download', { timeout: 20000 }).catch(() => null),
        link.click().catch(() => null),
      ]);
      if (download) {
        downloadInfo = {
          suggestedFilename: download.suggestedFilename(),
          url: download.url(),
        };
      }
    }

    console.log(JSON.stringify({
      ok: true,
      startUrl: url,
      finalUrl: page.url(),
      title: await page.title().catch(() => ''),
      href,
      downloadInfo,
      responses: seenResponses.slice(-40),
      contentSnippet: (await page.content()).slice(0, 4000),
    }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
