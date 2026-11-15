# Teste de pool Npgsql/Postgres

`pg_pool_probe.mjs` faz uma rampa HTTP contra `Slug` e `Recommendations`, ou
seja, o caminho real API -> Npgsql -> Postgres. `pg_pool_monitor.py` roda na
VPS e registra por segundo sessões do banco, CPU/memória/swap do host e dos
dois containers.

O teste deve ser executado com uma janela autorizada e backup restaurável
confirmado. O gerador atual pode rodar no mesmo host do agente; registrar essa
limitação ao interpretar CPU e vazão.

Não usar os scripts para alterar pool ou configuração. A mudança de ambiente e
o redeploy pertencem ao Coolify; cada rodada deve guardar o valor exato do pool
e devolver a configuração que ganhou a comparação.
