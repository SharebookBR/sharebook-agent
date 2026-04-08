# Create Book

Skill para transformar um manuscrito em livro apresentável dentro do Sharebook: texto consolidado, capa boa de verdade, edição HTML/CSS elegante e PDF final limpo.

Use esta skill quando a tarefa for criar, diagramar ou fechar um livro digital a partir de material bruto em Markdown, texto corrido ou capítulos soltos.

## Objetivo

Sair com um pacote editorial minimamente publicável:

- manuscrito consolidado
- capa oficial
- HTML do livro
- PDF final
- prompts e artefatos relevantes organizados em `assets/`

## Regra central

Livro bonito não é lugar para improviso técnico feio.

Se houver conflito entre automação total e qualidade visual/editorial, escolher qualidade visual/editorial.

## Fluxo oficial

### 1. Consolidar o texto primeiro

Antes de pensar em PDF, garantir que o manuscrito já existe em um arquivo mestre único.

Formato saudável:

- `nome-do-livro-manuscrito-v1.md`

Regras:

- não diagramar capítulos ainda fragmentados sem costura editorial
- resolver repetição, tom e progressão antes da etapa visual
- PDF não corrige texto frouxo

### 2. Organizar uma pasta de assets

Criar uma pasta simples e previsível:

- `missions/<projeto>/assets/`

Tudo visual relevante deve cair ali:

- capa final
- prompts de capa
- imagens auxiliares aprovadas

Evitar espalhar artefatos por raiz, `tmp` eterno ou pastas inventadas no impulso.

### 3. Capa: usar ChatGPT web como fluxo premium

Decisão consolidada desta skill:

- quando a capa precisar de qualidade real de vitrine, preferir ChatGPT web
- o agente escreve o prompt
- Raffa faz o meio de campo no ChatGPT web
- a imagem final volta para `assets/`

Motivo:

- na prática, a qualidade visual da capa no ChatGPT web ficou superior ao pipeline cru local da API
- insistir na rota mais fraca só porque é mais automática é burrice operacional

Fluxo recomendado:

1. Definir direção visual concreta.
2. Escrever `cover-prompt.txt`.
3. Pedir para Raffa gerar no ChatGPT web.
4. Salvar a capa final em `assets/`.
5. Tratar esse arquivo como source of truth.

Nome saudável:

- `nome-do-livro-capa.png`

### 4. Infográficos e diagramas: default é não usar

Regra consolidada:

- não usar infográficos só porque “ficaria bonito”
- se a peça visual não estiver didaticamente impecável, ela vira passivo de reputação
- livro introdutório com infográfico errado pega mal para a marca

Heurística:

- esquema técnico seco pode existir
- infográfico “bonito” gerado por IA costuma errar em texto, lógica ou consistência
- melhor sem infográfico do que com infográfico bonito e torto

Default saudável:

- livro sai sem infográficos
- só incluir se houver revisão humana pesada e confiança real na correção

### 5. Edição do livro: HTML/CSS antes de PDF

O fluxo saudável para o miolo é:

- Markdown consolidado → HTML/CSS bonito → PDF

Motivo:

- dá controle fino de tipografia, espaçamento, paginação e capa
- permite iterar rápido
- é muito mais amigável do que depender de toolchain pesada tipo LaTeX para este contexto

Padrão visual que funcionou bem:

- formato de página A5
- capa em página própria
- folha de rosto simples
- tipografia clássica para o corpo
- hierarquia limpa de títulos
- muito respiro

### 6. Gerar o PDF com Chrome headless

Fluxo consolidado:

- gerar um HTML final
- imprimir para PDF usando Chrome headless

Mas existe uma armadilha:

- o comando simples de `--print-to-pdf` pode inserir header/footer automático com caminho local e paginação feia

Regra:

- preferir gerar PDF via DevTools do Chrome com `displayHeaderFooter: false`
- não confiar só em flags de CLI se o rodapé lixo continuar aparecendo

Rota operacional recomendada no `sharebook-agent`:

```bash
node scripts/print_pdf_devtools.mjs \
  /data/workspace/sharebook-agent/missions/escrever-livros/<livro>-book.html \
  /data/workspace/sharebook-agent/missions/escrever-livros/<livro>-book-vX.pdf
```

Checklist pós-geração (rápido):

- validar que o PDF não contém `file:///` no texto extraído (`pdftotext ... | grep file:///`)
- abrir páginas de início/meio/fim para confirmar ausência de header/footer automático

### 7. Validar o PDF como produto, não só como arquivo

Checklist mínimo:

- capa correta
- folha de rosto correta
- sem header/footer automático do navegador
- tipografia agradável
- margens coerentes
- capítulos começando em páginas limpas
- nada visualmente quebrado no rodapé
- PDF gostoso de ler, não só tecnicamente gerado

## Estrutura sugerida de arquivos

Exemplo saudável:

```text
missions/
  escrever-livros/
    meu-livro-manuscrito-v1.md
    meu-livro-book.html
    meu-livro-book.pdf
    assets/
      meu-livro-capa.png
      cover-prompt.txt
```

## Anti-padrões

- tentar resolver tudo só com Markdown cru e rezar para o PDF sair bonito
- usar SVG manual para “arte bonita” ou diagrama sedutor
- insistir em infográfico de IA quando a lógica/texto ainda estão tortos
- aceitar capa local pior só porque o pipeline é mais automático
- deixar o PDF final com header/footer de navegador
- tratar arquivo gerado como vitória antes de abrir e olhar

## Heurística de decisão

Quando houver dúvida:

1. O texto já está editorialmente pronto?
2. A capa está realmente forte ou só “ok”?
3. O visual extra ajuda mesmo ou só aumenta risco?
4. O HTML está mais bonito do que a versão anterior?
5. O PDF final parece livro ou parece exportação?

## Frase de bolso

No Sharebook, livro digital bom não nasce de automação cega. Nasce de texto bem costurado, capa forte e PDF limpo.
