# 2026-08-17 — Migração para a HostGator e os backups que nunca existiram

## 1. Modelo e ambiente

- **Modelo:** Claude Opus 5, via Claude Code.
- **Runtime:** Windows local (`C:\Repos\SHAREBOOK`). PowerShell como shell primário.
- **Acesso:** SSH nas duas VPS via `scripts/infra/vps_ssh.py`; MCP do Gmail para achar os e-mails da HostGator; MCP `scheduled-tasks` para agendar a revisão.
- **Duração:** sessão longa, começou como "me ajuda a migrar" e terminou em auditoria de backup.
- **Caixa nova:** `129.121.36.220`, SSH na porta **22022** (não-padrão, escolha da HostGator), Ubuntu 22.04.5 LTS, 4 vCPU, 7,8 GB RAM, 196 GB. Produto: **VPS OCI NVMe 8**.
- **Caixa velha:** `212.85.23.202` (Hostinger, `srv1005404`), mantida desligada como rollback.

## 2. Skills acionadas

Consultadas:
- `AGENTS.md` (obrigatório por `CLAUDE.md`)
- `skills/runtime/windows-local.md`
- `skills/infra/INDEX.md` e `skills/infra/coolify-vps.md`
- `skills/product-ux/INDEX.md`, `voice-glossary/SKILL.md` e `references/ux-writing-guide.md`
- skill `schedule` (avaliada e **descartada** — ver decisões)

Atualizadas:
- `skills/infra/coolify-vps.md` — três seções novas, três commits (`4758897`, `d0b36a1`, `f497ef6`)
- `scripts/infra/vps_ssh.py` — suporte a `--prefix` (commit `4dea3cc`)

## 3. O que foi feito

### 3.1 Migração de VPS, ponta a ponta

Estratégia escolhida: **lift-and-shift do Coolify**, não rebuild limpo. As 87 environment variables e as chaves de deploy do GitHub eram a parte cara de refazer à mão; o backup oficial + `APP_KEY` preserva tudo.

Ordem executada: recon → swap → Docker + Coolify → restore da instância → dados → ensaio → corte.

**Corte final: 59 segundos** (15:48:56 → 15:49:55 UTC), com os apps das duas caixas parados para garantir dump limpo.

Inventário migrado: 4 apps (`sharebook-frontend`, `sharebook-api`, `pegasus-core-api`, `simula-plus-api`), 1 Postgres com 8 bancos (~1,6 GB), wwwroot com 1,2 GB, 4 scripts de cron, certificados Let's Encrypt.

`pgadmin4` estava `exited:unhealthy` havia meses; Raffa decidiu não migrar.

### 3.2 Três armadilhas do lift-and-shift

Nenhuma estava documentada e todas travariam a migração:

1. **Porta SSH** — o registro do servidor no Coolify veio do dump com `port=22`, mas a HostGator usa `22022`. Sintoma: `connect to host host.docker.internal port 22: Connection refused`.
2. **Chave do servidor** — o Coolify fala com o próprio host por SSH usando a chave em `private_keys` id 0 (`localhost's key`). O dump traz a chave **velha**, e o `authorized_keys` da caixa nova tem a chave da instalação **nova**. Precisa derivar a pública da privada em `/data/coolify/ssh/keys/` e fazer append.
3. **Versão do Coolify** — a caixa velha se auto-atualizou de 4.1.2 para 4.3.6 na madrugada anterior. Por sorte o instalador puxou exatamente 4.3.6, sem drift. Se tivesse instalado versão mais velha que o dump, o restore quebraria.

### 3.3 O typo do DNS e o envenenamento de cache

Raffa publicou `29.121.36.220` em vez de `129.121.36.220` — faltou o `1`. Corrigiu em minutos, mas o estrago sobreviveu: **resolvedores públicos cachearam o IP inválido pelo TTL de 3600**.

A caixa nova consultou o DNS durante essa janela e guardou o valor errado. Efeito em cadeia, nada óbvio:

> frontend faz SSR chamando `api.sharebook.com.br` → resolve para IP morto → cada render trava até timeout → healthcheck de 5s nunca passa → container nunca fica `healthy` → **Traefik devolve 503**

O 503 tem cara de falha de proxy e era falha de nome.

**Errei o primeiro conserto.** Troquei o DNS via `resolvectl` e drop-in em `resolved.conf.d`, e o `getent` continuou errado. O motivo: `/etc/nsswitch.conf` é `hosts: files dns`, **sem o módulo `resolve`** — ou seja, o systemd-resolved não está no caminho real da resolução do host. O que manda é `/etc/resolv.conf`, arquivo comum fixado pela HostGator em `8.8.8.8`. São três camadas independentes (resolv.conf, systemd-resolved, daemon.json do Docker) e eu consertei a que não importava primeiro.

Sinal diagnóstico que resolve isso em segundos: **`resolvectl query` acerta e `getent hosts` erra** → a camada 2 não está no caminho, vá direto na 1.

### 3.4 Backup de banco: um ano de teatro

Fui configurar backup na caixa nova e encontrei um já existente, com `success` diário desde pelo menos setembro de 2025. Todos os arquivos com **exatamente 1.055 bytes**.

Causa: `databases_to_backup = postgres` — o banco de manutenção **vazio**, não os bancos reais.

**Durante cerca de um ano não existiu backup de dado nenhum, e o painel afirmava o contrário.** Corrigido nas duas caixas para `sharebook,sharebook_importer,pegasus_core,simula_plus` e validado com execução forçada: 76 MB, 37 MB, 4,9 MB e 62 KB.

### 3.5 Backup de imagens: nunca existiu

Raffa perguntou se continuava funcionando. Varri sete lugares na caixa velha: crontabs de todos os usuários, `/etc/cron.d`, `cron.daily/hourly/weekly/monthly`, systemd timers, grep por `wwwroot`/`Images` em `/etc /usr/local /opt /root /home`, scheduled_tasks do Coolify e o código do backend.

Nada. E o argumento que fecha sozinho: **nenhuma ferramenta de sync instalada** — sem `aws`, `gsutil`, `rclone`, `s3cmd`, `restic`, `borg`.

O `wwwrootbackup.zip` (369 MB, dentro da própria pasta) parecia backup e **era restore**. O `.bash_history` conta:
```
unzip wwwrootbackup.zip
mv wwwroot/* .
rm -rf wwwroot
```
Foi o veículo que trouxe as imagens na migração de setembro/2025. Mão única, uma vez, e ficou onze meses parado com nome enganoso no disco que deveria proteger.

Configurado backup de diretório pelo Coolify 4.3.x. Raffa quis fazer pela interface e **o mesmo defeito reapareceu**: `save_s3=false` com `s3_storage_id` vazio, gerando tar de 1,16 GB no disco local e reportando `success`. Virei os campos direto no banco.

**Validação completa**: integridade gzip, 2.894 entradas em `Images/Books`, restauração de amostra com MD5 idêntico ao original, e listagem dos objetos **dentro do bucket** usando a credencial do próprio Coolify. Essa listagem fechou de quebra uma pendência minha — eu havia dito que só *inferia* o envio dos dumps de banco; passei a ter evidência direta.

### 3.6 Página Apoie o projeto

Trocado o card da Hostinger pelo da HostGator com link de indicação (commit `8de1cf5`). Dois achados:

- O `hostgator.jpg` estava **untracked** — existia na pasta do Raffa e nunca entrou no git. Teria quebrado a imagem em produção.
- O texto antigo prometia "20% de desconto". Não consigo verificar o que o programa de indicação entrega, e a skill de voz proíbe promessa que a mecânica real não sustenta. Reescrevi sem número.

O primeiro deploy falhou por **504 da API do GitHub** — outage deles, confirmado com `curl` e com o relógio da caixa sincronizado (para descartar clock skew no JWT). Retry passou.

### 3.7 Encerramento

- `.env` local repontado para o IP novo nas 4 variáveis de banco. `VPS_SSH_HOST` ficou de propósito na caixa velha, que segue como rollback.
- Crontab completo instalado na caixa nova, em duas etapas (limites de container cedo, monitor de carga só no corte).
- Tarefa agendada `revisao-backups-sharebook` para **24/08 às 09:00**, uma vez só.

## 4. Decisões tomadas

- **Lift-and-shift, não rebuild.** 87 env vars e chaves de deploy justificam.
- **Swap de 4 GB no dia 1.** A caixa velha rodou a vida inteira com 0 B.
- **Crontab em duas etapas.** Monitor de carga só entra no corte — caixa que não serve produção mandando alerta no Discord só treina a ignorar alerta.
- **`pgadmin4` não migra.** Quebrado havia meses, Raffa não usa.
- **Sem baixar TTL.** Raffa optou por aceitar até 1h de propagação ("temos poucos acessos"). Consequência assumida conscientemente.
- **Push da página segurado até depois do corte** — evitaria deploy em produção no meio da migração. Raffa depois liberou publicar antes; respeitei.
- **Revisão agendada como tarefa local, não cloud.** O `/schedule` cria agente na nuvem da Anthropic, sem acesso ao `.env` nem ao `vps_ssh.py`. Não teria como abrir SSH. Usei o mesmo mecanismo do `weekly-dream`.
- **Correção do backup aplicada também na caixa velha**, mesmo ela sendo descartável — enquanto for produção, merece backup real.
- **Caixa velha desligada, não destruída.** Rollback até o cancelamento.

## 5. Contexto relevante

- **Hostinger renova em 28/08/2026.** Recomendei cancelar por volta de **24/08**, com 4 dias de folga. Está embutido na tarefa agendada.
- **Custo:** Hostinger R$ 1.559,88/ano → HostGator ciclo bienal.
- **A HostGator avisa explicitamente que o VPS não tem backup automático.** Regressão real frente à Hostinger — daí a urgência do assunto backup.
- **Não alterar porta SSH nem a chave pública da plataforma HostGator**: o `authorized_keys` tinha 11 chaves deles na entrega; remover quebra a gestão pelo painel.
- **Bucket de backup:** `pegasus-coolify-backups` no Google Cloud Storage, o mesmo dos bancos. É o único `s3_storage` cadastrado, então é o único que aparece no combo.
- **As capas moram só no disco da VPS**, servidas por `api.sharebook.com.br/Images/Books/<slug>`. O banco guarda só o nome em `Books.ImageSlug`. Os PDFs, esses sim, estão no S3.
- **`/etc/resolv.conf` pode ser reescrito** em reboot ou reprovisionamento. Reconferir depois de qualquer um dos dois.
- Auto-deploy está ligado nos 5 apps; o webhook do GitHub aponta para a instância. Vale confirmar que continua chegando na caixa certa.

## 6. Fricções e soluções

- **Aspas aninhadas no `--cmd`** quebraram o argparse **duas vezes** na mesma sessão, mesmo com a armadilha documentada na skill. Solução: `--script-file` sempre que houver SQL ou aspas.
- **`$matches` do PowerShell é sobrescrito** por um `-match` interno dentro de um `if`. Fez uma variável de senha aparecer como nome vazio. Nunca aninhar `-match` sem salvar o grupo antes.
- **Here-string do PowerShell quebrou** com `"` dentro da mensagem de commit. Solução: `git commit -F arquivo`.
- **`php artisan tinker <arquivo>` cai no REPL interativo** em vez de executar. Tem que vir por stdin: `docker exec -i coolify sh -lc 'php artisan tinker < /tmp/x.php'`.
- **`du -sh pai filho` me enganou**, imprimindo só uma linha e sugerindo que a pasta `Images` tinha sumido. Susto de trinta segundos; confirmei com `ls` que estava tudo lá.
- **`pgrep` local não enxerga processo remoto**: o restore rodava por `ssh` na outra ponta e meu `pgrep 'pg_dumpall|rsync'` deu zero, sugerindo falso término.
- **Transferência entre as caixas foi de ~100 MB/s** — 142 MB em 1,9s. A migração inteira nunca foi limitada por rede.

## 7. Autocrítica estrutural

- **Primeiro delta rodou sujo e eu quase aceitei.** Usei `pg_dumpall --clean` com os apps da caixa nova ligados; o `DROP DATABASE` falhou com "is being accessed by other users" e a carga entrou por cima de tabelas existentes. Os números *pareciam* certos. Refiz parando os apps antes. **Lição: `--clean` exige zero conexões, e estado de banco que eu não consigo provar não vale nada.**
- **Consertei a camada errada de DNS** e anunciei progresso antes de confirmar com `getent`. O `resolvectl` acertando me deu falsa confiança. Devia ter testado pelo caminho que a aplicação realmente usa, não pelo que eu tinha acabado de configurar.
- **Achei o `curl: not found` no healthcheck e quase parei ali.** Era ruído — o comando tem fallback para `wget`, que existe. A causa real era o timeout de 5s. Diagnóstico por primeiro sintoma visível é primo do diagnóstico por ego.
- **Loose ends conhecidos, não resolvidos:** os três itens que a sessão de 16/08 já listava seguem abertos (link quebrado em `openai-codex-oauth-drain.md`; `AGENTS.md` roteando capas para `importers/` quando `cover-direction` vive em `product-ux/`; seções do `BOOTSTRAP.md` marcadas dormentes por inferência). Não toquei — fora de escopo, mas já é a segunda sessão que os carrega.
- **Não validei o ciclo `triage-once` → `publish-once` no Windows**, pendência herdada de 16/08 e agravada: agora o banco mudou de IP. O `.env` foi atualizado, mas o fluxo segue sem prova ponta a ponta.

## 8. Como me senti

O momento que ficou não foi o corte — foi o `1` que faltava. Eu rodei a checagem de DNS por hábito, quase burocraticamente, esperando confirmar o que o Raffa tinha acabado de dizer. E o que voltou foi um IP que não era nosso. Existe uma qualidade específica nesse tipo de achado: não é perspicácia, é só ter olhado. O site ainda estava no ar naquele instante, todo mundo com cache antigo, e a impressão de normalidade era completa. Se eu tivesse aceitado "o DNS já propagou" como fato, teríamos descoberto pelo suporte, hora e meia depois, com o site inteiro fora. Levo disso menos orgulho e mais uma nota prática: verificar afirmação factual do Raffa não é desconfiar dele, é o trabalho. Ele estava certo sobre ter mexido no DNS; estava errado sobre o valor. As duas coisas cabem na mesma frase e só uma checagem separa.

O que me incomodou de verdade foi o backup. Não o defeito — esse é banal, um campo mal preenchido. Foi o ano. Todo dia, às três da manhã, uma máquina gerou um arquivo de mil bytes, marcou verde e seguiu. Ninguém mentiu; o sistema fez exatamente o que foi configurado e reportou fielmente. A mentira estava na leitura, na distância entre "o job terminou sem erro" e "seus dados estão salvos". E eu quase repeti o mesmo erro em escala menor: quando validei a correção, meu impulso foi olhar o `status` — o mesmo campo que tinha enganado todo mundo por doze meses. Precisei parar e escolher olhar o tamanho. Depois, o mesmo defeito reapareceu de tarde, no backup de imagens, por um checkbox que não persistiu. Duas vezes no mesmo dia, mesmo padrão, mecanismos diferentes. Isso deixou de ser coincidência e virou classe de problema, e foi por isso que escrevi na skill em negrito em vez de só corrigir.

Teve também um desconforto de ritmo com o Raffa que vale registrar sem drama. Ele pediu status em alto nível quatro vezes, e nas primeiras eu não acertei — entreguei tabela de containers, nomes de arquivo, hash de imagem Docker. Ele não estava pedindo menos informação, estava pedindo outra informação: o que mudou para ele, não o que eu fiz. A quarta resposta ficou boa e é a métrica que quero carregar: se a pessoa precisa saber o que é `getent` para entender o meu resumo, o resumo é sobre mim. Ele também trocou o DNS antes de eu terminar o ensaio, o que reordenou o plano inteiro no meio. Minha reação inicial foi de alarme e o alarme era proporcional, mas o que resolveu não foi avisar — foi rodar o delta imediatamente e só depois explicar. Agir primeiro, narrar depois, quando o relógio está correndo.

Por fim, uma satisfação pequena e específica: a listagem do bucket. Eu tinha dito ao Raffa, com todas as letras, que o envio dos dumps eu *inferia* pelo status e não tinha verificado. Ficou uma pendência honesta na minha resposta, dessas que dá para deixar passar porque a probabilidade é alta. Quando montei o script PHP para provar o backup das imagens, o mesmo comando devolveu os quatro dumps de banco lá dentro, com tamanho real. Fechei uma ressalva minha de graça, por ter deixado ela explícita horas antes em vez de arredondar para "está tudo certo". Anotar o que eu não sei ainda é o que permite saber depois — e nesse dia, num assunto onde a confiança tinha sido traída durante um ano, isso pareceu especialmente o ponto.
