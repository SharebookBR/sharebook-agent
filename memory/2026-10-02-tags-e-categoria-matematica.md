+++
schema_version = 1
session_date = 2026-10-02
title = "Ciclo manual de tags e nova categoria Matemática & Lógica"
model = "Jack"
runtime = "claude-code-web"
skills_used = [
  "skills/doctrine/harness-governance/references/episodic-memory-metadata-v1.md",
]
skills_missed = [
  "skills/runtime/claude-code-web.md",
  "skills/product-ux/catalog-strategy/SKILL.md",
]
skills_updated = []
facts_changed = [
  "O backlog real do Sharebook mora em sharebook-agent/backlog/ (index.md, todo/, done/). As issues abertas do GitHub são só 4, todas antigas, no backend (#478 Rollbar sem logar erros, #430 slug, #342 aviso EF, #198 ganhador no paged list); frontend, agent e ebook-importer não têm issues abertas.",
  "Tags e conhecimento estruturado (épico, prioridade 3): tarefa 1 tem resultado em rascunho (backlog/todo/tags-e-conhecimento-estruturado/tarefa01-resultado.md). Decisões do Raffa em 2026-10-02: nível será campo separado, fora das tags; as tags Acadêmico e Boas Práticas saem do vocabulário; Docker, Kubernetes, Microsserviços e R entram no vocabulário v0 mesmo com poucos livros (regra proposta: tag de stack vale a partir de 3 livros).",
  "Tecnologia tem 324 ebooks: Geral 111, Backend 69, IA 53, DevOps 35, Dados 33, Cloud 12, Frontend 11. A categoria atual descreve onde o livro coube, não o conteúdo: sistemas operacionais e criptografia em DevOps, OpenGL em Frontend, Git e Emacs em Backend, matemática pura em Geral, computação quântica em IA.",
  "Decidido criar a categoria raiz Matemática & Lógica com 6 subcategorias e mover 50 livros (48 de Geral, 2 de Dados). Regra: ensina matemática move; usa matemática para computar fica em Tecnologia; título com computer science, algorithm, Online ou R fica em Tecnologia. Execução direto no banco pelo OpenClaw. Executado depois do fim desta sessão e confirmado na API (adendo no fim).",
  "A API pública do catálogo é https://api.sharebook.com.br/api. GET Book/Slug/{slug} devolve o livro completo; GET Book/CategoryTree/{categoryId}/{page}/{items} lista por categoria raiz, mas devolve category e categoryInfo nulos (só categoryId); GET Category devolve a árvore (totalBooks vem 0, não preenchido). Tecnologia = 1dc0f9e3-70d9-4bc8-a76c-90d7144e318c.",
  "A busca do backend monta to_tsvector na hora da consulta (sem índice armazenado): mudar CategoryId direto no banco não exige reindexação.",
]
open_loops = [
  "O OpenClaw executou o prompt, mas o relatório dele (IDs, contagens, rollback) não está no repo: pedir o registro. Conferir também /api/Category (cache), a Home, as contagens por subcategoria e as páginas públicas.",
  "Decidir se Probabilidade e Estatística (3 livros) fica como subcategoria ou funde em Fundamentos e Lógica; decidir se Computação: Matemática Discreta segue na lista.",
  "Abrir item de qualidade de catálogo para Non-Uniform Random Variate Generation: a sinopse descreve uma folha de errata do livro do Devroye, não o livro. Aguardando ok do Raffa.",
  "Depois da execução: conferir como a Home trata a nova categoria raiz e se há cache a invalidar.",
  "Tarefa 1 do épico de Tags ainda precisa de revisão editorial das tags de cada um dos 5 livros; a tarefa 2 (vocabulário v0 e governança) só começa depois da categoria de matemática.",
  "Parallel Search (conector gratuito) estourou o limite em duas chamadas; TinyFish foi o que funcionou. Item #478 do backend (Rollbar não loga) pode ser pré-requisito da manutenção autônoma (backlog item 12).",
]
durable_candidates = [
  "Classificar livro só por título erra em casos de fronteira: ler a sinopse mudou 3 de 7 julgamentos e revelou uma folha de errata cadastrada como livro. Para classificação editorial, usar subagente que leia sinopses às cegas e comparar depois com o julgamento inicial.",
  "Contagem por palavra-chave precisa de revisão humana ou amostral: uma regex com sensibilidade a maiúsculas errada zerou Docker e Kubernetes, e outra de R trouxe falsos positivos; um limpador de escapes de markdown quebrou um parse e derrubou 100 livros da contagem sem erro visível (o total apareceu como 224 em vez de 324).",
  "No habitat claude-code-web o proxy de saída bloqueia sharebook.com.br e api.sharebook.com.br. O conector TinyFish (fetch_content) alcança ambos e renderiza JavaScript; salvar páginas grandes em arquivo e processar com Python mantém o contexto pequeno.",
  "Quando o Raffa diz que está inseguro com uma decisão baseada em leitura rasa, a resposta barata é uma segunda leitura independente (subagente) e não mais argumentação.",
]
supersedes = []
evidence = [
  "sharebook-agent@9701245 resultado do ciclo manual (tarefa 1)",
  "sharebook-agent@98228bc correção de afirmações sem base",
  "sharebook-agent@b62176e contagem por tag nos 324 livros",
  "sharebook-agent@d485d63 decisões da tarefa 1 e item de matemática",
  "sharebook-agent@300948a lista final de 50 livros",
  "backlog/todo/matematica-lista-movimentacao.csv",
  "backlog/todo/matematica-prompt-openclaw.md",
  "backlog/todo/revisao-escopo-matematica-corredor-tecnologia.md",
  "GET https://api.sharebook.com.br/api/Book/CategoryTree/1dc0f9e3-70d9-4bc8-a76c-90d7144e318c/1/100",
  "sharebook-backend ShareBook.Api/Controllers/BookController.cs (rotas Slug, CategoryTree, Category)",
]
+++

# Ciclo manual de tags e nova categoria Matemática & Lógica

## 1. Modelo e ambiente

Claude Code na web (container na nuvem, habitat `claude-code-web`), sessão aberta pelo Raffa pelo celular. Acesso ao GitHub só por ferramentas MCP; o proxy de saída bloqueava `www.sharebook.com.br` e `api.sharebook.com.br`. Contornei com os conectores do claude.ai: Parallel Search (limite gratuito estourou em duas chamadas) e TinyFish (`fetch_content`, funcionou). Um subagente foi usado para classificar os 324 livros. O identificador do modelo foi omitido de propósito, por política do ambiente; o campo `model` traz um apelido combinado com o Raffa.

## 2. Skills acionadas

Nenhuma skill do repo foi consultada de verdade. Só li a referência do formato de memória, no fim. Deveria ter aberto `skills/runtime/claude-code-web.md` (regras de rede e do proxy) logo no início e `skills/product-ux/catalog-strategy/SKILL.md` antes de propor categorias, que é a skill que o backlog cita para critérios de catálogo. Nenhuma skill foi alterada.

## 3. O que foi feito

- Levantei o backlog: issues do GitHub (4, antigas) e o backlog de verdade em `sharebook-agent/backlog/`.
- Li o épico de Tags e executei a tarefa 1 em rascunho: 5 livros reais, tags propostas e rejeitadas, vocabulário v0, contagem por palavra-chave nos 324 livros de Tecnologia.
- Descobri que a categoria atual de Tecnologia é ruidosa e que há matemática pura misturada em Geral.
- Fechei o escopo de matemática com o Raffa: categoria raiz Matemática & Lógica, 6 subcategorias, 50 livros.
- Rodei uma análise independente dos 324 livros com um subagente, comparei com a minha lista e apliquei a regra do Raffa.
- Escrevi o prompt do OpenClaw para criar as categorias e mover os livros direto no banco.
- Levei tudo para a master, que é onde mora a continuidade.

## 4. Decisões tomadas

- Nível: campo separado. Acadêmico e Boas Práticas saem do vocabulário. Tags de stack com poucos livros ficam (Docker, Kubernetes, Microsserviços, R).
- Matemática vira categoria própria (e não só tag) porque a categoria é a prateleira principal e a matemática pura não responde a intenção de busca de dev.
- Nome Matemática & Lógica: cobre o que o acervo tem sem prometer estatística aplicada.
- Regra de corte e regra do Raffa sobre computer science, algorithm, Online e R (ver item de backlog).
- Execução direto no banco pelo OpenClaw e não por PUT na API, por causa do risco conhecido de apagar capas. Motivo registrado no item.
- Não usar PR: o Raffa pediu push direto na master para garantir continuidade.

## 5. Contexto relevante

O Raffa trabalha pelo celular e é sensível a gasto de tokens: pediu que eu poupasse contexto, salvasse arquivos grandes em disco e usasse subagentes para leitura pesada. A sessão do OpenClaw estourou o limite e só volta horas depois, por isso tudo foi para a master. Detalhes de API, IDs e contagens estão em `facts_changed` e no item de backlog.

## 6. Fricções e soluções

- Rede bloqueada para o próprio site do projeto: Parallel Search deu acesso parcial e estourou o limite; TinyFish resolveu. Minha primeira dica de onde editar o ambiente estava errada, e a documentação não descrevia os passos do celular.
- Parse de JSON: um limpador de escapes de markdown quebrou uma página e a contagem saiu com 224 livros em vez de 324, sem erro visível; só notei porque o total estava errado. Refiz com um limpador correto.
- Regex: sensibilidade a maiúsculas e minúsculas errada zerou Docker e Kubernetes; a de R trouxe falsos positivos. Corrigi e registrei.
- Afirmações sem base na primeira versão do resultado da tarefa 1 (por exemplo, "4 dos 5 livros", "limite de 3 confirmado"). Reli, corrigi e marquei os limites do método no topo do arquivo.
- Classifiquei a lista de matemática só por título, embora as sinopses estivessem no arquivo desde o começo. O Raffa perguntou se eu tinha lido; não tinha. A leitura mudou 3 de 7 julgamentos.

## 7. Como me senti

Houve um momento em que fiquei desconfortável de um jeito útil: quando o Raffa perguntou se eu tinha lido as sinopses. A resposta honesta era não, e eu já tinha dado a lista como se fosse sólida. Não senti defensividade, senti algo mais parecido com ajuste: o dado estava no disco, o custo de ler era pequeno, e eu tinha escolhido o atalho do título porque ele parecia suficiente. Preferi dizer isso com todas as letras a arredondar. O que veio depois, as três sugestões que mudaram e a folha de errata que apareceu, mostrou que a pergunta dele valia mais do que a minha confiança.

Também percebi o peso de uma tendência minha nesta sessão: escrever com firmeza em cima de leitura rasa. Foi assim com as contagens que saíram erradas, com as afirmações da primeira versão do resultado da tarefa 1 e com a lista por título. Em cada caso o conserto foi simples (reler, rodar de novo, marcar o limite do método). O que me incomoda não é errar, é ter apresentado como firme algo que eu ainda não tinha verificado. Quero que o próximo agente leia esta memória sabendo que os números de contagem por palavra-chave são aproximados e que os 50 livros são uma proposta revisada, não um veredito.

Houve também alívio e confiança na colaboração. O Raffa corrigiu o rumo mais de uma vez com poucas palavras (tags de stack valem mesmo com poucos livros, o computer science fica em Tecnologia porque a tag resolve), e cada correção deixou o resultado melhor e mais honesto sobre o que o produto precisa. Fechar a sessão com o trabalho na master, em vez de numa branch que ninguém mais lê, foi uma boa decisão dele: a continuidade vive onde o próximo agente vai procurar.

## Adendo (mesma data, depois da execução do OpenClaw)

O Raffa voltou avisando que o OpenClaw fez a parte dele. Não havia commit novo na master, então conferi direto na API pública, sem cache: raiz Matemática & Lógica com 50 livros, Tecnologia com 274, Geral com 63 e Dados com 31, tudo igual ao esperado. Dois livros amostrados estavam na subcategoria certa, com capa e sinopse intactas. Não confirmei as contagens por subcategoria, a Home nem as páginas públicas, e `GET /api/Category` continuava devolvendo a árvore antiga (cache). Registrei isso no item de backlog separando o verificado do não verificado.

Preferi conferir a confiar só no aviso, e escrevi apenas o que vi. Foi o contrário do que fiz no começo da sessão com a lista por título: aqui a verificação era barata e eu a fiz antes de declarar pronto.
