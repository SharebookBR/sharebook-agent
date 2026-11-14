# Restore drill controlado dos backups

> **Concluído em 2026-11-14.** O Sharebook é recuperável a partir dos backups remotos: banco e capas voltaram íntegros, e o Raffa subiu o frontend contra o restore e aprovou o resultado ("impecável"). Receita reaproveitável em `playbooks/infra/coolify-vps.md`, seção "Restore a partir do GCS — receita validada".

## Resultado (2026-11-14)

**Onde:** Windows local do Raffa, declarado por ele como máquina confiável e com Docker. Mudou o plano original (container temporário na VPS): restaurar fora da VPS prova também o cenário de desastre, em que a VPS não existe. Executor: Claude Code no Windows (o texto original dizia OpenClaw, mas este habitat tem SSH na VPS).

**Fonte:** backups da noite de 2026-11-14 (03:00 UTC), baixados **do bucket GCS**, não da cópia local da VPS, por URLs pré-assinadas de 30 min geradas dentro do Coolify (a credencial do bucket não saiu de lá).

| Artefato | Tamanho | Download do GCS | Restore |
|---|---|---|---|
| `sharebook` (dump custom) | 52.589.244 B, idêntico ao registro | 18 s | `pg_restore` 4 s, 0 erros, 22 tabelas |
| `sharebook_importer` | 5.446.929 B, idêntico | 1 s | 1 s, 0 erros, 4 tabelas |
| Capas (`tar.gz`) | 1.233.636.879 B, idêntico | 129 s | extração 10 s, 5.963 arquivos (3.028 capas + 2.935 miniaturas) |

**Prova de integridade:**

- Livros criados antes do início do dump: **2.858 no restore e 2.858 em produção**. Diferenças nas tabelas vivas são atividade posterior ao dump (os 4 livros de `vida_bem_estar_2026` publicados às 18h26 do mesmo dia, usuários, logs e jobs). Tabelas estáticas (categorias, tags, meetups, `__EFMigrationsHistory`) idênticas; `importer.queue_items` e `importer.sources` idênticas.
- Capas: 2.857 de 2.858 `ImageSlug` têm arquivo no backup; amostra de 41 imagens decodificada sem erro. A única ausente (`o-orfanato-da-srta-peregrine-para-criancas-pe.jpg`, livro físico em "Aguardando envio") **também responde 404 em produção**: falha anterior ao backup, não do backup. 196 arquivos no backup não têm livro no banco (órfãos).
- Aplicação: backend local (.NET 10) e frontend SSR (`npm run dev:ssr`) subiram contra o restore; a API aplicou as migrações na cópia sem erro, serviu livros e capas; o Raffa subiu o frontend nessa configuração e aprovou. Livros criados depois do dump não aparecem, o que confirma que o site mostrava o backup e não a produção.

**Tempo de recuperação observado:** ~2,5 min de download + segundos de restore. No desastre real, o tempo dominante passa a ser provisionar a nova VPS e reconfigurar o Coolify, não os dados.

**Fricções que viraram receita:** `<?php` quebra o tinker por stdin; Git Bash converte `/tmp/...` em caminho Windows (`MSYS_NO_PATHCONV=1`); `dotnet restore` com `NU1103` por índice NuGet velho (`--no-http-cache`).

**Fora do escopo, de propósito:** `pegasus_core` e `simula_plus` (não são Sharebook) e os PDFs de ebooks (vivem no S3, não neste backup).

**Achados colaterais:** a capa ausente acima (produção já está sem ela) e o `npm start` do frontend quebrado no Angular 22, corrigido no commit `7a92591` do frontend.

## Prioridade

**Topo do backlog, por decisão do Raffa em 2026-11-14.** Temos um processo de backup, mas **nunca o usamos para restaurar**; este item valida se seria possível ou não recuperar o Sharebook. É o que protege contra o pior cenário (perda de dados).

Por que importa, com a história do próprio projeto: em 2026-08-17 descobriu-se que o backup agendado do Postgres apontava para o banco de manutenção `postgres`, **vazio**, em vez dos bancos reais. Rodava toda noite, subia ao bucket e gravava `success`, com arquivos de **exatamente 1.055 bytes**, **desde pelo menos setembro de 2025**: quase um ano de "backups" que não guardavam nada (ver `playbooks/infra/coolify-vps.md`, seção "Backup agendado — success não prova backup"). Foi corrigido e os tamanhos hoje são coerentes (por exemplo `sharebook` na casa de dezenas de MB, volume de capas ~1,3 GB, `s3_uploaded=true`), mas **nenhum restore foi testado**.

**Ordem entre itens:** este item vem **antes** do teste de estresse do Postgres (`investigar-pool-conexoes-e-limite-postgres.md`), porque levar o banco ao limite sem saber se o backup restaura é o pior momento para descobrir que não restaura; e **antes** da migração dos backups para a AWS (`migracao-backups-gcp-aws.md`), para não migrar algo que não sabemos recuperar.

**Versão mínima proposta por Claude (a confirmar com o Raffa, em nome da simplicidade):** restaurar o dump mais recente do banco `sharebook` num container temporário de Postgres, conferir algumas contagens (livros, usuários, categorias) e algumas consultas, abrir algumas capas do volume restaurado, apagar tudo e escrever o passo a passo no playbook de infra. Sem ritual mensal nem automação por ora; repetir quando a infraestrutura mudar. Executor: o OpenClaw (este agente não tem acesso ao servidor).

## Escopo

Executar restore seguro e documentado de dump Postgres e volume de capas a
partir de backup remoto, sem tocar produção.

## Valor

Upload confirmado não prova recuperabilidade. O drill fecha o principal gap de
continuidade operacional.

## Risco

Destino errado pode sobrescrever produção ou expor dados. Usar ambiente isolado,
permissões mínimas e descarte seguro do material restaurado.

## Validação

Objeto remoto, checksum/tamanho, restore de banco e arquivos, integridade
mínima da aplicação restaurada e limpeza do ambiente temporário registrados.

## Relações

- Observabilidade: `observabilidade-sharebook-epico.md`.
- Migração: `migracao-backups-gcp-aws.md`.
