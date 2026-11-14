# Repetir teste de carga SSR a partir de origem externa

## Escopo

Repetir o roteiro controlado de carga SSR com máquina fora da VPS, pela URL
pública e limites atuais 6/3. Manter guardrails de parada, User-Agents
identificáveis, coleta por requisição e amostragem de CPU, memória, swap e
Postgres.

## Valor

Separa o gerador da CPU/rede da produção e valida o caminho Internet → Traefik
→ SSR de verdade.

## Risco

Pode degradar o site se limites ou guardrails falharem. Exige janela
autorizada, origem única e comando de parada imediato.

## Validação

503/`Retry-After: 5` com p95 abaixo de 300 ms, zero 500/Npgsql, Postgres abaixo
de 80 conexões, reserva humana, HIT rápido, `peakInFlight=6` e recuperação sem
restart; comparar explicitamente com o V2 local de 2026-11-14.

## Relações

- Concluído: `backlog/done/protecao-sobrecarga-ssr.md`.
- Capacidade: `capacidade-ssr-vps-replicas-pre-renderizacao.md`.
