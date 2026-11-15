#!/usr/bin/env node
/*
 * Rampa HTTP para medir o pool Npgsql pela API real.
 *
 * Exemplo:
 * node pg_pool_probe.mjs --slug-url URL --recommend-url URL \
 *   --concurrency 5,20,50,100,200 --duration 15 --out resultado.jsonl
 */
import fs from "node:fs";
import { performance } from "node:perf_hooks";

function args(argv) {
  const result = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    if (!key.startsWith("--")) throw new Error(`argumento inválido: ${key}`);
    const value = argv[++i];
    if (!value || value.startsWith("--")) throw new Error(`valor ausente para ${key}`);
    result[key.slice(2)] = value;
  }
  return result;
}

function percentile(values, p) {
  if (values.length === 0) return null;
  const ordered = [...values].sort((a, b) => a - b);
  return Number(ordered[Math.min(ordered.length - 1, Math.ceil(ordered.length * p) - 1)].toFixed(1));
}

function withNonce(url, nonce) {
  const parsed = new URL(url);
  parsed.searchParams.set("pool_test", nonce);
  return parsed.toString();
}

const opt = args(process.argv);
const slugUrl = opt["slug-url"];
const recommendUrl = opt["recommend-url"];
const output = opt.out;
const durationSeconds = Number(opt.duration ?? 15);
const timeoutMs = Number(opt.timeout ?? 20_000);
const levels = (opt.concurrency ?? "5,20,50,100,200")
  .split(",")
  .map((v) => Number(v.trim()))
  .filter((v) => Number.isInteger(v) && v > 0);

if (!slugUrl || !recommendUrl || !output || !Number.isFinite(durationSeconds) || levels.length === 0) {
  throw new Error("uso: --slug-url URL --recommend-url URL --out ARQ [--concurrency 5,20,...] [--duration 15]");
}

const stream = fs.createWriteStream(output, { flags: "a" });
function write(record) {
  stream.write(`${JSON.stringify(record)}\n`);
  process.stdout.write(`${JSON.stringify(record)}\n`);
}

async function runPhase(concurrency, phase) {
  const deadline = performance.now() + durationSeconds * 1000;
  const durations = [];
  const status = {};
  const errors = {};
  let bytes = 0;
  let requests = 0;
  let sequence = 0;

  async function worker(workerId) {
    while (performance.now() < deadline) {
      const current = sequence++;
      const url = withNonce(current % 2 === 0 ? slugUrl : recommendUrl, `${phase}-${workerId}-${current}`);
      const started = performance.now();
      try {
        const response = await fetch(url, {
          headers: { "User-Agent": "SharebookPgPoolTest/1.0", "Cache-Control": "no-cache" },
          signal: AbortSignal.timeout(timeoutMs),
        });
        const body = await response.arrayBuffer();
        bytes += body.byteLength;
        status[response.status] = (status[response.status] ?? 0) + 1;
      } catch (error) {
        const key = error?.name || "request-error";
        errors[key] = (errors[key] ?? 0) + 1;
      } finally {
        durations.push(performance.now() - started);
        requests += 1;
      }
    }
  }

  const startedAt = new Date().toISOString();
  const started = performance.now();
  await Promise.all(Array.from({ length: concurrency }, (_, i) => worker(i)));
  const elapsedMs = performance.now() - started;
  const ok = Object.entries(status)
    .filter(([code]) => Number(code) >= 200 && Number(code) < 300)
    .reduce((sum, [, count]) => sum + count, 0);

  write({
    type: "phase",
    started_at: startedAt,
    concurrency,
    duration_s: Number((elapsedMs / 1000).toFixed(2)),
    requests,
    ok,
    rps: Number((requests / (elapsedMs / 1000)).toFixed(1)),
    bytes,
    status,
    errors,
    p50_ms: percentile(durations, 0.5),
    p95_ms: percentile(durations, 0.95),
    p99_ms: percentile(durations, 0.99),
    max_ms: durations.length ? Number(Math.max(...durations).toFixed(1)) : null,
  });
}

write({ type: "meta", started_at: new Date().toISOString(), levels, duration_s: durationSeconds, timeout_ms: timeoutMs });
for (let phase = 0; phase < levels.length; phase += 1) await runPhase(levels[phase], phase + 1);
await new Promise((resolve) => stream.end(resolve));
