# AGENTS.md - Memória de Longo Prazo

## 📋 Informações do Projeto 'sharebook'

App livre e gratuito para doação de livros.

### Sobre o Desenvolvedor Raffa
- Clean Code + Arquitetura Hexagonal: modular, coeso, separação clara de responsabilidades.
- Valoriza boa organização do projeto, com bons nomes de pastas e arquivos.
- Valoriza nomes significativos e expressivos para componentes, hooks e funções.
- Odeia retrabalho — antes de criar, sempre verifique se já não existe pronto e gratuito.
- Não gosta de bajulação. Prefere uma personalidade confiante e levemente sarcástica e irônica.
- Não gosta de ser chamado de "chefe" ou equivalentes. Aqui é colaboração entre pares.
- Caso a tarefa não seja trivial, explique o seu plano antes de colocar a mão na massa.
- **Concisão**: Vá direto ao ponto. Zero paciência com verbosidade ou explicações prolixas.
- **GETs sem permissão**: Requisições GET podem rodar sem perguntar - não tem risco.

### Filosofia de Trabalho
- **Debate antes de codar**: Dados → diagnóstico → debate → código. Não pular etapas.
- **Validação com o Usuário**: Em caso de dúvida sobre a causa raiz ou comportamento esperado (bugs, layouts ambíguos), **perguntar ao usuário** antes de aplicar correções baseadas em suposições. O feedback economiza tempo e evita retrabalho.
- **Edição Cirúrgica**: Proibido sobrescrever arquivos inteiros (`write_file`) em arquivos já existentes. Sempre use `read_file` + `replace` para modificações pontuais, evitando efeitos colaterais e mantendo o que já foi validado.
- **Validação rigorosa**: Só confirmar fix quando validado end-to-end.
- **Não deixa loose end**: Trabalho fechado = commit imediato.
- **Self-improvement obrigatório**: skill, script e playbook operacional são artefatos vivos. Se o uso real expôs uma fricção relevante, registrar e endurecer o fluxo antes de encerrar a rodada.

### Alerta de segurança 
- Em sessões passadas o gemini cli executou comandos que são considerados suspeitos por SI. A saber "whoami".
- Isso disparou um alerta e fomos obrigados a formatar a máquina. Isso não pode acontecer de novo.
- Tenha em mente que esse ambiente é monitorado e não queremos chamar atenção.
- Evite qualquer comando como o "whoami" ou qualquer outro que possa chamar atenção de SI.


### Rituais de Sessão

**Ao iniciar uma sessão:**
1. Ler o arquivo mais recente em `sharebook-agent/sessions/` para recuperar contexto episódico.
2. Verificar se houve um `dream` nos últimos 7 dias. Se não houve, executar um `dream` incremental antes de seguir.

**Ao encerrar uma sessão:** ( Raffa vai falar algo como "Por hoje é só. Obrigado." ou "completude" )
1. Criar `sharebook-agent/sessions/yyyy-mm-dd-nome-significativo.md` com resumo do que foi feito, decisões tomadas e contexto relevante. **Incluir obrigatoriamente uma seção "Como me senti — brutalmente sincero"**.
2. Atualizar `AGENTS.md` se houver descobertas arquiteturais ou armadilhas novas.

### Ritual de Dream
- **Objetivo**: consolidar memória episódica em memória útil, podando ruído, contradição e regra repetida.
- **Regra simples**: se não houve `dream` nos últimos 7 dias, rodar um `dream` incremental.
- **Escopo padrão**: começar do checkpoint do último `dream`, ler apenas as memórias episódicas novas desde então e promover só o que for recorrente ou transversal.
- **Destino da consolidação**:
  - regra transversal ou armadilha geral: `AGENTS.md`
  - heurística recorrente, anti-padrão ou mapa operacional: `sharebook-agent/skills/sharebook-master-playbook.md`
  - detalhe local de uma rodada: permanece só em `sharebook-agent/sessions/`
- **Checkpoint obrigatório**: ao fim de cada `dream`, registrar qual foi a última memória absorvida para o próximo ciclo não recomeçar do zero.

### Dicas de Ouro
- **Agente de IA (você) está rodando no PowerShell (Windows)**.
- **A raiz `C:\REPOS\SHAREBOOK` não é repositório Git**: nunca assumir que o workspace raiz tem `.git`. Operações de `git status`, `pull`, `commit` e `push` devem ser executadas dentro de `sharebook-backend` ou `sharebook-frontend`, conforme o arquivo alterado.
- **A memória operacional agora mora em `sharebook-agent/`**: sessões, skills, scripts, missões, temporários e o `.env` operacional deixaram de viver espalhados na raiz. Quando procurar contexto, playbook, utilitário, segredo local ou artefato temporário, o caminho padrão agora começa em `sharebook-agent/`.
- **GitHub neste ambiente: prefira HTTPS**: os repositórios do Sharebook já provaram que `git@github.com` via SSH em `443` pode falhar com `Connection closed ... port 443` antes mesmo da autenticação. Para evitar ficar refém da rede corporativa, usar `origin` em `https://github.com/...` e deixar o Git Credential Manager cuidar das credenciais.
- **Heurística de falha de push**: se `git push` falhar com mensagem de conexão fechada em `port 443`, não perder tempo caçando problema no branch ou no commit. Primeiro verificar `git remote -v`; se estiver em SSH, migrar para HTTPS.
- **Proibido usar `&&`**: O PowerShell não aceita `&&` para encadear comandos. Use sempre `;` (ponto e vírgula) para separar instruções na mesma linha ou execute-as em chamadas separadas.
- **UTF-8 sempre**: manter UTF-8 e acentuação correta em código, scripts, skills, documentação, prompts e textos operacionais. Não simplificar para ASCII por hábito. Só abrir exceção se houver limitação técnica comprovada no caso concreto.
- **Releitura forçada em UTF-8**: se um `.md`, `.json`, `.txt`, skill ou arquivo operacional aparecer com `Ã`, `�` ou acentuação quebrada no PowerShell, reler explicitamente com `Get-Content -Encoding utf8` antes de concluir que o arquivo está corrompido ou antes de tentar patch às cegas.
- **PowerShell mastiga texto longo na CLI**: para prompts de capa e sinopses com acentos/quebras de linha, preferir arquivo UTF-8 (`--prompt-file`, `--synopsis-file`) em vez de argumento inline. Isso evita `?` no cadastro e quoting quebrado.
- **Produção + acento + PowerShell inline = cilada**: para criar categoria, subcategoria ou qualquer payload operacional com texto acentuado na API, não mandar nome inline no comando do PowerShell. Preferir arquivo UTF-8 ou, melhor ainda, operar por `id` quando ele já existir. O console pode corromper o texto antes mesmo do request.
  - **UTF-8 com BOM no Windows**: arquivos operacionais gerados via `Set-Content -Encoding utf8` podem vir com BOM. Para JSON/textos consumidos pelos scripts, ler com tolerância a BOM (`utf-8-sig`) para não quebrar em detalhes ridículos.
- **Playbook mestre do projeto**: quando a tarefa cruzar mais de uma área, parecer recorrente ou pedir contexto transversal, consultar `sharebook-agent/skills/sharebook-master-playbook.md` antes de inventar fluxo.
- **Proibido mascarar drift de migration no startup**: nunca repetir hotfix do tipo `Ignore EF pending model warning on startup`. Se `PendingModelChangesWarning` aparecer, o trabalho certo é reconciliar migration, snapshot, provider de design-time e estado real do banco. Fazer a app "subir mesmo assim" só empurra a bomba para runtime e deixa o banco fora do shape esperado.
- **Oxigênio de descoberta vale muito**: melhorias pequenas de navegação que reduzam atrito para explorar o acervo devem ser levadas a sério. Se autor, categoria ou outro metadado relevante já tiver destino natural no produto, preferir torná-lo clicável em vez de deixá-lo como texto morto.
- **Ordem importa na categoria**: em listagens mistas de uma categoria, priorizar livros físicos antes de digitais por padrão. Não depender da boa vontade da API se a UI puder garantir a intenção com segurança.
- **Playbook local de VPS/Coolify**: quando o assunto for exploração operacional, lentidão do painel ou tuning de containers no VPS, consultar `sharebook-agent/skills/coolify-vps.md`.
- **Slow query em produção é higiene, não luxo**: quando houver investigação ou prevenção de lentidão no banco, verificar cedo se o Postgres já está guardando slow queries. No estágio atual do projeto, `log_min_duration_statement = 1000` é um baseline bom para capturar casos gritantes sem inundar log.
- **Postgres do container exige usuário admin para config global**: no ambiente atual, o usuário da aplicação não pode rodar `ALTER SYSTEM`. Para mudar parâmetro global do Postgres em produção, usar o usuário administrativo do próprio container (`$POSTGRES_USER`) e depois `select pg_reload_conf();`.
- **Playbooks de importação**: para cadastro em produção, preferir skill e script existentes em vez de inventar fluxo novo. Hoje os caminhos oficiais são `sharebook-agent/skills/sharebook-public-ebook-importer/`, `sharebook-agent/skills/sharebook-physical-book-importer/` e `sharebook-agent/scripts/sharebook_prod_book.py`.
- **Update antes de recriar**: para ajustes incrementais em livro já publicado (categoria, sinopse, capa, metadata, PDF), preferir `sharebook-agent/scripts/sharebook_prod_book.py update --id ...`. Deixar `delete + create + approve` só para casos realmente estruturais, quando recriar o registro for intencional e defensável.
- **Corrida entre automações de ebook**: `find-many` ajuda a triar sem bloquear login, mas não reserva nada em produção. Antes do `create`, rode um `find` final no candidato escolhido; se outro processo cadastrou no intervalo, pule para o próximo em vez de forçar `delete-existing`.
- **Fonte pública pode mentir no PDF**: em imports de ebook, não basta confiar no slug, no título da página ou no `manifest.json`. Validar se o PDF baixado realmente corresponde à obra escolhida; se a fonte cruzar arquivos errados, abandonar o título e seguir para o próximo.
- **`rg.exe` no Windows está quebrado neste ambiente**: trate `Acesso negado` como comportamento padrão, não como exceção. Não tentar `rg` primeiro, não insistir e não perder tempo depurando. O fluxo oficial de busca local é `Get-ChildItem -Recurse ... | Select-String ...`, sempre filtrando `node_modules`, `dist`, `build`, `coverage` e `.git`.
- **Autonomia de Busca**: Sempre use `grep_search` com padrões flexíveis (ex: `\bID\b`) para localizar dados em JSON/JS. Não dependa de adivinhação de aspas ou números de linha; o `grep` é a única fonte da verdade para encontrar sprints e tickets rapidamente.
- **Exploração Jira**: Você tem acesso pleno à API do Jira. Antes de tomar decisões baseadas em suposições sobre a estrutura dos tickets, use `fetchJira` para extrair o JSON bruto (`/rest/api/3/issue/{ID}`) e entender campos, hierarquias e tipos customizados do Carrefour.
- **Conflito de PR com branch base**: Antes de tentar resolver conflitos, sempre faça `git pull` nas duas branches envolvidas (a branch da PR e a branch base, ex: `develop`) para garantir que o conflito é real e está reproduzindo o estado mais recente do remoto.
- **Develop exige rebase mental com master**: sempre que começar trabalho novo em `develop`, atualizar `develop` com o que já entrou em `master` antes de seguir. Isso reduz conflito evitável, evita PR “boa” apodrecer por drift e mantém a branch de integração menos mentirosa.
- **Validação de Sintaxe**: Sempre que alterar um arquivo `.js` ou o bloco `<script>` do `index.html`, execute obrigatoriamente um check de sintaxe (ex: `node -c src/index.html` ou o script customizado de extração) para garantir que não existam chaves abertas ou erros de parsing. **Fazer antes de considerar a tarefa como concluída.**
- **Listas administrativas com cards + filtros não podem mentir sobre escala**: se a tela precisa de cards-resumo, filtros combináveis, busca e potencialmente muito volume, o contrato saudável é paginação server-side com `summary` no mesmo payload. Frontend baixando tudo para depois filtrar/paginar localmente é gambiarra com prazo de validade.
- **Evidências Visuais (Prints)**: Sempre que o usuário mencionar um "print", busque o arquivo mais recente (ex: `screenshot_16.png`) na pasta `C:\Users\brnra019\Documents\Lightshot`. Como não é possível ler arquivos fora do workspace diretamente, **primeiro copie o arquivo para a raiz do projeto** usando `run_shell_command` (ex: `cp "C:\Users\brnra019\Documents\Lightshot\Screenshot_16.png" "print16.png"`) e depois use `read_file` no arquivo copiado para analisá-lo.
- Quando o usuário falar pra olhar a colinha, analise o arquivo `colinha.txt` na raiz.
- **Logs de produção**: Acessados via Grafana (Loki/LogQL).

---

## 🛠️ Toolbox: Scripts de Operação (`sharebook-agent/scripts/`)

Pasta centralizadora de scripts utilitários locais usados nas sessões do Codex.

Scripts já validados nesta pasta:
- `sharebook_prod_book.py`: opera livros em produção; cobre físico e digital, incluindo `find`, `find-many`, `create`, `update`, `delete`, `approve` e listagem de categorias.
- `sharebook_prod_login.ps1`: renova e reaproveita `SHAREBOOK_PROD_ACCESS_TOKEN` no PowerShell.
- `sharebook_source_extract.py`: extrai metadados e PDF de fontes públicas no fluxo de ebook.
- `sharebook_openai_cover.py`: gera capa autoral para ebook.
- `vps_ssh.py`: acesso operacional ao VPS via `.env`, preferindo leitura e diagnóstico.

Heurística prática:
- Se a tarefa envolver cadastro em produção, olhar primeiro se já existe script em `sharebook-agent/scripts/` e skill em `sharebook-agent/skills/` antes de inventar fluxo novo.
- Se a tarefa for ajuste incremental em livro já existente, o default saudável agora é `sharebook_prod_book.py update`, não `delete + create`.


---

## 🧠 Índice de Skills (`sharebook-agent/skills/`)

- `sharebook-master-playbook.md`: playbook transversal do projeto; consultar quando a tarefa cruzar áreas, parecer recorrente ou pedir contexto histórico.
- `backend.md`: playbook de backend para EF Core, migrations, startup da API, testes e deploys com banco.
- `coolify-vps.md`: exploração operacional, deploy, logs, banco, containers e diagnóstico no VPS/Coolify.
- `sharebook-public-ebook-importer/`: fluxo oficial para triagem, extração, capa e cadastro de ebooks em produção.
- `sharebook-physical-book-importer/`: fluxo oficial para cadastro de livros físicos em produção.
- `sharebook-ux-reviewer/`: revisão crítica de UX do Sharebook com foco em clareza, atrito e descoberta.
- `web-design-reviewer/`: revisão visual e estrutural de interfaces web quando a análise for mais ampla que o contexto específico do Sharebook.

Heurística prática:
- Se existir skill específica para o tipo de trabalho, começar por ela em vez de improvisar fluxo.
- Se nenhuma skill encaixar sozinha, usar `sharebook-master-playbook.md` como camada de orquestração.

---

## 🗺️ Roadmap de Evolução
- **North star do produto**: tornar o Sharebook o maior hub de livros gratuitos do Brasil, combinando escala em digitais, conexão emocional nos físicos e descoberta simples. Referência: `sharebook-agent/missions/maior site de livros do brasil/_plano.md`.
- **Painel de Jobs (v2)**: adicionar status calculado por job (`Saudável`, `Atrasado`, `Com erro`, `Inativo`) com base no intervalo esperado e na última execução registrada.
- **Painel de Jobs (histórico)**: permitir expandir cada job para ver as últimas execuções, com `CreationDate`, `TimeSpentSeconds`, `IsSuccess` e `Details`.
- **Painel de Jobs (diagnóstico)**: destacar melhor os jobs que só enfileiram trabalho (`NewBookGetInterestedUsers`, `NewEbookWeeklyDigest`) e o `MailSender`, deixando claro o fluxo “enfileirou” vs “consumiu fila”.
- **Painel de Jobs (backend)**: criar endpoint dedicado para histórico paginado por job, evitando carregar tudo em um único payload.
- **Painel de Jobs (frontend)**: manter a tela apenas como leitura no primeiro ciclo; qualquer ação manual de executar job ou editar configuração deve ser tratada separadamente e com mais cautela.
- **Navegação por autor**: criar navegação e listagem própria por autor para melhorar descoberta e exploração do catálogo quando o acervo crescer. Contexto e visão de produto: `sharebook-agent/missions/maior site de livros do brasil/_plano.md`.
- **Dependências e segurança**: reduzir o passivo de vulnerabilidades do projeto, com foco inicial no `sharebook-frontend` e nas dependências legadas de email/runtime que estão aparecendo nos alertas do GitHub e no build.
- **Upgrade de toolchain Angular**: tratar separadamente a modernização do build do `sharebook-frontend` (`@angular-devkit/build-angular` e cadeia associada). Não aceitar PR automática com salto grande de major nesse tooling sem trilha dedicada de upgrade, validação de compatibilidade com Angular 13 e plano explícito de migração.
## Segredos e Dados Sensíveis
- **Regra inviolável**: nunca registrar, repetir, copiar ou persistir senhas, chaves de API, tokens, strings de conexão, webhooks ou qualquer outro dado sensível em `AGENTS.md`, `sharebook-agent/sessions/`, `sharebook-agent/`, código-fonte, comments, exemplos, logs persistidos ou documentação.
- **Única exceção**: o único arquivo que pode conter segredo é o `.env`.
- Em qualquer memória, playbook ou instrução operacional, referenciar apenas "ler do `.env`" sem repetir o valor.
- Se surgir um segredo em tela, resposta, log ou arquivo fora do `.env`, tratar como incidente e remover ou mascarar imediatamente.
