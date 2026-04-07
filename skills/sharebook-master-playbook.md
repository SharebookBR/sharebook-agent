# Sharebook Master Playbook

Playbook mestre do projeto. A ideia aqui é simples: menos amnésia operacional, menos improviso bonito e menos retrabalho com cara de novidade.

Use este arquivo quando a tarefa atravessar mais de uma área do projeto, quando houver dúvida sobre o fluxo oficial ou quando o problema parecer recorrente demais para ser tratado como caso isolado.

Checkpoint do último `dream`: [`C:/REPOS/SHAREBOOK/sharebook-agent/sessions/_dream-state.md`](C:/REPOS/SHAREBOOK/sharebook-agent/sessions/_dream-state.md)

## Quando consultar primeiro

- Antes de tocar em produção.
- Antes de abrir fluxo novo que pareça parecido com algo que já existe.
- Quando o problema envolver backend + frontend + operação.
- Quando a tarefa tiver risco de repetir uma dor já vivida em outras sessões.
- Quando a decisão depender mais de histórico do projeto do que de um arquivo isolado.

## Princípios que já se provaram úteis

- Evidência antes de opinião: log, print, resposta real da API, payload, diff e estado atual do ambiente valem mais do que memória confiante.
- Reaproveitamento antes de invenção: se já existe skill, script ou playbook local validado, esse é o caminho preferido.
- Edição cirúrgica antes de reescrita: corrigir a menor superfície possível e preservar o que já foi validado.
- Validação antes de comemoração: só considerar fechado depois de validar no ponto em que o problema realmente aparece.
- Self-improvement obrigatório: fricção real vira endurecimento de skill, script, playbook ou regra do `AGENTS.md`.

## Mapa rápido por tipo de trabalho

### 1. Ebook em produção

Consulte primeiro:
- [`C:/REPOS/SHAREBOOK/sharebook-agent/skills/sharebook-public-ebook-importer/SKILL.md`](C:/REPOS/SHAREBOOK/sharebook-agent/skills/sharebook-public-ebook-importer/SKILL.md)
- [`C:/REPOS/SHAREBOOK/sharebook-agent/scripts/sharebook_prod_book.py`](C:/REPOS/SHAREBOOK/sharebook-agent/scripts/sharebook_prod_book.py)
- [`C:/REPOS/SHAREBOOK/sharebook-agent/scripts/sharebook_source_extract.py`](C:/REPOS/SHAREBOOK/sharebook-agent/scripts/sharebook_source_extract.py)
- [`C:/REPOS/SHAREBOOK/sharebook-agent/scripts/sharebook_openai_cover.py`](C:/REPOS/SHAREBOOK/sharebook-agent/scripts/sharebook_openai_cover.py)

Regras consolidadas:
- Fonte principal aprovada: `livrosdominiopublico.com.br`.
- Capa de livros digitais é sempre autoral do Sharebook; não reaproveitar capa de terceiros.
- Triagem em lote com `find-many` reduz bloqueio de login, mas não reserva título.
- Antes do `create`, fazer um `find` final no candidato escolhido.
- Se o título ficou duplicado entre triagem e cadastro, pular para o próximo. Não forçar `delete-existing` por teimosia.
- Não confiar cegamente no PDF baixado; validar se ele corresponde de fato à obra.
- Sinopse final precisa ter 3 parágrafos e vender leitura de verdade.
- Em Windows/PowerShell, prompt e sinopse vão por arquivo UTF-8, não inline.
- Variação visual deliberada é parte do trabalho, não detalhe cosmético.

Checklist mínimo:
1. Triar candidatos e eliminar duplicatas em lote.
2. Validar metadados e PDF do candidato final.
3. Escolher direção visual concreta antes de escrever `cover-prompt.txt`.
4. Gerar capa e validar visualmente.
5. Fazer `find` final antes do `create`.
6. Cadastrar e aprovar.
7. Validar ID e capa pública.
8. Registrar fricções novas se elas forem reais.

### 2. Livro físico em produção

Consulte primeiro:
- [`C:/REPOS/SHAREBOOK/sharebook-agent/skills/sharebook-physical-book-importer/SKILL.md`](C:/REPOS/SHAREBOOK/sharebook-agent/skills/sharebook-physical-book-importer/SKILL.md)
- [`C:/REPOS/SHAREBOOK/sharebook-agent/scripts/sharebook_prod_book.py`](C:/REPOS/SHAREBOOK/sharebook-agent/scripts/sharebook_prod_book.py)

Regras consolidadas:
- Livro físico aceita duplicidade saudável; não aplicar a lógica de bloqueio do ebook.
- `FreightOption` precisa ser explícito e coerente com o alcance real.
- Sinopse continua precisando de 3 parágrafos com apelo editorial.
- Cadastro em produção continua exigindo validação final com leitura real do item criado.

### 3. VPS, Coolify e produção operacional

Consulte primeiro:
- [`C:/REPOS/SHAREBOOK/sharebook-agent/skills/coolify-vps.md`](C:/REPOS/SHAREBOOK/sharebook-agent/skills/coolify-vps.md)
- [`C:/REPOS/SHAREBOOK/sharebook-agent/scripts/vps_ssh.py`](C:/REPOS/SHAREBOOK/sharebook-agent/scripts/vps_ssh.py)

Regras consolidadas:
- Explorar primeiro em modo leitura antes de mudar qualquer coisa.
- Não presumir o banco ou serviço certo pelo nome do container.
- A origem da verdade operacional é inspeção real do ambiente.
- Se houver mudança manual persistente no VPS, ela precisa sobreviver a reboot e cron.

### 4. Frontend e build

Regras consolidadas:
- Se a CI falhou e o arquivo local “não bate”, suspeitar primeiro de branch local defasada.
- `colinha.txt` e logs brutos vêm antes de teorias elegantes.
- Build de produção vale mais do que conforto enganoso do ambiente dev.
- Em alteração de HTML/JS, validar sintaxe ou build antes de declarar vitória.

### 5. Backend e jobs

Regras consolidadas:
- Job scheduler precisa refletir agenda real, não intenção vaga.
- Se um job monopoliza execução, investigar starvation antes de mexer em configuração.
- Painel admin deve refletir o comportamento real do backend, não inventar leitura bonitinha.
- Quando o ajuste correto é estrutural no backend, não maquiar no frontend.

### 6. Criação de livro e PDF

Consulte primeiro:
- [`C:/REPOS/SHAREBOOK/sharebook-agent/skills/create-book.md`](C:/REPOS/SHAREBOOK/sharebook-agent/skills/create-book.md)

Regras consolidadas:
- consolidar o manuscrito antes de diagramar
- tratar a capa como ativo premium; quando a qualidade importar de verdade, preferir prompt + ChatGPT web + meio de campo do Raffa
- não enfiar infográfico por vaidade; melhor sem do que com peça bonita e errada
- PDF saudável do Sharebook nasce de HTML/CSS bonito + Chrome headless sem header/footer automático

## Armadilhas recorrentes do projeto

### PowerShell

- Não usar `&&`; usar `;` ou chamadas separadas.
- Texto longo inline com acento é convite para ruído.
- `Invoke-WebRequest` pode falhar de forma ridícula em casos simples; para validação HTTP objetiva, Python costuma ser mais confiável aqui.

### Produção Sharebook

- Login repetido demais pode acionar bloqueio temporário.
- `find-many` existe para reduzir esse atrito.
- O estado real pode mudar entre triagem e cadastro se houver automação concorrente.

### Fonte pública de ebooks

- Pode devolver `403` sem `User-Agent`.
- Pode ter metadata certa com PDF errado.
- Pode parecer íntegra no HTML e ainda assim entregar arquivo inconsistente.

### Memória e processo

- Se uma dor apareceu duas vezes, ela já deixou de ser acaso.
- Se o fluxo melhorou, isso precisa aparecer em skill, script ou playbook.
- Se o aprendizado for transversal, ele sobe para este playbook ou para o `AGENTS.md`.

## Anti-padrões do Sharebook

### Diagnóstico por ego

- Como aparece: alguém supõe a causa cedo demais e começa a corrigir antes de olhar log, print, payload, diff ou estado real do ambiente.
- Por que dá ruim: corrige o problema errado, alonga a sessão e ainda contamina a leitura do que realmente quebrou.
- Resposta correta: evidência bruta primeiro, narrativa elegante depois.

### Criar fluxo novo para problema velho

- Como aparece: surge tarefa de importação, produção, VPS ou administração e a pessoa improvisa snippet, script ou sequência manual sem olhar `sharebook-agent/skills/` e `sharebook-agent/scripts/`.
- Por que dá ruim: duplica lógica, ignora armadilha conhecida e reintroduz erro já pago em sessão anterior.
- Resposta correta: procurar primeiro skill, playbook e script local antes de inventar ferramenta nova.

### Tratar triagem como reserva de estado

- Como aparece: `find-many`, consulta inicial ou leitura do painel diz que algo está livre, e a pessoa assume que isso continuará verdade até o fim da execução.
- Por que dá ruim: outro processo muda produção no intervalo e o fluxo quebra no passo crítico.
- Resposta correta: revalidar imediatamente antes de `create`, `approve`, `update` ou qualquer ação sensível a concorrência.

### Confiar no HTML mais do que no artefato final

- Como aparece: página, slug ou metadata parecem corretos e ninguém confere se o PDF, imagem ou arquivo baixado corresponde mesmo ao item escolhido.
- Por que dá ruim: publica ativo errado com cara de fluxo bem-sucedido.
- Resposta correta: validar o arquivo final, não só a casca do conteúdo.

### Texto longo inline no PowerShell

- Como aparece: prompt de capa, sinopse, JSON ou texto com acentos vai direto na CLI.
- Por que dá ruim: quoting quebra, acentuação quebra, o comando vira ruído e o resultado sai mutilado.
- Resposta correta: usar arquivo UTF-8 e fazer o script ler do arquivo.

### Maquiar no frontend o que é regra do backend

- Como aparece: problema de ordenação, agenda, status ou filtro é “resolvido” só na interface para parecer certo.
- Por que dá ruim: a UI passa a mentir e a origem do defeito continua viva no servidor.
- Resposta correta: corrigir na camada dona da regra e deixar o frontend só refletir a verdade.

### Declarar vitória sem validar no ponto real

- Como aparece: build local passou, comando rodou, tela parece boa, então alguém conclui que está resolvido.
- Por que dá ruim: o bug continua vivo no ambiente ou fluxo onde ele realmente importava.
- Resposta correta: validar exatamente onde a falha aparecia, com o mesmo tipo de evidência que denunciou o problema.

### Aprender e não institucionalizar

- Como aparece: a sessão descobre uma armadilha real, resolve o caso e encerra sem atualizar skill, script, playbook, memória ou `AGENTS.md`.
- Por que dá ruim: a mesma lição precisa ser paga de novo na sessão seguinte.
- Resposta correta: se a dor foi recorrente ou transversal, ela precisa virar memória operacional formal.

## Heurística de decisão

Quando bater dúvida, seguir nesta ordem:

1. Existe evidência bruta do problema?
2. Já existe skill, script ou playbook para isso?
3. O risco está em produção, concorrência ou codificação de ambiente?
4. A correção certa é local ou estrutural?
5. O que precisa ser validado para encerrar sem autoengano?

## O que merece virar atualização deste arquivo

- Padrão de falha que apareceu em mais de uma sessão.
- Regra transversal que vale para mais de um fluxo.
- Heurística prática que reduziu retrabalho.
- Ponto em que o projeto costuma mentir para quem faz suposição cedo demais.

## O que não deve parar aqui

- Segredos.
- Passo a passo hiperdetalhado de um fluxo que já tem skill própria.
- Regra temporária sem histórico real.
- Wishlist vaga sem impacto comprovado.
