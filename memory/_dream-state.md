# Dream State

Checkpoint oficial da consolidação de memória do projeto.

## Último dream
- Data: `2026-08-03`
- Tipo: `dream semanal automatizado`
- Última memória absorvida: `C:\Repos\SHAREBOOK\sharebook-agent\memory\2026-07-30-cover-diversity.md`
- Total de memórias lidas: `4 memórias episódicas absorvidas (2026-07-27-cadastro-rastreios-doacoes, 2026-07-27-quatro-preparos-editoriais-publicacao, 2026-07-27-recuperacao-editorial-falsos-positivos, 2026-07-30-cover-diversity)` + releitura de `2026-07-27-dream.md` para contexto real do checkpoint anterior.

## Consolidação produzida

### Reparo de corrupção (prioridade deste ciclo)
O commit `6c6bbfe` (30/07, sobre backlog de produto) sobrescreveu, como efeito colateral (aparentemente checkout/branch desatualizado no momento do commit), conteúdo bom e recente de três arquivos:
- **`memory/_dream-state.md`** — regrediu para um checkpoint anterior a `2026-07-19`, apagando o registro do dream de `2026-07-27` (`59aa1a4`). Corrigido agora com o checkpoint real.
- **`skills/runtime/windows-local.md`** — perdeu 8 guardrails reais e pagos: trap Python 3.14 vs 3.12, confirmação de `paramiko` antes de depender dele, guardrail `Invoke-WebRequest`/`Invoke-RestMethod` (adicionado por sessão viva em `48c28f1` no mesmo dia 27/07 e destruído 3 dias depois), guardrail `publish-once --id`, guardrail de Bash tool silencioso em comandos longos do Windows, exemplo específico de corrupção de heredoc Python no PowerShell, guardrail de monitor de background órfão (achado maior da sessão de 07-24, consolidado no dream de 07-27), seção "Browser pane — screenshot pode travar". Todos restaurados; o conteúdo novo e legítimo que o commit trouxe (nota sobre `paramiko` já disponível, bullet "Inline Python no PowerShell") foi preservado e mesclado.
- **`skills/engineering/frontend.md`** — perdeu as duas seções que o dream de 07-27 tinha acabado de promover: padrão "Chart.js atrás de `*ngIf`" (recorrência real, 2ª ocorrência) e fallback Karma/Puppeteer Chrome ausente. Restauradas. O conteúdo novo e legítimo (reescrita mais detalhada da seção SSR, Shelf arrows, HomeService showcase Union) foi mantido — não foi revertido, só complementado.

Este não foi tratado como esquecimento seletivo ou poda deliberada — é reparo de dado perdido por acidente de commit, plenamente dentro do mandato do Dream de manter o corpus coerente. Guardrails já validados por recorrência real não são candidatos a esquecimento só porque desapareceram sem querer.

### Consolidação de memórias novas
- **`skills/importers/ebook-importer/SKILL.md`** — uma adição: `PurePosixPath` em vez de `Path` para qualquer caminho Windows que atravesse a fronteira para o container Linux (lição da sessão de recuperação editorial de 07-27; helper quebrou silenciosamente gravando barra invertida, dry-run falhou antes de qualquer publicação real).
- `skills/product-ux/cover-direction/SKILL.md` — nenhuma ação. Toda a evolução da sessão de 07-30 (roleta com 14 famílias/7 macrogrupos, `--avoid-style`/`--avoid-group`, geração nativa preferencial) já tinha sido consolidada ao vivo nos commits `c28e485`/`208b288`/`9e308db`. Conferido via leitura do arquivo atual — nada faltando.
- `scripts/production/INDEX.md` e os dois utilitários de leitura read-only — já corrigidos e indexados ao vivo no commit `a2511e1`. Sem ação.

### Decisão consciente de não promover
- A lição "recuperar antes de rejeitar quando o defeito é do resolvedor de PDF, não da obra" (sessão `2026-07-27-recuperacao-editorial-falsos-positivos.md`) **não foi promovida** para `skills/importers/ebook-importer/SKILL.md`. A própria memória registra que Raffa pediu uma conversa específica antes de qualquer mudança na skill de preparo editorial. Promover isso agora, de forma autônoma, contrariaria uma instrução explícita — fica como candidato para sonho manual ou para quando essa conversa acontecer.
- Badge contraditório de livro físico já doado (fix `336bb29`, repo `sharebook-frontend`) — ocorrência única, sem repo/skill do `sharebook-agent` envolvido além do registro em memória. Não criou skill nem editou `frontend.md` por falta de recorrência.

## Próximo dream
- Confirmar que o checkpoint deste ciclo (`2026-08-03`) sobrevive ao próximo commit externo — o incidente de `6c6bbfe` sugere que outra sessão (provavelmente Codex operando num checkout desatualizado) pode voltar a sobrescrever arquivos de skill/memória sem querer. Se acontecer de novo, vale considerar um guardrail estrutural (ex: checar `git log` do arquivo antes de qualquer commit que o edite "de passagem").
- A lição de recuperação editorial (07-27) segue pendente de conversa com Raffa antes de virar skill — não é papel do Dream autônomo forçar isso.
- `client_max_body_size` do nginx segue pendente (arrastada desde 06-21).
- Canal Claude↔OpenClaw (A2A) segue sem execução real — sem novidade nesta safra.
- Item backlog `limpeza-duplicatas-catalogo.md` (235 excedentes) segue sem novo caso de produção.
- Novos itens de backlog nesta safra (Pegasus Engagement Engine, Lista de Desejos, OpenAI Codex OAuth drain) são decisão de produto, fora do mandato de arquitetura de skills do Dream — não tocar.
- `skills/runtime/openclaw.md` ganhou uma seção nova e legítima de diagnóstico de OAuth/sessões silenciosas (via o mesmo commit `6c6bbfe`) — vale observar se esse padrão se repete, o que confirmaria a heurística e a tornaria candidata a endurecimento adicional.

## Observações
- Dream executado de forma autônoma (scheduled task, sem usuário presente).
- Safra pequena em volume de memórias novas (4 em 4 dias), mas com achado estrutural maior que o normal: corrupção real de três arquivos por um commit externo não relacionado. A maior parte do esforço deste ciclo foi diagnóstico (`git log`/`git show` extensivo) e reparo, não promoção de aprendizado novo.
- Padrão reconfirmado: quando a sessão original já consolida o aprendizado ao vivo (commit direto em skill/script na mesma sessão), o papel do Dream é auditar e fechar lacunas, não recriar — válido para `cover-direction` e para os utilitários de leitura read-only nesta safra.
- Padrão novo: consolidação ao vivo não é permanente por padrão. Um commit não relacionado, de outra sessão/agente, pode reverter silenciosamente conteúdo já consolidado se operar sobre um checkout desatualizado. O Dream não deve mais presumir que "já foi commitado" significa "está seguro" — vale conferir o estado atual do arquivo, não só a existência de um commit passado que o tocou.
