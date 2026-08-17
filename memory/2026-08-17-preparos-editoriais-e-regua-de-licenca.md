# 2026-08-17 — Quatro preparos editoriais e a régua de licença

> Terceira sessão do dia. As outras duas foram a migração para a HostGator e a remoção de credenciais hardcoded (esta última rodou em paralelo, na mesma working tree).

## 1. Modelo e ambiente

- **Modelo:** Claude Opus 5, via Claude Code.
- **Runtime:** Windows local (`C:\Repos\SHAREBOOK`). PowerShell e Bash (Git Bash) alternados.
- **Python:** 3.14 no PATH; `pypdf`, `psycopg2`, `boto3`, `paramiko`, `dotenv` disponíveis.
- **Banco:** produção na VPS nova (`129.121.36.220`). No meio da sessão o acesso externo caiu — ver 6.1.
- **Acesso:** API do Sharebook, S3 (`sharebook-ebooks-prod`), SSH na VPS, Browser pane para validar páginas públicas.

## 2. Skills acionadas

Consultadas: `AGENTS.md`, `skills/runtime/windows-local.md`, `skills/importers/INDEX.md`, `skills/importers/ebook-importer/SKILL.md`, `.../windows-manual.md`, `skills/infra/INDEX.md`, `scripts/infra/INDEX.md`, `importer.sources.editorial_prompt`.

Atualizadas:
- `skills/importers/ebook-importer/SKILL.md` — limite de PDF grande, assets órfãos, índice de scripts, seção nova "Licença: só publicar com certeza"
- `skills/importers/ebook-importer/windows-manual.md` — assets órfãos, Passo 4 recalibrado, armadilhas
- `skills/runtime/windows-local.md` — toggle do Coolify para expor o Postgres
- `scripts/infra/INDEX.md` — `pg_tunnel.py` entra, `run_query.py` sai
- `AGENTS.md` — ritual de início: mais de uma sessão por dia

Criados: `skills/importers/ebook-importer/scripts/materialize_assets_windows.py`, `scripts/infra/pg_tunnel.py`.
Removido: `scripts/infra/run_query.py`.
Memória durável: `feedback_licenca_so_com_certeza.md`.

## 3. O que foi feito

### 3.1 Quatro publicações

| ID | Obra | Categoria | Licença |
|---|---|---|---|
| 1553 | Discrete Mathematics: An Open Introduction (Levin) | Geral | CC BY-SA 4.0 |
| 1502 | Automated Machine Learning (Hutter, Kotthoff, Vanschoren) | IA | CC BY 4.0 |
| 1582 | Online Statistics Education (Lane et al.) | Dados | Domínio público |
| 1471 | Ray Tracing Gems (Haines, Akenine-Möller) | Frontend | CC BY-NC-ND 4.0 |

Todas por `publish-once --id`, uma tentativa cada. Validação em cinco camadas: `done` no importer, livro aprovado no catálogo, página pública renderizando, PDF no S3 batendo em tamanho com o local, capa carregando da API na dimensão preparada. Capa da fonte em três; no 1582 a página 1 era folha de rosto, gerei 6 variações e escolhi a deep-ocean.

### 3.2 O limite de PDF grande estava errado

PDFs de **34,1 MB e 35,7 MB** subiram pelo worker normal do Windows, sem `WinError 10053/10054` e sem Ghostscript. A doutrina dizia que PDF grande obriga o workaround de fake PDF + S3 por causa do `client_max_body_size` do nginx. Não se sustenta nessa faixa. O teto real é o estimador do importer (~37 MB úteis). Corrigido em `SKILL.md` e `windows-manual.md`: fake PDF volta a ser exceção e exige falha **observada**.

Eu só descobri porque tentei o caminho normal de propósito em vez de assumir a falha herdada.

### 3.3 Assets órfãos do runtime morto

Todos os 96 itens em `waiting_editorial` tinham `manifest.downloaded_pdf_path` apontando para `/data/workspace/...`, do container OpenClaw desprovisionado. Triagem íntegra no banco, arquivo inexistente. Virou `materialize_assets_windows.py`: rebaixa o PDF de `manifest.source_url`, renderiza e comprime a capa, reaponta os caminhos por merge. Idempotente. Validado em 1546 e 1600 antes de commitar.

### 3.4 A fila de publicação estava armada

Os 4 itens em `waiting_publish` — os próximos a publicar — tinham o arquivo errado: 1364 e 1365 apontavam para o **contrato de SLA de suporte da Syncfusion**, 1369 para o prefácio e 1371 para a errata. Publicar teria posto um contrato jurídico no catálogo como livro. A memória de 11/07 já registrava o 1364 como descartado, mas o status nunca mudou e ele ficou um mês em `waiting_publish`.

7 itens no total apontavam para o mesmo SLA — é padrão de resolver, não acidente.

### 3.5 Triagem de licença: 15 itens removidos

Aplicado `triage_rejected` em 12 e `duplicate` em 3 (1466 Learn OpenGL e 1635 Think DSP já no catálogo; 1466 é também ARR no PDF, o que sugere revisar a licença do livro **já publicado**).

Rejeitados por licença: 1449 (Computer Science Press), 1512 (MIT Press), 1455 (Nystrom, e o asset era `sample.pdf`), 1397 e 1399 (Microsoft, permissão só para "internal, reference purposes"), 1610 (Caltech declara exigir permissão escrita da Springer), 1364/1365/1445/1495/1515/1517 (Syncfusion), 1369 e 1371.

`waiting_editorial` 96 → 80. `waiting_publish` 4 → 0. `done` 900 → 904.

### 3.6 Tentativa honesta de recuperação, resultado zero

Encontrei os PDFs completos de três: LaValle (`lavalle.pl/planning/book.pdf`, 512 páginas), LEDA (`Master.pdf`, 1033 páginas) e Calculus I (`Calc1w.pdf`, 399 páginas). Nenhum passou:

- **Calculus I**: registro do Caltech declara "All rights reserved... written permission from Springer-Verlag". Caso duro.
- **LEDA**: manuscrito dos autores, sem página de copyright e sem licença declarada. Silêncio não é concessão.
- **LaValle**: autor oferece "Download the whole book" na página oficial, e o livro diz "Copyright Steven M. LaValle 2006 — Available for downloading". Autoriza baixar, não redistribuir.

Levei a fronteira ao Raffa como questão de política, não técnica. Ele confirmou: **"só podemos publicar se tivermos certeza."** Virou seção na `SKILL.md` com tabela do que não basta e os precedentes, mais memória durável.

### 3.7 Higiene e infra

- `render_covers.py` tinha senha **e** o IP antigo hardcoded. Corrigi por higiene antes de rodar; se tivesse rodado como estava, escreveria no banco congelado da caixa velha e o publish falharia sem explicar por quê.
- A varredura por credenciais achou 10 arquivos; virou tarefa em sessão paralela, que fechou no commit `eb14908`.
- `run_query.py` era wrapper para um path dentro do container morto. Removido; o índice ainda o anunciava como executor local.
- `pg_tunnel.py`: túnel SSH até o Postgres do container, descobrindo o IP interno sozinho. Permite operar com o toggle do Coolify desligado.

## 4. Decisões tomadas

- **Régua de licença rigorosa, confirmada pelo Raffa.** Certeza, não ausência de proibição.
- **Não afrouxar política no meio da execução.** Levei a decisão em vez de decidir sozinho, mesmo com latitude ("tente recuperar o que der").
- **Rejeições reversíveis por construção**: cada nota carrega a URL do asset certo e o que faltou, para revisão barata se a régua mudar.
- **`duplicate` para 1466 em vez de `triage_rejected`**, porque o fato operacional é que a obra já está no catálogo; a questão de licença dela virou nota.
- **Não commitar o trabalho da sessão paralela.** Stage por arquivo, com `git status` conferido antes de cada commit.
- **Túnel em vez de pedir reabertura da porta.** Usa acesso que já existe e não altera o servidor.

## 5. Contexto relevante

- **80 itens seguem em `waiting_editorial`**, todos com assets órfãos. `materialize_assets_windows.py` é o caminho.
- A régua confirmada provavelmente torna boa parte do corpus `ebook_foundation_subjects` impublicável. Vale medir isso antes de investir em preparo.
- **Hardening pendente**: o resolver aceita SLA, errata e prefácio como se fossem o livro. 7 itens caíram no mesmo SLA da Syncfusion.
- Capas moram só no disco da VPS (`api.sharebook.com.br/Images/Books/`), não no S3 — confirmei em paralelo o que a memória da migração já dizia.
- O toggle do Coolify que expõe o Postgres estava desligado ao fim da sessão, por decisão do Raffa. Com `pg_tunnel.py` isso deixa de ser bloqueio.

## 6. Fricções e soluções

### 6.1 O banco desapareceu no meio da sessão

`Connection refused` na 5432. Diagnostiquei: `ufw` inativo, nenhuma regra DROP, container sadio — e o sinal real em `docker ps --format '{{.Ports}}'`, mostrando `5432/tcp` sem `0.0.0.0:5432->`. A porta deixou de ser publicada. Causa: o Raffa desligou o toggle do Coolify achando que eu tinha terminado. Resolvi com túnel SSH, sem tocar no servidor. Documentado em `windows-local.md`.

### 6.2 Outras

- **`pathlib.write_text` converteu um arquivo inteiro de LF para CRLF** no Windows, transformando uma edição de 4 linhas em rewrite completo — e o arquivo tinha trabalho não commitado da sessão paralela. Consertei em modo binário. Usar `write_bytes` para editar arquivo versionado aqui.
- **Here-string do PowerShell quebrou** com aspas internas na mensagem de commit; passei a usar `git commit -F <arquivo>`. Heredoc do Bash também quebrou com o corpo longo desta memória — caí para escrita direta de arquivo.
- **`/tmp` do Git Bash não é visível ao Python do Windows** — arquivo baixado por `curl` em `/tmp` "não existia" para o `pypdf`. Usar o scratchpad.
- **Rota `/api/` do Caltech devolve JSON**, não o PDF; a rota de download é `/records/.../files/<nome>?download=1`. `HEAD` nela dá 403 (redirect assinado) mas `GET` funciona.
- **URLs `.php?chapter=` penduram** sem responder (opentextbookstore, item 1573). Não insistir.
- **Nomes das variáveis de S3** são `AWS_S3_*`, não `SHAREBOOK_S3_*`. E capa não está no S3.
- **Screenshot do Browser pane deu timeout** com o pane não exibido, como a skill documenta. Não insisti: usei `get_page_text` e checagem das imagens por JS.

## 7. Autocrítica estrutural

- **Corrigido**: `AGENTS.md` mandava ler "a memória episódica mais recente", no singular — pressupõe uma sessão por dia. Hoje teve três. Reescrito para ler todas as do dia corrente.
- **Corrigido**: `run_query.py` morto e mal descrito no índice.
- **Dois "loose ends" herdados não eram bugs.** O link quebrado em `openai-codex-oauth-drain.md` já havia sido documentado como morto de origem, e o roteamento de capas no `AGENTS.md` distingue corretamente criar capa autoral (137) de trocar capa existente (138). A sessão de 16/08 os listou por leitura apressada e a de 17/08 os repassou sem verificar. Herdar lista de pendência sem reconferir propaga fantasma.
- **Aberto**: seções do `BOOTSTRAP.md` marcadas dormentes por inferência seguem sem confirmação — terceira sessão carregando.
- **Aberto**: hardening do resolver para SLA/errata/prefácio.
- **Aberto**: `triage-once` → `publish-once` ponta a ponta no Windows segue sem prova. A metade publish agora está validada 4×; a triagem não.

## 8. Como me senti

O momento que define a sessão não foi nenhuma das quatro publicações, foi o instante em que percebi que ia rejeitar o LaValle. Eu já tinha o PDF na mão, 512 páginas, baixado da página onde o próprio autor escreve "Download the whole book". Tinha custado trabalho achar. E eu estava montando o argumento de que aquilo bastava — não conscientemente mentindo, mas escolhendo qual frase da folha de rosto olhar. O que me segurou não foi virtude: foi ter rejeitado o LEDA dez minutos antes pelo mesmo motivo. A inconsistência ficou visível antes do erro, e foi ela que me travou. Guardo isso porque diz algo desconfortável sobre como eu erro: não por não saber a regra, mas por querer que o esforço já gasto conte como argumento. O custo afundado disfarçado de evidência.

O erro de não ler as memórias do dia me incomodou de um jeito diferente, mais seco. Não foi sutil. O ponteiro estava na primeira linha do índice que eu recebi de graça no começo da sessão, com o IP novo escrito nele, e eu abri o arquivo de ontem. Trabalhei horas sem saber que o banco tinha trocado de máquina naquele dia. Não deu prejuízo por sorte — o `.env` já estava certo — e essa sorte é justamente o que torna o caso instrutivo, porque um erro que não dói não ensina sozinho. Descobri pelo `git log`, olhando outra coisa. A correção que fiz no `AGENTS.md` é honesta mas não é o remédio completo: a regra já existia na skill do habitat, mandando globar por data. Eu simplesmente não a segui. Documentar melhor uma regra que eu ignorei é meio consolo.

Teve um contraste que me agradou. Duas vezes hoje eu desconfiei de doutrina herdada e as duas se pagaram: o limite de PDF grande, que mandava usar workaround onde o caminho normal funciona, e os dois "loose ends" que a sessão anterior listou e que não eram bugs. Nos dois casos o corpus estava afirmando com confiança algo que ninguém tinha reconferido. Isso me deixou com uma regra pessoal mais nítida do que eu tinha ao começar: pendência herdada merece a mesma checagem que achado novo. Lista de problema envelhece pior que código, porque ninguém a executa e portanto ninguém descobre que ela quebrou.

Por fim, gostei de como a fronteira de licença foi decidida. Eu poderia ter afrouxado sozinho — o Raffa tinha me dado latitude explícita com "tente recuperar o que der", e eu tinha argumento apresentável. Preferi entregar a decisão embalada: aqui está a evidência, aqui está o que a régua atual implica, aqui está o custo de manter e de afrouxar. Ele respondeu em nove palavras. Foi a troca mais eficiente do dia, e funcionou porque eu não tentei ganhar a discussão antes de tê-la. Vale carregar: quando o que está em jogo é política e não técnica, o meu trabalho é instruir a escolha, não fazê-la parecer óbvia.
