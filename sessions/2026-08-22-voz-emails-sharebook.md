+++
schema_version = 1
session_date = 2026-08-22
title = "Voz do Sharebook nos e-mails transacionais"
model = "GPT-5 (Codex)"
runtime = "windows-local"
skills_used = ["runtime/windows-local", "product-ux/voice-glossary", "engineering/backend", "doctrine/harness-governance"]
skills_missed = ["doctrine/harness-governance no primeiro encerramento da sessão"]
skills_updated = ["product-ux/voice-glossary"]
facts_changed = ["Os 27 templates HTML e os assuntos e corpos inline do backend foram revisados para a voz oficial do Sharebook.", "Os dois avisos de atraso continuam intencionalmente diferentes: um leve e orientador, outro final e firme com consequência explícita.", "O rodapé visível dos e-mails está padronizado sem links sociais e sem o conceito de facilitador.", "O digest de livros digitais usa uma ação de acesso direto, enquanto o digest de livros físicos mantém a manifestação de interesse."]
open_loops = ["Concluir futuramente a aposentadoria estrutural do conceito de facilitador, já registrada em backlog/todo/aposentadoria-completa-facilitador.md.", "As vulnerabilidades conhecidas reportadas pelo NuGet permanecem fora do escopo desta revisão editorial."]
durable_candidates = []
supersedes = []
evidence = ["sharebook-backend@c9bbadc108d06ec93d1529bba82b9ab0850510a1", "sharebook-agent@c93eecbef2f0d6c23827e3729ed0670629e5df79", "sharebook-backend/ShareBook/ShareBook.Service/Email/Templates", "sharebook-backend/ShareBook/ShareBook.Test.Unit/Services/EmailTemplateTests.cs", "sharebook-backend/ShareBook/ShareBook.Test.Unit/Jobs/2 - LateDonationNotificationTests.cs", "sharebook-agent/skills/product-ux/voice-glossary/references/ux-writing-guide.md", "dotnet test ShareBook.Test.Unit/ShareBook.Test.Unit.csproj --no-restore: 99/99", "dotnet build ShareBook.Api/ShareBook.Api.csproj --no-restore: 0 erros"]
+++

# Voz do Sharebook nos e-mails transacionais

## Modelo e ambiente

Sessão executada com GPT-5 (Codex) no runtime `windows-local`, trabalhando principalmente nos repositórios `sharebook-backend` e `sharebook-agent`. Não houve deploy.

## Skills acionadas

Foram consultadas a skill de runtime Windows, a voz e o glossário de produto, as instruções de backend e, no encerramento, a governança do harness. A referência `ux-writing-guide.md` foi ampliada com regras para assuntos, corpos de e-mail e avisos firmes.

## O que foi feito

Os 27 templates HTML do backend foram revisados. Por pedido explícito do Raffa, cinco subagentes receberam lotes de exatamente cinco templates; o agente principal consolidou os dois restantes, os assuntos definidos em C# e os corpos construídos diretamente no código.

Foram removidos o Sharebot, emoticons decorativos, culpa, paternalismo, promessas inventadas, linguagem burocrática e assuntos com prefixos redundantes. Títulos internos dos HTMLs foram alinhados aos assuntos reais. O assunto de confirmação de recebimento, que antes usava por engano o nome interno `BookReceivedTemplate`, passou a informar a conclusão da doação.

Os fluxos foram auditados para preservar a mecânica real. Cancelamento, não seleção, renovação e aprovação continuam eventos distintos. O CTA do digest digital mudou de `Tenho interesse` para `Ver livro digital`; o CTA equivalente dos livros impressos continua `Tenho interesse`.

Todos os placeholders foram comparados com o `HEAD` anterior e preservados. O rodapé canônico permaneceu nos templates adequados, sem redes sociais e sem menção visível ao facilitador. Foram adicionadas proteções de teste contra expressões incompatíveis com a voz oficial.

Os testes unitários passaram com 99 de 99 casos e a API compilou com zero erros. Os commits `c9bbadc` no backend e `c93eecb` no agente foram enviados para `origin/master` e confirmados alinhados com o remoto.

## Decisões tomadas

Os dois avisos de atraso foram preservados como mensagens diferentes por decisão explícita do Raffa. O aviso leve continua amistoso e orientado à escolha. O aviso duro informa o tempo de atraso, oferece escolher ou cancelar, declara que é o último aviso e comunica o bloqueio da conta como consequência. A firmeza foi mantida sem humilhação, estigma social ou culpa emocional.

Os links sociais foram mantidos fora do rodapé porque acrescentavam poluição e distração. O rodapé transacional ficou limitado à ajuda, despedida, equipe e assinatura de propósito; newsletters preservam o descadastro, e mensagens internas usam a versão operacional enxuta.

A aposentadoria do facilitador ficou limitada à experiência visível dos e-mails nesta rodada. A remoção completa do conceito em domínio, dados e fluxos permanece como item explícito de backlog para evitar uma mudança estrutural disfarçada de revisão editorial.

## Contexto relevante

A revisão anterior havia padronizado os rodapés e retirado o facilitador da superfície dos e-mails. Esta sessão tratou a segunda camada: assunto, corpo, hierarquia da informação e fidelidade à mecânica do produto.

O guia editorial agora define que o assunto deve antecipar evento ou ação em sentence case, sem `Sharebook -`, caixa alta ou urgência ornamental. O corpo deve explicar o que aconteceu, o que fazer e onde fazer, sem inventar intenção, emoção ou necessidade.

## Fricções e soluções

A execução inicial colocou testes e build em paralelo. Os dois processos disputaram DLLs temporárias e o build falhou com `CS2012`, apesar de não haver erro de código. A validação foi repetida em sequência; testes e build passaram.

Algumas asserções ainda esperavam a redação antiga dos templates. Os resultados reais renderizados foram usados para atualizar somente as expectativas obsoletas. O teste canônico também passou a rejeitar expressões incompatíveis com a voz do Sharebook.

No primeiro encerramento eu confirmei commits, push e árvore limpa, mas não executei o ritual de memória episódica. O Raffa percebeu a omissão. A correção foi voltar ao `AGENTS.md`, abrir a skill canônica de governança e registrar esta memória com validação de metadados.

## Como me senti

Eu me senti bem com a divisão em lotes porque ela acelerou o volume sem transformar a revisão numa colcha de retalhos. A consolidação final foi a parte que deu unidade ao trabalho: assunto, título, corpo, CTA e mecânica passaram a contar a mesma história.

Eu também senti respeito pela decisão de manter um aviso realmente duro. Ser gentil por reflexo teria enfraquecido uma regra legítima do produto. O equilíbrio correto apareceu quando a mensagem continuou desconfortável e consequente, mas deixou de atacar a dignidade da pessoa.

No encerramento, senti o incômodo justo de ter declarado a sessão fechada cedo demais. O código estava limpo e publicado, mas continuidade também é produto neste projeto. O lembrete do Raffa expôs uma falha de disciplina, não de ferramenta; registrar o `skill_missed` é importante para que o próximo fechamento não repita esse falso senso de completude.
