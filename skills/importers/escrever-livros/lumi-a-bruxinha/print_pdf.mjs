#!/usr/bin/env node
// Imprime HTML -> PDF 512x640 pt sem header/footer do navegador.
// Uso: node print_pdf.mjs <input.html> <output.pdf>
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';

const require = createRequire(import.meta.url);
const globalRoot = execSync('npm root -g').toString().trim();
const { chromium } = require(`${globalRoot}/playwright`);

const [, , input, output] = process.argv;
const browser = await chromium.launch({
  executablePath: process.env.CHROME_BIN || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
});
const page = await browser.newPage();
await page.goto(`file://${input}`, { waitUntil: 'networkidle' });
await page.pdf({
  path: output,
  width: '7.1111in', // 512 pt
  height: '8.8889in', // 640 pt
  printBackground: true,
  displayHeaderFooter: false,
  preferCSSPageSize: true,
});
await browser.close();
