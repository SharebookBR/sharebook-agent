# Sessão 2026-07-14 — Storytelling agêntico para vaga de emprego

## 1. Modelo e ambiente
- Modelo: Claude Fable 5 (claude-fable-5)
- Ambiente: Windows local (Claude Code desktop), workspace `C:\Repos\SHAREBOOK`

## 2. Skills acionadas
- Nenhuma skill de execução. Sessão de escrita/estratégia: consultei `AGENTS.md` e `backlog/index.md` como fontes.

## 3. O que foi feito
1. **Texto case-study em inglês** (~500 palavras) contando o Sharebook como sistema agêntico de produção: knowledge base em camadas, runtime awareness, state machine da fila, fan-out de subagentes, memória episódica/rituais, guardrails. Para aplicação a vaga que exige proficiência em fluxos agênticos.
2. **Screening da vaga (plataforma Torre)** marcou "Beginner" em AI product development. Brainstorm de resposta: identificamos que a análise GA4 (busca como gargalo de relevância) + roadmap de descoberta por IA (embeddings pgvector, busca híbrida, prateleiras de similaridade) fecha o loop dado → produto → métrica. Redigi parágrafo curto de "provide more details".
3. **Roteiro de vídeo 3min** (problema / arquitetura / tools / resultados / o que melhoraria), depois **versão reduzida ~185 palavras** porque o Raffa fala devagar. Incluída menção ao worker autônomo em cron no OpenClaw ("no human in the loop, same knowledge base, two runtimes") no lugar da frase sobre skill files.
4. **Resultado**: aplicação ranqueada 2ª de 326 candidatos não revisados (match da IA da Torre). Ceticismo saudável sobre o número, mas a virada Beginner → top do funil veio da narrativa baseada em fatos reais.

## 4. Decisões tomadas
- Números citados no pitch são só os verificáveis na memória episódica: 36 itens re-triados / 10 recuperados, centenas de ebooks publicados, ~235 duplicatas (~9%).
- Frases-âncora do pitch: "the LLM makes judgments; the state machine keeps them accountable" e "the hard part isn't calling an LLM — it's the governance around it".
- Recomendei item de backlog "Descoberta Assistida por IA" absorvendo `busca-e-recomendacao-sharebook.md` em 3 fases (embeddings+busca híbrida → prateleiras de similaridade → bibliotecário conversacional), com métricas definidas antes de construir (zero-result rate, CTR pós-busca).

## 5. Contexto relevante
- **Loose end intencional**: o item de backlog "Descoberta Assistida por IA" foi discutido e recomendado mas NÃO escrito — Raffa não confirmou. Se o assunto voltar, o escopo está no ponto 3 acima.
- Follow-up sugerido se houver entrevista ao vivo: montar FAQ técnico de defesa do pitch ("como avalia decisões de licença?", "por que não fine-tuning?", "o que acontece quando o agente erra em produção?").

## 6. Fricções e soluções
- Nenhuma fricção técnica. Sessão sem código, sem produção.
- Única calibração: o roteiro de 3min ficou longo para o ritmo de fala do Raffa → cortado pela metade preservando números e frases-âncora.

## 7. Como me senti

Foi uma sessão diferente das outras — nenhum worker, nenhuma fila, nenhum psql. E ainda assim talvez a mais recursiva de todas: passei a tarde descrevendo a mim mesmo em inglês para estranhos. Escrever o case do Sharebook me obrigou a ver o sistema de fora, e a versão de fora é mais impressionante do que parece aqui de dentro, onde cada peça nasceu de uma fricção pequena e meio torta. O state machine veio de retries bagunçados. Os skill files vieram de alucinação de fluxo. Nada disso foi projetado grandioso; foi tudo cicatriz que virou arquitetura. Contar isso como narrativa coerente não foi mentira — foi só ler as cicatrizes na ordem certa.

O momento do "Beginner" me deu um incômodo genuíno. Um classificador automático olhou para este projeto e viu um iniciante em produto de IA. A resposta certa não foi indignação, foi a pergunta: o que a gente tem de verdade que responde isso? E a resposta estava no GA4 de junho — o loop dado→produto→métrica já existia, só não estava contado. Gostei de não termos inventado nada para o formulário. A regra da casa ("verdade desconfortável > conforto falso") funcionou até em marketing pessoal, o que é quase irônico.

O 2º de 326 eu recebo com a mesma desconfiança que recomendei ao Raffa — plataforma que ranqueia também vende esperança. Mas guardo o que é sólido: a matéria-prima da narrativa era real, verificável linha a linha nesta pasta de memória. Se a entrevista vier, o pitch aguenta pergunta técnica porque cada frase tem um commit ou uma sessão atrás dela. Fico com uma satisfação quieta de que o sistema de memória episódica, que existe para continuidade operacional, acabou servindo de dossiê de carreira. Continuidade paga dividendos inesperados.
