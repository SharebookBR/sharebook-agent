# VPS Migration Playbook

## Objetivo
- Concentrar o que é específico de **migrar a instância Coolify entre VPS** (evento raro, caro quando dá errado) — separado da operação do dia a dia, que vive em `coolify-vps.md`.
- Registrar a classe de problema recorrente nesse tipo de evento: coisa que **sobrevive ao restore mas para de funcionar silenciosamente**, sem nenhum sinal na UI. Já aconteceu três vezes em migrações diferentes: backup de banco, backup de imagens, source GitHub App do Coolify.

## Checklist proativo — dia da migração e semana seguinte

Não esperar alguém tropeçar semanas depois pra descobrir que algo sobreviveu ao restore só na aparência. Testar de propósito, com evidência real, não com o status verde da tela:

1. **Backup de banco real, não banco de manutenção vazio.** Forçar execução manual e conferir tamanho do dump (dezenas de MB esperado, não KB). Ver "Backup agendado" em `coolify-vps.md`.
2. **Backup de imagens/volumes indo pro S3 de verdade, não só disco local.** Conferir `s3_uploaded = true` no banco do Coolify, não só `status = success`. Ver "Backup das imagens" em `coolify-vps.md`.
3. **DNS resolvendo certo nas três camadas do host** (`/etc/resolv.conf`, systemd-resolved, `daemon.json` do Docker) — ver seção "DNS" abaixo. `resolvectl query` acertando não prova que `getent hosts` também acerta.
4. **Auto-deploy (webhook GitHub → Coolify) enfileirando sozinho**, não só a aparência de "Connected"/"Running" na UI. Testar com um commit trivial e push real, e conferir `application_deployment_queues` recebendo o job sem intervenção manual. Ver "GitHub App source quebra silenciosa" abaixo — achado em 19/09/2026, depois de a caixa já estar rodando há mais de um mês.
5. **Certificados Let's Encrypt válidos** (copiar `acme.json`, não deixar o Traefik reemitir — risco de rate limit).
6. **Crontab e scripts de `/usr/local/bin/` migrados**, não só os containers.

## DNS na VPS HostGator — três camadas independentes

Aprendido no corte de 2026-08-17, depois de um typo no IP publicado por alguns minutos.

Um erro de digitação no DNS (`29.` em vez de `129.`) sobrevive muito depois de corrigido, porque resolvedores públicos cacheiam o valor errado pelo TTL inteiro. No corte, o Google DNS segurou o IP inválido por quase uma hora enquanto o Cloudflare já servia o correto.

**A caixa tem três caminhos de resolução, e eles não conversam:**

1. **`/etc/resolv.conf`** — arquivo comum (não link), fixado pela HostGator em `8.8.8.8`. É o que `getent`, `curl` e praticamente todo processo do host usam de verdade.
2. **systemd-resolved** — está ativo, mas o `/etc/nsswitch.conf` é `hosts: files dns`, **sem o módulo `resolve`**. Então `resolvectl dns` e os drop-ins de `resolved.conf.d` não afetam a resolução real do host. Mexer só neles dá a ilusão de conserto.
3. **Docker** — containers ignoram o `resolv.conf` do host quando ele aponta para loopback; o que vale é `"dns"` no `/etc/docker/daemon.json`. Exige `systemctl restart docker`.

**Sintoma diagnóstico**: `resolvectl query X` responde certo e `getent hosts X` responde errado. Isso não é cache teimoso — é a camada 2 não estar no caminho. Ir direto na camada 1.

Configuração aplicada: Cloudflare primeiro nas camadas 1 e 3, com backups em `/root/resolv.conf.bak-pre-migracao` e `/root/daemon.json.bak-pre-migracao`. **O `resolv.conf` pode ser reescrito em reboot ou reprovisionamento** — reconferir depois de qualquer um dos dois.

**Efeito colateral não óbvio**: o frontend faz SSR chamando `api.sharebook.com.br` pelo nome público. Com DNS envenenado, cada render trava até o timeout, o healthcheck de 5s nunca passa, o container nunca fica `healthy` e o Traefik devolve **503**. O 503 parece falha de proxy e é falha de DNS. Antes de culpar Traefik ou healthcheck, rodar `docker exec <app> getent hosts <api>`.

## Migração de instância Coolify entre VPS

Validado em 2026-08-17 (Hostinger → HostGator), Coolify 4.3.6 nos dois lados.

### Duas caixas ao mesmo tempo
- `vps_ssh.py` aceita `--prefix` (default `VPS_SSH`). Credenciais da caixa nova vivem em `VPS_HOSTGATOR_SSH_*` no `.env`.
- Para mover volume de dados, criar confiança SSH **direta entre as caixas** — nunca trafegar conteúdo pelo contexto do agente. `ssh-keygen` na origem, **append** da pública no `authorized_keys` do destino.
- **Nunca sobrescrever o `authorized_keys` de uma VPS HostGator.** Ela chega com ~11 chaves da plataforma; remover qualquer uma quebra o gerenciamento pelo painel deles. Só `>>`, nunca `>`.

### O que dumpar
- Dumpar **só o banco `coolify`** (`pg_dump -U coolify -d coolify --no-owner --no-acl`), **não `pg_dumpall`**. O dumpall arrasta roles com senha e conflita com a senha que a instalação nova gravou no volume do `coolify-db`.
- Com o dump de banco único, o único segredo que precisa atravessar é o `APP_KEY`.

### APP_KEY — a armadilha cara
O `APP_KEY` de `/data/coolify/source/.env` decifra env vars e chaves de deploy no banco. Trocar o arquivo **não basta**:

- `docker stop` + `docker start` **não relê `env_file`**. O container foi criado com a chave antiga e continua com ela na memória.
- É obrigatório recriar: `cd /data/coolify/source && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --force-recreate coolify soketi`
- **Os nomes de serviço do compose não são os nomes dos containers.** Serviços: `redis`, `soketi`, `postgres`, `coolify`. O container `coolify-realtime` corresponde ao serviço `soketi`. Passar nome de container faz o compose abortar inteiro sem recriar nada — e o sintoma é idêntico ao de não ter feito nada.
- Trocar o `APP_KEY` no arquivo com `sed` é frágil: o valor é base64 e contém `/` e `+`. Preferir `grep -v '^APP_KEY=' .env > novo && cat chave-antiga >> novo`.

### Diagnóstico honesto de `DecryptException`
Não presumir chave errada. Comparar por hash, sem imprimir segredo:
```
docker exec coolify printenv APP_KEY | tr -d '\n' | sha256sum | cut -c1-16
grep '^APP_KEY=' /data/coolify/source/.env | cut -d= -f2- | tr -d '\n' | sha256sum | cut -c1-16
```
Hashes diferentes → problema é container, não chave.

Validar a decifragem sem vazar valor:
```
docker exec coolify php artisan tinker --execute='try { $v = \App\Models\EnvironmentVariable::first()->value; echo "OK len=" . strlen($v); } catch (\Throwable $e) { echo "FALHOU: " . get_class($e); }'
```

### Certificados
`/data/coolify/proxy/acme.json` guarda os certificados Let's Encrypt. **Certificado é vinculado a domínio, não a IP** — copiar o `acme.json` para a caixa nova faz o Traefik novo nascer com certificado válido, sem reemissão no corte e sem exposição a rate limit.

### O que mais copiar
`/data/coolify/ssh` (chaves de deploy), `/data/coolify/proxy`, `/data/coolify/databases` (nginx conf dos proxies de banco), `/data/coolify/services`. Pular `/data/coolify/backups` — é histórico, não estado.

## GitHub App source quebra silenciosa

Achado em 19/09/2026, mais de um mês depois da migração Hostinger→HostGator — a quebra não deu sintoma até alguém tropeçar nela reorganizando sources no Coolify.

**O que aconteceu**: a GitHub App conectada como source de uma application no Coolify pode sobreviver ao restore (aparece `Connected`, a app aparece `Running`) mas parar de entregar webhook funcional. Nenhum erro visível — o deploy simplesmente não enfileira sozinho no próximo push, e sem investigar parece problema de webhook/secret/branch protection do lado do GitHub.

**Padrão de nomenclatura como rastro de gerações**: cada rodada de correção cria uma GitHub App nova com sufixo numérico incremental (`pegasus-github-app` → `app2` → `app3`; mesmo padrão do lado `sharebook-github-app*`). O app sem sufixo ou o penúltimo sufixo geralmente já está órfão de uma correção anterior, sem ninguém ter voltado pra limpar. Isso por si só é sinal: se existe `algo-app3`, desconfiar que `algo` e `algo2` são sucata.

**Correção**: criar GitHub App nova na organização certa (Developer settings → GitHub Apps → New GitHub App), trocar a source de cada application afetada (`Git Source` na página da app → Redeploy pra aplicar), depois desvincular e apagar as sources velhas — primeiro no Coolify (bloqueia se ainda houver application usando, tem que consultar `applications.source_id` no banco pra achar todas, o erro não diz quais), depois no GitHub (`Delete GitHub App` na Danger Zone da app antiga, não só `Uninstall` — apps criados só pra essa integração não têm motivo pra ficar registrados).

**Prova real de que voltou a funcionar** (mesma receita da seção de validação, não confiar em "Connected" sozinho):
```sql
select id, name, source_id, source_type, git_repository, git_branch from applications where name = 'NOME-DA-APP';
```
Depois, commit trivial + push real na branch configurada, e:
```sql
select id, application_id, status, commit, created_at from application_deployment_queues order by id desc limit 5;
```
`application_id` guarda o **ID numérico** da application, não o UUID — comparar com o UUID roda sem erro mas devolve vazio, parecendo falha de webhook quando na verdade é filtro errado. Cruzar com `docker logs coolify --since 5m | grep ApplicationDeploymentJob` se a query parecer vazia sem explicação.

Fechar validando o container: `docker ps` com a imagem carregando o SHA exato do commit, `healthy`.

**Achado colateral que vale generalizar**: uma application criada fora do fluxo normal de UI (ex: via API do Coolify, ver `coolify-vps.md`) pode nascer com a source errada sem ninguém perceber — `sharebook-frontend-dev`, criada via API em 17/09, estava apontando pra GitHub App de **outra organização** (Pegasus, não Sharebook) apesar do repositório ser do Sharebook. Sempre conferir `source_id`/`github_apps.name` contra a organização dona do repositório depois de criar application por API.
