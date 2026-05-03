# OpenClaw Ops Skill

Diretrizes para manutenção de ambiente, permissões e higiene operacional em instâncias OpenClaw/VPS.

## 🛠️ Permissões e Ownership (Docker/Volume)

O OpenClaw opera dentro de um ecossistema de volumes Docker onde a alternância de usuários (`root` vs `node`) pode causar falhas silenciosas de escrita ou Git.

### Padrão de Ouro
- Arquivos editáveis do workspace devem pertencer ao usuário `node:node`.
- Se o OpenClaw falhar em: `git add`, `rename`, `write_file` ou `replace`, a causa primária costuma ser ownership inconsistente.

### Comando de Correção Canônico
Sempre que rodar operações como root que deixem rastro, ou notar erros de permissão, normalize o repositório:
```bash
chown -R node:node /data/workspace/sharebook-agent
```

---

## ☁️ Persistência e Volumes

- As pastas em `/data/workspace/` (incluindo `sharebook-agent/`, `sharebook-ebook-importer/`, etc) estão em volumes persistentes.
- Elas **sobrevivem** a updates de imagem do OpenClaw.
- Não guarde estados críticos fora desses volumes.

---

## ⏱️ Automação e Cron

- Se o container usar cron Linux interno, o setup deve ser **reidempotente**.
- O script de setup do cron deve estar documentado e versionado no repositório (`setup-importer-cron.sh`).
- Não dependa de configuração manual feita via `docker exec` que não esteja em script.

---

## 🖥️ PowerShell e Windows (Windows Ops)

- **Comandos**: NÃO usar `&&`; usar `;` ou chamadas separadas.
- **Encoding**: Texto longo ou sinopses com acentos devem ir via arquivo UTF-8 (`--synopsis-file`), nunca inline na CLI para evitar quebra de caracteres.

---

## 🔍 Diagnóstico Rápido

1. **Ownership**: `ls -la` no arquivo problemático.
2. **Espaço**: `df -h` para garantir que o volume não estourou.
3. **Logs**: Verifique os logs do container se a persistência parecer falhar.
