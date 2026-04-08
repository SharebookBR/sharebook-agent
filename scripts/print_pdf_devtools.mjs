#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [,, inputPath, outputPath] = process.argv;
if (!inputPath || !outputPath) {
  console.error('Uso: node scripts/print_pdf_devtools.mjs <input.html> <output.pdf>');
  process.exit(1);
}

const chromiumBin = 'chromium';
const debugPort = 9229;
const profileDir = mkdtempSync(join(tmpdir(), 'chromium-devtools-'));
const targetUrl = inputPath.startsWith('file://') ? inputPath : `file://${inputPath}`;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function waitJsonList(retries = 80) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${debugPort}/json/list`);
      if (res.ok) {
        const list = await res.json();
        if (Array.isArray(list) && list.length) return list;
      }
    } catch {}
    await sleep(150);
  }
  throw new Error('DevTools /json/list não respondeu a tempo.');
}

function wsCall(ws, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = Math.floor(Math.random() * 1e9);
    const onMessage = (event) => {
      try {
        const msg = JSON.parse(event.data.toString());
        if (msg.id !== id) return;
        ws.removeEventListener('message', onMessage);
        if (msg.error) reject(new Error(JSON.stringify(msg.error)));
        else resolve(msg.result || {});
      } catch (e) {
        ws.removeEventListener('message', onMessage);
        reject(e);
      }
    };
    ws.addEventListener('message', onMessage);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

const chrome = spawn(chromiumBin, [
  `--remote-debugging-port=${debugPort}`,
  '--headless=new',
  '--no-sandbox',
  '--disable-gpu',
  '--allow-file-access-from-files',
  `--user-data-dir=${profileDir}`,
  targetUrl,
], { stdio: 'ignore' });

function waitChromeExit(proc) {
  return new Promise(resolve => {
    proc.once('exit', () => resolve());
  });
}

function cleanupProfile() {
  try { rmSync(profileDir, { recursive: true, force: true }); } catch {}
}

(async () => {
  try {
    const list = await waitJsonList();
    const page = list.find(t => t.type === 'page' && (t.url === targetUrl || t.url.startsWith('file://'))) || list.find(t => t.type === 'page');
    if (!page?.webSocketDebuggerUrl) throw new Error('Página DevTools não encontrada.');

    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => {
      ws.addEventListener('open', resolve);
      ws.addEventListener('error', reject);
    });

    await wsCall(ws, 'Page.enable');
    await wsCall(ws, 'Runtime.enable');
    await sleep(350);

    const result = await wsCall(ws, 'Page.printToPDF', {
      printBackground: true,
      displayHeaderFooter: false,
      preferCSSPageSize: true,
      marginTop: 0,
      marginBottom: 0,
      marginLeft: 0,
      marginRight: 0,
    });

    writeFileSync(outputPath, Buffer.from(result.data, 'base64'));
    ws.close();
    chrome.kill('SIGTERM');
    await waitChromeExit(chrome);
    cleanupProfile();
    console.log(`OK ${outputPath}`);
  } catch (err) {
    chrome.kill('SIGKILL');
    await waitChromeExit(chrome);
    cleanupProfile();
    console.error('Erro ao gerar PDF via DevTools:', err.message);
    process.exit(2);
  }
})();
