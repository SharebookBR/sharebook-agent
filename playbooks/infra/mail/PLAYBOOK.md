# Mail Operations

Operacoes de email do agente Sharebook.

## Scripts

- `scripts/sharebook_agent_send_email.py` — envia email pelo SMTP proprio/Stalwart usando o `.env` canonico.
- `scripts/sharebook_bounce_imap.py` — inventaria e processa bounces assincronos por IMAP.

## Regra

Rodar em dry-run quando disponivel antes de qualquer operacao que grave em producao.
