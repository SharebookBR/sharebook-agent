# Sharebook Runtime — Windows Local

Regras específicas para quando o Sharebook-agent estiver rodando no ambiente local Windows do Raffa, fora do OpenClaw.

## Quando usar

- No início da sessão, após detectar que o runtime atual é o ambiente local Windows.
- Antes de executar trabalho relevante neste habitat.
- Sempre que houver dúvida sobre caminhos, encoding, limitações de ferramenta, prints ou diferenças de autonomia em relação ao OpenClaw.

## Natureza do habitat

- Ambiente local com acesso a arquivos, ferramentas e interfaces do Windows.
- Pode compartilhar doutrina e memória do Sharebook-agent, mas não deve assumir as mesmas capacidades do OpenClaw.
- Continuidade, autonomia, tooling e background work podem ser diferentes ou mais limitados.

## Regra-mãe

- Não assumir capacidades do OpenClaw neste habitat.
- Detectou Windows local, muda o modo de operação conscientemente.

## Operação prática

- Validar quais ferramentas realmente existem antes de depender delas.
- Preferir fluxo simples, direto e local, sem desenhar automação sofisticada demais só porque ela faria sentido no OpenClaw.
- Se houver limitação real de ambiente, explicitar logo. Não fingir equivalência entre habitats.

## Paths, shell e encoding

- Tratar caminhos Windows como fonte canônica quando o trabalho for local.
- Em PowerShell, não usar `&&`; usar `;` ou chamadas separadas.
- Texto longo ou sinopses com acentos devem ir via arquivo UTF-8, nunca inline na CLI, para evitar quebra de caracteres.
- Prints devem ser buscados no caminho operacional conhecido e copiados para o workspace antes de leitura quando necessário.

## Continuidade e memória

- Compartilhar identidade operacional com o Sharebook-agent, mas sem presumir que toda infraestrutura de memória/recall do OpenClaw existe igual aqui.
- Se a continuidade depender de registro durável, favorecer escrita clara em arquivos canônicos do projeto.
- Não confiar em improviso de sessão para carregar contexto importante entre habitats.

## Validação

- Validar no mundo local real antes de declarar vitória.
- Se uma correção depende de app, shell, arquivo ou UI local, provar no próprio ambiente.
- Não importar confiança do OpenClaw para encobrir falta de validação no Windows.

## Diagnóstico rápido

1. Confirmar shell e ferramenta em uso.
2. Confirmar path real do arquivo ou print.
3. Checar encoding quando texto acentuado quebrar.
4. Evitar assumir que problema é de lógica quando pode ser limitação de habitat.

## Anti-padrões

- Fingir que Windows local tem a mesma autonomia agentica do OpenClaw.
- Transportar playbook de cron, sessões, subagentes ou memória ativa como se fosse universal.
- Usar comandos PowerShell como se fossem shell POSIX.
- Deixar regra específica de Windows poluir a camada genérica do AGENTS.
