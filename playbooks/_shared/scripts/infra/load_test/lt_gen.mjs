// Gerador do teste de carga SSR de origem externa (roteiro do V2).
// Uso: node lt_gen.mjs <urls.json> <saida.jsonl> <arquivo STOP>
// Grava uma linha por requisição: estágio, tipo (load/probe), UA, início, duração,
// status, Retry-After e bytes recebidos (comprimidos). Para se o arquivo STOP existir.
import https from 'node:https';
import fs from 'node:fs';

const [urlsFile, outFile, stopFile] = process.argv.slice(2);
const urls = JSON.parse(fs.readFileSync(urlsFile, 'utf8'));
const out = fs.createWriteStream(outFile, { flags: 'a' });
const HUMAN = 'SharebookLoadTest/1.0';
const BOT = 'SharebookLoadTest-bot/1.0';
const MAX_RPS = 500;
const agent = new https.Agent({ keepAlive: true, maxSockets: 400 });

const STAGES = [
  { name: 'humano c=3', ua: HUMAN, c: 3, secs: 60 },
  { name: 'humano c=6', ua: HUMAN, c: 6, secs: 60 },
  { name: 'humano c=12', ua: HUMAN, c: 12, secs: 60 },
  { name: 'humano c=24', ua: HUMAN, c: 24, secs: 60 },
  { name: 'bot c=5', ua: BOT, c: 5, secs: 60, probe: 2000 },
  { name: 'bot c=15', ua: BOT, c: 15, secs: 60, probe: 2000 },
  { name: 'bot c=50', ua: BOT, c: 50, secs: 60, probe: 2000 },
  { name: 'bot c=200', ua: BOT, c: 200, secs: 30, probe: 2000 },
  { name: 'recuperacao', ua: HUMAN, c: 0, secs: 180, probe: 5000 },
];

let stopped = false;
const stopWatch = setInterval(() => { if (fs.existsSync(stopFile)) stopped = true; }, 200);

// Limitador global simples: no máximo MAX_RPS inícios por janela de 1 s.
let winStart = Date.now(), winCount = 0;
async function rateGate() {
  for (;;) {
    const now = Date.now();
    if (now - winStart >= 1000) { winStart = now; winCount = 0; }
    if (winCount < MAX_RPS) { winCount++; return; }
    await new Promise(r => setTimeout(r, 1000 - (now - winStart)));
  }
}

function get(url, ua) {
  return new Promise(resolve => {
    const t0 = Date.now();
    const req = https.get(url, { agent, headers: { 'User-Agent': ua, 'Accept-Encoding': 'gzip, br', 'Accept': 'text/html' }, timeout: 30000 }, res => {
      let bytes = 0;
      res.on('data', ch => { bytes += ch.length; });
      res.on('end', () => resolve({ t0, ms: Date.now() - t0, status: res.statusCode, ra: res.headers['retry-after'] ?? null, bytes }));
      res.on('error', e => resolve({ t0, ms: Date.now() - t0, status: 0, err: String(e.code || e.message), bytes }));
    });
    req.on('timeout', () => req.destroy(new Error('timeout')));
    req.on('error', e => resolve({ t0, ms: Date.now() - t0, status: 0, err: String(e.code || e.message), bytes: 0 }));
  });
}

const pick = () => urls[Math.floor(Math.random() * urls.length)];

async function hit(stage, kind, ua) {
  const url = pick();
  const r = await get(url, ua);
  out.write(JSON.stringify({ stage, kind, ua: ua === BOT ? 'bot' : 'humano', url, ...r }) + '\n');
}

async function runStage(s) {
  const end = Date.now() + s.secs * 1000;
  console.log(`${new Date().toISOString()} INICIO ${s.name}`);
  const workers = [];
  for (let i = 0; i < s.c; i++) {
    workers.push((async () => {
      while (!stopped && Date.now() < end) { await rateGate(); await hit(s.name, 'load', s.ua); }
    })());
  }
  if (s.probe) {
    const isRecovery = s.c === 0;
    workers.push((async () => {
      while ((isRecovery || !stopped) && Date.now() < end) {
        const t = Date.now();
        await hit(s.name, 'probe', HUMAN);
        await new Promise(r => setTimeout(r, Math.max(0, s.probe - (Date.now() - t))));
      }
    })());
  }
  await Promise.all(workers);
  console.log(`${new Date().toISOString()} FIM ${s.name}${stopped ? ' (PARADO)' : ''}`);
}

// Com STOP, os estágios de carga são pulados; a recuperação (só sondas, 1 a cada 5 s) roda sempre.
for (const s of STAGES) {
  if (stopped && s.c > 0) continue;
  await runStage(s);
}
clearInterval(stopWatch);
out.end();
agent.destroy();
console.log(stopped ? 'GERADOR PARADO PELO STOP' : 'GERADOR CONCLUIU O ROTEIRO');
