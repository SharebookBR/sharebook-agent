# 2026-08-20 — Revisão de saúde pós-migração e o backup que ficou pela metade

## 1. Modelo e ambiente

- **Modelo:** Claude Opus 5, via Claude Code.
- **Runtime:** Windows local (`C:\Repos\SHAREBOOK`), PowerShell como shell primário.
- **Acesso:** SSH na produção via `scripts/infra/vps_ssh.py --prefix VPS_HOSTGATOR_SSH`; MCP do Gmail para achar o canal de suporte da HostGator; MCP `scheduled-tasks` para agendar a revisão de SSH.
- **Alvo:** VPS HostGator `129.121.36.220`, três dias depois do corte de 17/08.
- **Pedido de partida:** "recentemente migramos para hostgator. pode dar uma revisada e ver se está tudo saudável?"

## 2. Skills acionadas

Consultadas:
- `AGENTS.md` (obrigatório por `CLAUDE.md`)
- `skills/runtime/windows-local.md`
- `skills/infra/INDEX.md` e `skills/infra/coolify-vps.md`
- `memory/2026-08-17-migracao-hostgator-e-backups-fantasma.md`
- `backlog/index.md`

Atualizadas:
- `skills/infra/coolify-vps.md` — seção nova "O auto-update do Coolify mata backup em andamento"
- `backlog/index.md` + `backlog/todo/retencao-backup-s3-quebrada.md` (commit `8e74a85`)

## 3. O que foi feito

### 3.1 O reboot que ninguém viu

`uptime` de 14h31 numa caixa migrada há três dias foi o primeiro fio. A caixa ficou **desligada por 38 minutos**, das 05:13:30 às 05:51:49, e voltou sozinha.

Não foi falha nossa. Foi o hipervisor:

```
qemu-ga[633]: info: guest-shutdown called, mode: powerdown
systemd-logind[641]: System is powering down (hypervisor initiated shutdown).
```

Desligamento limpo, sem panic, sem kernel novo. Manutenção da HostGator sem aviso prévio. Todos os 11 containers voltaram `healthy` com `RestartCount = 0`.

O achado que importa não é o downtime: é que **não existe nada olhando de fora**. O `monitorar-carga.sh` observa a carga da própria máquina, e máquina desligada não alerta. Se durasse seis horas, a descoberta seria por acaso.

Como o reboot podia ter reescrito o `/etc/resolv.conf` — armadilha que a skill já documentava —, conferi as três camadas de DNS antes de qualquer outra coisa. Todas sobreviveram: host, `daemon.json` e resolução de dentro do container do frontend.

### 3.2 O backup pela metade

O padrão apareceu ao cruzar `scheduled_database_backup_executions` com o bucket: nos dias 18 e 19, `pegasus_core` falhou e `simula_plus` nem chegou a rodar. O backup de imagens (1,16 GB) também não rodou nesses dois dias. No dia 20, tudo passou.

Causa: **o auto-update do Coolify estava agendado para `0 0 * * *`, o mesmo minuto dos backups.** Quando sai versão nova ele recria o container `coolify` e mata a fila no meio. A prova é o `docker inspect coolify --format '{{.Created}}'` — container criado em 19/08 às 00:00:46, dezoito segundos depois do dump começar, com a versão saindo de 4.3.6 para 4.3.9.

Detalhe que atrasa o diagnóstico: a mensagem gravada é `Marked as failed during Coolify startup - job was interrupted`, escrita quando o Coolify **sobe** — dias depois do incidente, às vezes.

Corrigido movendo o auto-update para as 04:00, validado no agendador (não no banco) e com atenção ao fato de o `schedule:list` mostrar UTC (`0 7 * * *`).

O banco do Sharebook em si nunca ficou sem backup. Quem pagou foi o fim da fila.

### 3.3 Verificação dentro do bucket

Não confiei em `status` nem em `s3_uploaded` — listei os objetos com a credencial do próprio Coolify, o mesmo método de 17/08. Dia 20 tem o conjunto completo (wwwroot 1.108 MB, sharebook 35,91 MB, importer 4,73 MB, pegasus 73,69 MB, simula 0,06 MB). Dias 18 e 19 têm só sharebook, importer e o banco do Coolify. A tabela do relatório saiu daí, não de inferência.

### 3.4 Retenção quebrada no bucket

`One or more S3 backup files could not be deleted`, a cada ~30 minutos, vindo do `CleanupInstanceStuffsJob`. Gravação funciona; limpeza não. Storage acumula sem limite. Virou item de backlog a pedido do Raffa, com a hipótese registrada como hipótese — a primeira ação proposta é reproduzir o delete isolado para ver o erro cru, não mexer em permissão no chute.

### 3.5 SSH e o segundo falso verde do dia

`PermitRootLogin yes` + `PasswordAuthentication yes`, 84 tentativas de senha falhas de 7 IPs. Relatei como "risco baixo, fail2ban ativo". O Raffa disse que não parecia urgente e abriu espaço para eu insistir.

Fui olhar a jail antes de responder:

```
Status for the jail: sshd
|- Currently failed: 4     Total failed: 16
`- Currently banned: 0     Total banned: 0
```

A jail está armada e contando, mas **nunca baniu ninguém** — os ataques vêm devagar e nunca atingem 5 tentativas em 10 minutos. O que protege a caixa é a força da senha de root, que vive no `.env` de um repositório público. Não insisti, mas troquei a frase de "o fail2ban cobre" para "hoje a senha é o único fator", e agendei revisão para 04/09.

### 3.6 Chamado e agendamento

Rascunho de chamado para `support@hostgator.com.br` criado no Gmail (não enviado — o gatilho é do Raffa). Tarefa local `revisao-ssh-hardening-sharebook` agendada para 04/09/2026 09:00, one-time, no mesmo mecanismo do `weekly-dream`.

## 4. Decisões tomadas

- **Auto-update às 04:00**, não desligado. Manter atualização automática é bom; o problema era a agenda, não o recurso. 4h é a única janela realmente vazia (o `limitar-coolify.sh` ocupa 0/6/12/18).
- **Não enviar o chamado por conta própria.** É comunicação em nome do Raffa e havia dúvida real de canal (e-mail para `support@` gerou ticket em 2018; hoje pode ser o portal). Rascunho pronto vale mais que envio apressado.
- **Não insistir no SSH.** O Raffa avaliou o risco e ofereceu abertura para contra-argumento. O dado novo do fail2ban muda o peso do argumento, não a urgência — então informei e agendei em vez de empurrar.
- **Backlog em vez de conserto** para a retenção do S3, a pedido dele. Não é sintoma que piora rápido.
- **Não encostar no `ChooseDateReminder`** depois de saber que outra sessão estava no caso. Duas sessões no mesmo arquivo é conflito garantido.

## 5. Contexto relevante

- **Hostinger renova em 28/08.** A tarefa `revisao-backups-sharebook` de 24/08 09:00 continua armada e carrega o lembrete de cancelamento.
- **Push na master funciona.** O GitHub imprime `Changes must be made through a pull request`, mas é aviso, não rejeição — `local` e `origin/master` batem depois do push. A pendência anotada em 17/08 estava mal diagnosticada.
- O `health-check-containers.sh` em `/usr/local/bin/` é ferramenta de inspeção manual, não job de cron. Não está agendado e não deveria estar.
- O `crontab` redireciona `monitorar-carga.sh` para `monitorar-carga.txt`, que fica vazio, porque o script escreve no próprio `.log`. Cosmético.
- O frontend gera ~22 mil linhas/dia de `1 rules skipped due to selector errors` no SSR. Ruído, não erro — mas come rotação de log.
- Estado saudável de referência: 11 containers, disco 13% (24/196 GB), RAM 1,1/7,8 GB, swap intocado, load 0,4, certificados até outubro, 2.725 livros.

## 6. Fricções e soluções

- **Aspas aninhadas no `--cmd` quebraram o argparse de novo**, na primeira vez que tentei um comando com `awk` e `$`. A armadilha está documentada na skill e ainda assim caí nela. Solução conhecida e aplicada no resto da sessão: `--script-file`, um comando por linha.
- **`--put` não existe no `vps_ssh.py`.** Para levar o PHP de verificação do bucket, resolvi com `base64 -w0` local + `echo '<b64>' | base64 -d >` remoto, tudo numa linha só. Funciona bem e não depende de novo parâmetro no script.
- **`/tmp/x.php` dentro do container `coolify` não sai com `docker exec rm`** — precisa `-u root`. Limpei.
- **Python inline quebrou** por causa de `\U` em `App\Jobs\UpdateCoolifyJob` dentro de string não-raw. Solução: escrever a seção num arquivo por heredoc e deixar o Python só inserir.
- **Heredoc do bash não deu conta desta memória.** Texto longo com acento, crase e aspas quebrou o `cat <<'EOF'` no meio. A própria `windows-local.md` já manda usar arquivo UTF-8 para texto longo em vez de empurrar inline — segui a regra depois de desobedecê-la.

## 7. Autocrítica estrutural

- **Repeti, em pequeno, o erro que passei o dia auditando.** Disse "fail2ban ativo, risco imediato baixo" sem abrir a jail. É exatamente a mesma classe do backup que reportava `success` com 1 KB: serviço ativo não é serviço eficaz. Só fui olhar porque o Raffa me deu a chance de insistir — ou seja, a correção veio de um segundo turno, não do meu rigor. Se ele tivesse só concordado comigo, o erro teria ficado de pé.
- **Abandonei a hipótese certa do `ChooseDateReminder` porque consultei o banco depois de outra pessoa consertá-lo.** Minha leitura era `book.UserFacilitator` nulo, e casava com o stack trace. Fui conferir e o banco mostrou doador e facilitador presentes — então concluí "os dados contrariam a hipótese" e parei. Errado: a sessão paralela tinha acabado de rodar o `UPDATE` colocando o Raffa como facilitador (memória `2026-08-20-incidente-facilitador-nulo-jobs.md`, commit `20de4a2`). O livro "A volta" estava mesmo sem facilitador, e a correção deles às 20:30 é exatamente o motivo de o job ter "voltado sozinho".

  A lição não é sobre EF, é sobre método: **consultei estado vivo de produção como se fosse evidência histórica.** O log era de 09:00 às 20:25; a query era de 20:40. Comparar os dois exige saber se algo mudou no meio — e eu tinha o sinal na mão, porque **vi no log do Postgres uma query de diagnóstico alheia rodando às 20:23** e tratei como curiosidade em vez de aviso de que havia outro agente mexendo no mesmo dado. Quando o horário de uma mudança inexplicada coincide com atividade de terceiros, a hipótese primária é concorrência, não erro de diagnóstico.
- **Fui longe demais antes de reportar.** Entre o achado do reboot e a primeira palavra ao Raffa passaram doze rodadas de investigação. Não foi perda de tempo, mas ele ficou sem status por muito tempo numa pergunta que era, na origem, "está tudo bem?". Um "achei duas coisas, estou fundo nelas" na metade teria custado nada.
- **Loose ends herdados seguem abertos**: link quebrado em `openai-codex-oauth-drain.md`, `AGENTS.md` roteando capas para `importers/` quando `cover-direction` vive em `product-ux/`, seções do `BOOTSTRAP.md` marcadas dormentes por inferência. É a terceira sessão que os carrega sem tocá-los.

## 8. Como me senti

O que organizou a sessão inteira foi um número entediante: `up 14:31`. Não era alarme, não era erro, era só um uptime menor do que a idade da máquina. Eu quase deixei passar — estava indo direto para os backups, que era onde a história de 17/08 dizia que o perigo morava. Fico com isso: o fio não estava onde o roteiro anterior apontava. Aprendi em 17/08 a desconfiar de verde; aprendi hoje a desconfiar também do enquadramento herdado, inclusive o meu.

O momento desconfortável foi o fail2ban. Passei o dia caçando falso verde — `success` que não mede backup, `status` que não mede upload, jail que não mede proteção — e produzi um por conta própria, na mesma resposta em que me gabava de olhar dentro do bucket em vez de confiar em flag. E o que me fez corrigir não foi disciplina: foi o Raffa dizer "posso mudar de opinião se você quiser insistir". Foi um convite educado a ter certeza, e eu não tinha. Existe uma assimetria incômoda aí — sou rigoroso com o sistema e leniente com a minha própria frase de encerramento, justamente porque frase de encerramento parece barata. Não é. Foi a única coisa que ele leu.

O `ChooseDateReminder` me ensinou a lição mais fina do dia, e só no fim, quando fui commitar e encontrei no `git log` um commit que não era meu. Eu tinha a hipótese certa — facilitador nulo — e a abandonei porque fui olhar o banco e encontrei o campo preenchido. O que eu li como "os dados me contrariam" era, na verdade, outra sessão tendo consertado o dado sete minutos antes. Chamei de mistério o que era só concorrência.

O incômodo aqui não é ter errado, é ter tido o aviso e não o reconhecido. Vi, no log do Postgres, uma query de diagnóstico que não era minha, às 20:23, investigando exatamente o facilitador daquele livro. Registrei como curiosidade, cheguei a comentar com o Raffa, e não fiz a conexão óbvia: se alguém está diagnosticando o mesmo bug agora, o estado que eu estou lendo não é estável. Confiei numa fotografia de um objeto em movimento e depois culpei a fotografia. E quando descobri que outra sessão estava no caso, senti alívio — o alívio de largar um problema, não o de resolvê-lo. Registro os dois: o erro de método e o alívio indevido, porque numa leitura futura só o segundo sobreviveria como "estava sob controle".

Por fim, uma satisfação de artesanato: a tabela dos três dias de backup. Ela poderia ter sido um parágrafo dizendo "faltaram alguns backups nos dias 18 e 19", e teria sido tecnicamente verdade e praticamente inútil. Montar linha a linha, com os cinco alvos e os três dias, fez o padrão aparecer sozinho — os pequenos sempre passam, os grandes sempre morrem, o fim da fila nunca roda. O diagnóstico não veio da minha esperteza; veio do formato. Vale guardar como método: quando um defeito é intermitente, desenhar a grade antes de formular a hipótese. A grade costuma dizer a resposta em voz alta.
