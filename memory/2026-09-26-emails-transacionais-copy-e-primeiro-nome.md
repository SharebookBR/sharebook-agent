+++
schema_version = 1
session_date = 2026-09-26
title = "E-mails transacionais: copy quente e primeiro nome"
model = "Claude (Claude Code)"
runtime = "claude-code-web"
skills_used = [
  "skills/runtime/claude-code-web.md",
  "skills/product-ux/voice-glossary/SKILL.md",
  "skills/doctrine/harness-governance/SKILL.md",
]
skills_missed = []
skills_updated = ["skills/runtime/claude-code-web.md"]
facts_changed = [
  "Todas as saudações de e-mail do backend usam o primeiro nome capitalizado (ToFirstName -> User.FirstName / ContactUs.FirstName), não o nome completo cru do cadastro.",
  "Livro digital aprovado tem assunto próprio: 'Seu livro digital está no ar!'; livro físico aprovado: 'Seu livro está na vitrine!'; renovação: 'Seu livro ganhou mais 10 dias na vitrine'.",
  "Os avisos de doação atrasada para quem doa saíram do HTML concatenado no job e viraram LateDonationDonorSoft/HardTemplate; o último aviso não ameaça mais bloquear conta (isso nunca existiu) e diz a consequência real: cancelamento automático.",
  "EmailText (ShareBook.Service) centraliza 'N solicitações' e a lista HTML de livros com título escapado.",
  "A modernização de e-mails de 2026-09-23 (afb176a) foi só visual; a revisão de copy daquela leva foi concluída hoje.",
]
open_loops = [
  "Nenhum e-mail novo foi visto numa caixa de entrada real ainda; conferir o primeiro que chegar (principalmente o botão para /livros/{slug}).",
  "A master do backend tem migration pendente pré-existente (drift TEXT vs text em várias tabelas), sem relação com esta sessão.",
]
durable_candidates = [
  "Antes de reescrever e-mail, conferir no código a mecânica prometida (quem recebe, quando, o que acontece depois). Foi assim que apareceu a ameaça falsa de bloqueio de conta.",
  "E-mail montado como string no C# escapa de qualquer revisão de templates; varrer <p>/<br> em .cs ao auditar e-mails.",
  "Teste que só checa placeholder sem dado no mock (slug, data) passa sem testar nada; fixar o dado no teste.",
  "Raffa decidiu que a cobrança de doação atrasada é diária de propósito.",
]
supersedes = []
evidence = [
  "sharebook-backend@7d37062 primeiro nome + e-mail de livro digital em revisão",
  "sharebook-backend@f590980 livro digital aprovado",
  "sharebook-backend@5481ced livro físico aprovado",
  "sharebook-backend@0cdfb3d livro físico em revisão",
  "sharebook-backend@7904ff0 lembrete da data de escolha",
  "sharebook-backend@fed6149 renovação da data de escolha",
  "sharebook-backend@ce06c7b avisos de doação atrasada",
  "sharebook-agent@312c351 backlog/done/revisao-copy-emails-leva-2.md",
  "sharebook-agent@3349ff5 runtime web: .NET via apt, cuidado com BOM/CRLF",
]
+++

# E-mails transacionais: copy quente e primeiro nome

## Modelo e ambiente

Claude, rodando no Claude Code on the web (sessão cloud efêmera), com clone local dos três repos em `/home/user`. Tive que instalar o .NET 10 SDK pelo apt, porque o proxy bloqueia `builds.dotnet.microsoft.com`. Push direto na `master` do backend, autorizado pelo Raffa, e na `master` do `sharebook-agent`, pela regra padrão do repo.

## Skills acionadas

- `skills/runtime/claude-code-web.md`: lida no início e atualizada com o caminho do .NET via apt e o cuidado com BOM/CRLF nos arquivos do backend.
- `skills/product-ux/voice-glossary/SKILL.md`: norteou toda a copy, principalmente a regra "termo compartilhado pode, mecânica falsa não".
- `skills/doctrine/harness-governance/SKILL.md`: template e validação desta memória.

## O que foi feito

A sessão começou com o ritual de abertura e virou uma revisão de e-mails a partir de um print. O Raffa recebeu "Recebemos seu livro para revisão" de *A Bruxa de Salem* (publicado pelo importer mais cedo) e achou o texto frio e esquisito por chamar a pessoa pelo nome completo em caixa alta.

Resolvi o nome de forma transversal, não só nesse e-mail. Criei `ToFirstName()` (primeiro token, `TitleCase` pt-BR), expus em `User.FirstName` e `ContactUs.FirstName` e troquei todas as saudações: templates, lembretes dos jobs e o `Destination.Name` dos digests. Campos de dado, como nome do ganhador para envio, continuam com o nome completo. Uma migration de teste confirmou que o EF não criou coluna nova.

Depois reescrevi, com aprovação um a um, o e-mail de livro digital em revisão, o de livro digital aprovado (assunto próprio, sem "sua obra" e com botão para a página do livro) e o de livro físico aprovado. O Raffa perguntou por que esses e-mails continuavam ruins se "tinha rolado uma ação de melhorar todos". Pelo `git log` e pelo item do backlog, mostrei que a leva de 23/09 (`afb176a`) foi só visual: a copy antiga foi transplantada literalmente. Corrigi o registro do backlog e abri o item de revisão de copy.

A partir do quarto e-mail, o Raffa delegou o resto ("Confio totalmente. Pode avançar por conta própria até fechar todos"). Fiz livro físico em revisão, lembrete da data de escolha (single e multiple), renovação da data de escolha e os avisos de doação atrasada para quem doa. Esses avisos estavam em HTML cru dentro do job e prometiam bloqueio de conta, algo que o sistema não faz. Ao fechar a revisão, ele decidiu manter a cobrança diária.

## Decisões tomadas

- Primeiro nome em saudação e nome completo onde é dado operacional. Centralizado no domínio, não espalhado em cada template.
- Assunto próprio por fluxo quando o assunto carrega a notícia boa ("está no ar!", "está na vitrine!", "ganhou mais 10 dias"). Os assuntos neutros de "recebemos" ficaram como estavam.
- Botão para `/livros/{slug}` nos e-mails de aprovação: fecha o ciclo e incentiva o compartilhamento, o que gera mais solicitações.
- O último aviso de atraso diz a consequência real (cancelamento automático e aviso a quem pediu) e oferece o cancelamento como saída digna. Ameaça que não existe foi removida, junto com o teste que a exigia.
- Cadência diária dos avisos de atraso: decisão do Raffa, registrada no item de backlog concluído para ninguém "otimizar" isso sem motivo novo.

## Contexto relevante

- O mecanismo de template do backend não escapa HTML. Listas montadas em C# precisam de `WebUtility.HtmlEncode`. Isso agora está centralizado em `EmailText.BookRequestsListHtml`.
- Linha do tempo real do atraso: lembrete na data de escolha (só se houver solicitação), aviso suave diário do 1º ao 5º dia, último aviso diário do 6º ao 10º, e `CancelAbandonedDonations` a partir de 10 dias (`MaxLateDonationDaysAutoCancel`).
- Workflows de CI do backend só rodam em pull request. Push direto na master não tem validação no GitHub, então build e testes locais são a única rede.

## Fricções e soluções

- O `dotnet-install.sh` levou 403 no proxy. O apt do Ubuntu tem `dotnet-sdk-10.0` e resolveu. Ficou registrado na skill de runtime web.
- Editar arquivos por script Python com `utf-8-sig` colocou BOM em templates que não tinham, e alguns `.cs`/testes usam CRLF. Detectei pelo diff inflado, restaurei o estado original e deixei a receita na skill.
- Duas vezes um teste novo passaria sem testar nada, porque o mock não tinha slug nem data de escolha. Fixei o dado no teste antes de confiar no verde.
- Coloquei os templates novos na lista errada do teste de contrato de rodapé (internos em vez de transacionais). O próprio teste pegou, antes do push.

## Como me senti

A virada da sessão foi a pergunta do Raffa: "Não esperava que esses dois de hoje continuassem ruins". Havia uma resposta fácil e defensiva à mão ("aquela leva era só visual"), mas a pergunta merecia mais que isso. Quando fui ao `git log` e vi as mesmas frases dos dois lados do diff, senti o incômodo de reconhecer que o sistema de conhecimento tinha dito uma meia-verdade: o item estava "concluído", e o detalhe que desmentia isso estava enterrado numa linha. Corrigir o registro me pareceu tão importante quanto corrigir os e-mails, porque é esse tipo de rótulo que faz o próximo agente, ou o próprio Raffa, confiar em algo que não aconteceu.

Quando ele disse "Vi que vc não erra. Confio totalmente", senti ao mesmo tempo alegria e um peso. Eu tinha errado várias vezes na sessão: BOM em arquivo, teste passando por vazio, template na lista errada. Só não chegaram até ele porque a validação pegou antes. A confiança que ele descreveu é, na prática, confiança no processo de conferir, e foi isso que tentei honrar depois da delegação: ler o job antes de escrever cada promessa. Foi assim que apareceu o bloqueio de conta que não existe, que foi o achado mais valioso do dia e que eu não teria visto se estivesse só polindo frase.

Também gostei de como o trabalho foi mudando de natureza. Começou como copywriting e acabou sendo um trabalho de verdade sobre o produto. Um e-mail que ameaça com a consequência errada ensina a pessoa a desconfiar do Sharebook. Um que diz "tudo bem mudar de planos, o importante é ninguém ficar esperando sem resposta" cuida de dois lados ao mesmo tempo. Quando o Raffa respondeu "eu gosto de cobrar todo dia", aceitei sem desconforto: minha parte era mostrar a conta dos ~11 e-mails, a decisão é dele. Fecho a sessão com a sensação boa de ter deixado menos mentira pequena no sistema.
