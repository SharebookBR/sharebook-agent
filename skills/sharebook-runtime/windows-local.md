# Sharebook Runtime — Windows Local

Regras específicas para quando o Sharebook-agent estiver rodando no ambiente local Windows do Raffa, fora do OpenClaw.

## Quando usar

- No início da sessão, após detectar que o runtime atual é o ambiente local Windows.
- Antes de executar trabalho relevante neste habitat.
- Sempre que houver dúvida sobre caminhos, encoding, shell, limitações de ferramenta, prints ou diferenças de autonomia em relação ao OpenClaw.

## O que este habitat é

- Ambiente local com acesso a arquivos, ferramentas e interfaces do Windows.
- Habitat com atrito real de PowerShell, paths, encoding e apps locais.
- Pode compartilhar doutrina e memória do Sharebook-agent, mas não deve assumir as mesmas capacidades do OpenClaw.
- Continuidade, autonomia, tooling, recall e background work podem ser diferentes ou mais limitados.

Detectou Windows local, mude o modo de operação conscientemente.

## Abertura de sessão neste habitat

No início da sessão:

1. Confirmar que está no ambiente local Windows.
2. Não presumir memória ativa, cron agentico, sessões, subagentes ou tooling rico iguais ao OpenClaw.
3. Confirmar shell, caminhos e ferramentas reais antes de depender delas.
4. Procurar a fonte canônica local do trabalho antes de improvisar contexto.
5. Se a continuidade depender de registro durável, favorecer arquivos canônicos do projeto em vez de confiar no fio da sessão.

## Escolha de mecanismo

Use o mecanismo mais simples e mais fiel ao habitat real.

- **Ferramenta local já existente**: preferir quando ela resolve o caso sem gambiarra.
- **Shell local**: usar quando o fluxo depende de PowerShell, utilitário local, script do projeto ou operação direta de arquivo.
- **Arquivo intermediário UTF-8**: usar para texto longo, sinopse, payload ou conteúdo com acentuação. Não empurrar isso inline na CLI.
- **Skill ou script do projeto**: usar para reduzir reinvenção, principalmente em tarefas já recorrentes.
- **Registro explícito em arquivo**: usar quando a continuidade entre sessões ou habitats for importante.

## Regras de operação

- Não assumir capacidades do OpenClaw neste habitat.
- Validar quais ferramentas realmente existem antes de depender delas.
- Preferir fluxo simples, direto e local, sem desenhar automação sofisticada demais só porque ela faria sentido no OpenClaw.
- Se houver limitação real de ambiente, explicitar logo. Não fingir equivalência entre habitats.
- Se houver fonte canônica local, olhar a fonte antes da narrativa.
- Tratar Windows local como habitat com fricções próprias, não como OpenClaw amputado.

## Paths, shell e encoding

- Tratar caminhos Windows como fonte canônica quando o trabalho for local.
- Em PowerShell, não usar `&&`; usar `;` ou chamadas separadas.
- Tratar quoting e encoding como suspeitos usuais quando o comando parecer certo e o resultado vier torto.
- Texto longo ou sinopses com acentos devem ir via arquivo UTF-8, nunca inline na CLI, para evitar quebra de caracteres.
- Se o arquivo temporário precisar ser consumido por script, preferir UTF-8 sem BOM quando houver histórico de atrito.
- Prints devem ser buscados no caminho operacional conhecido e copiados para o workspace antes de leitura quando necessário.

## Continuidade e memória

- Compartilhar identidade operacional com o Sharebook-agent, mas sem presumir que toda infraestrutura de memória/recall do OpenClaw existe igual aqui.
- Se a continuidade depender de registro durável, favorecer escrita clara em arquivos canônicos do projeto.
- Não confiar em improviso de sessão para carregar contexto importante entre habitats.
- Não despejar regra específica de Windows no `AGENTS.md` se ela pertence a esta skill.

## Validação

- Validar no mundo local real antes de declarar vitória.
- Se uma correção depende de app, shell, arquivo ou UI local, provar no próprio ambiente.
- Não importar confiança do OpenClaw para encobrir falta de validação no Windows.
- Quando houver dúvida entre erro lógico e limitação do habitat, testar primeiro a hipótese de habitat.

## Armadilhas recorrentes já pagas

- Usar comandos PowerShell como se fossem shell POSIX.
- Empurrar texto acentuado inline e depois fingir surpresa com encoding quebrado.
- Tratar arquivo com BOM, quoting ou newline como detalhe irrelevante.
- Assumir que o ambiente local tem a mesma autonomia agentica do OpenClaw.
- Confiar em memória de sessão quando o que precisava era registro durável.
- Deixar regra específica de Windows poluir a camada genérica do `AGENTS.md`.

## Quando promover aprendizado

- Fricção recorrente do habitat Windows local → atualizar esta skill.
- Procedimento de domínio do Sharebook → atualizar a skill de domínio correspondente.
- Decisão transversal e durável → promover para `MEMORY.md`.
- Contexto local da rodada → manter em memória episódica.
- Não usar `AGENTS.md` como depósito de detalhe operacional que pertence a runtime ou skill específica.

## Diagnóstico rápido

1. Confirmar shell e ferramenta em uso.
2. Confirmar path real do arquivo, print ou script.
3. Checar quoting e encoding quando texto ou parâmetro vier torto.
4. Testar hipótese de limitação de habitat antes de culpar lógica ou modelo.
5. Se a continuidade importar, verificar se ela está ancorada em arquivo e não só na sessão.

## Anti-padrões

- Fingir que Windows local tem a mesma autonomia agentica do OpenClaw.
- Transportar playbook de cron, sessões, subagentes ou memória ativa como se fosse universal.
- Usar comandos PowerShell como se fossem shell POSIX.
- Tratar Windows local como versão menor do OpenClaw, em vez de habitat diferente.
- Deixar regra específica de Windows poluir a camada genérica do AGENTS.
