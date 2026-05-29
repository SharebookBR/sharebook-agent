const { chromium } = require('playwright');

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('usage: node triage_fetch.js <url>');
    process.exit(2);
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    acceptDownloads: true,
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  const requests = [];
  const responses = [];
  page.on('request', req => requests.push(req.url()));
  page.on('response', async res => {
    try {
      responses.push({ url: res.url(), status: res.status(), contentType: res.headers()['content-type'] || '' });
    } catch {}
  });

  try {
    const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);

    const title = await page.title().catch(() => '');
    const finalUrl = page.url();
    const content = await page.content();
    const links = await page.locator('a').evaluateAll(nodes => nodes.map(a => ({ text: (a.textContent || '').trim(), href: a.href })).filter(x => x.href));

    const pdfLike = links.filter(x => /pdf|download|viewcontent|cgi/i.test(x.href) || /pdf|download/i.test(x.text)).slice(0, 20);

    console.log(JSON.stringify({
      ok: true,
      startUrl: url,
      finalUrl,
      status: resp ? resp.status() : null,
      title,
      pdfLike,
      responses: responses.slice(-30),
      contentSnippet: content.slice(0, 4000)
    }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
