# Nova Fonte: InfoQ Minibooks

## O que é
`https://www.infoq.com/minibooks/` — minibooks técnicos gratuitos produzidos pela InfoQ. Arquitetura, microserviços, DevOps, linguagens, cloud.

## Por que vale
- Conteúdo editorial de alta qualidade — autores reconhecidos da indústria
- PDFs gratuitos mediante cadastro (pode exigir WAF/JS — investigar)
- Foco técnico alinhado com o corpus do Sharebook

## Descoberta
Item `1332` da fila (`source_blocked`) — WAF challenge bloqueou o worker.

## O que fazer
1. Investigar se o download é possível sem browser (WAF)
2. Se necessário, explorar se há mirror ou RSS com links diretos
3. Criar source dedicada se viável

## Quem faz
Sem executor definido. O heartbeat do OpenClaw, que era o dono desse tipo de expansão, ficou sem runtime com o desprovisionamento do container em 2026-08-16. Enquanto não houver substituto, isso só avança por execução manual no Windows local — decisão em aberto.
