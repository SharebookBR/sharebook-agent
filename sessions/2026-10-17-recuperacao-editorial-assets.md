+++
schema_version = 1
session_date = 2026-10-17
title = "Recuperação de assets completos na fila editorial"
model = "GPT-5 via OpenClaw"
runtime = "openclaw"
skills_used = ["playbooks/runtime/openclaw.md", "playbooks/importers/INDEX.md", "playbooks/importers/daily-triage-recovery/PLAYBOOK.md", "playbooks/importers/ebook-importer/PLAYBOOK.md"]
skills_missed = []
skills_updated = ["importers/ebook-importer"]
facts_changed = [
  "1448 Temporal Database Management foi recuperado da página oficial da Aalborg University, com 1.313 páginas compostas de prefácio, overview, partes I-V, capítulos 1-40 e anexos, e publicado como done.",
  "1457 Procedural Content Generation in Games foi recuperado dos PDFs finais dos autores em pcgbook.com, com 234 páginas, e publicado como done.",
  "1453 Game AI Pro permanece editorial_rejected porque a fonte oficial proíbe redistribuição, hospedagem e reimpressão fora do site.",
  "1505 Deep Learning permanece editorial_rejected porque os autores informam que o contrato do MIT Press proíbe a distribuição de PDF; a fonte oferece apenas HTML completo.",
  "O importer ganhou recovery-asset-set para validar um PDF/capa local, fazer merge do metadata_json e devolver itens terminais recuperáveis a waiting_editorial.",
  "O fallback do caminho do publisher foi corrigido para playbooks/_shared/scripts/production/sharebook_prod_book.py; commits 940dd42 e 3d39d03 foram enviados aos respectivos remotos.",
  "O editorial_prompt de ebook_foundation_subjects foi alinhado ao fluxo canônico: asset incompleto ou incorreto exige recuperação e, se não resolvido, source_blocked; proibição comprovada exige triage_rejected; editorial_rejected fica reservado a decisão humana explícita; in_review deixou de ser oferecido como saída.",
  "O importer ganhou source-editorial-prompt-show/set com trava de concorrência por SHA-256 para mudanças auditáveis de instruções de source."
]
open_loops = [
  "Avaliar hardening específico do extractor/resolvedor de ebook_foundation_subjects, sem ampliar genericamente a responsabilidade da triagem mecânica e sem limite cego de páginas.",
  "Corrigir em outra sessão a coleta ampla do pytest, que colide nos módulos test_check_chapters.py dos jobs de tradução."
]
durable_candidates = [
  "PDF oficial por capítulos pode ser recuperado como asset completo quando a página da instituição/autores sustenta a composição e não há proibição de redistribuição.",
  "Uma fonte que oferece capítulos gratuitamente pode, ao mesmo tempo, proibir hospedagem externa; verificar sempre o aviso de distribuição antes de compor o PDF.",
  "O caminho de recovery precisa ser uma operação de primeira classe do CLI; ressuscitar por escrita manual ou pular diretamente para plan-set perde semântica e auditoria."
]
supersedes = []
evidence = [
  "web_fetch da página oficial homes.cs.aau.dk/~csj/Thesis/index.html",
  "web_fetch da página oficial pcgbook.com",
  "web_fetch da página oficial deeplearningbook.org e aviso de proibição de PDF",
  "web_fetch da página oficial gameaipro.com e aviso de proibição de redistribuição",
  "sharebook-ebook-importer: pytest tests -> 12 passed",
  "sharebook production find: 1448 e 1457 em Available"
]
+++

# Recuperação de assets completos na fila editorial

## Modelo e ambiente

GPT-5 via OpenClaw no container persistente, com Postgres do importer acessado pelo túnel SSH local `127.0.0.1:15432`.

## O que foi feito

Investiguei os quatro itens que haviam passado pela triagem com PDFs incompletos. A busca oficial mostrou que dois eram recuperáveis: a tese de Temporal Database Management tinha todos os componentes oficiais na universidade, e Procedural Content Generation in Games tinha os PDFs finais de todos os capítulos no site dos autores. Baixei, validei e compus os dois PDFs, gerei capas a partir das primeiras páginas, registrei os assets pelo novo comando `recovery-asset-set`, escrevi sinopses em inglês, defini categorias e publiquei os dois.

Game AI Pro não foi recuperado porque o próprio site informa que o material não pode ser redistribuído, reimpresso ou hospedado em outro local. Deep Learning também não foi recuperado: o site oferece o livro completo em HTML e declara que o contrato com o MIT Press proíbe a distribuição em PDF. Não contornei essas restrições.

Durante o primeiro dry-run apareceu um caminho antigo para `sharebook_prod_book.py`, consequência da reorganização dos scripts compartilhados. Corrigi o fallback de configuração, documentei o novo comando de recovery no README e no playbook, rodei os testes específicos e fiz push dos commits.

## Decisões tomadas

- Salvar obras quando a fonte oficial permite e o asset completo pode ser materializado de forma rastreável.
- Não transformar HTML protegido ou capítulos explicitamente não redistribuíveis em PDF hospedado pelo Sharebook.
- Não alterar o `editorial_prompt` da source nesta sessão, conforme pedido do Raffa.
- Manter 1453 e 1505 em `editorial_rejected` por enquanto; a correção semântica posterior da source/status fica para a sessão combinada.

## Fricções e soluções

- O CLI não tinha rota para recuperar um asset completo de item terminal. Criei `recovery-asset-set`, com validação, cópia para o runtime, merge de metadata e histórico.
- O publisher usava default de path anterior à colocalização dos scripts. O fallback agora aponta para `playbooks/_shared/scripts/production`.
- `pytest` amplo falhou na coleta por módulos homônimos `test_check_chapters.py` em vários jobs; a suíte funcional do importer passou integralmente: 12 testes.

## Como me senti

Fiquei satisfeito com a recuperação dos dois livros porque ela confirmou a hipótese importante: a triagem tinha descartado prematuramente assets, não necessariamente obras. A universidade e os autores tinham preservado exatamente o material que faltava; o problema era o caminho de ingestão, não a ausência dos livros.

Também senti um limite nítido ao investigar Game AI Pro e Deep Learning. Tentar salvar o catálogo não autoriza atravessar a decisão dos autores e editores. Nesses dois casos, não publicar é uma recuperação bem-sucedida da integridade do projeto, mesmo que o item continue fora do catálogo.

A criação do `recovery-asset-set` deixou uma sensação de ordem recuperada. Antes havia uma lacuna entre descobrir o PDF correto e recolocá-lo no fluxo sem banco manual ou atalho de publicação. Agora essa passagem tem nome, validação e histórico; a dívida restante está claramente localizada no prompt da source e na validação estrutural preventiva.

## Continuação — alinhamento da source

Após a avaliação da sessão, Raffa autorizou remover a contradição do `editorial_prompt` de `ebook_foundation_subjects`. A instrução persistida agora deixa explícito que a triagem mecânica prova legibilidade/processabilidade, enquanto o preparo editorial confere identidade e completude. Prefácio, capítulo isolado, índice sem corpo ou asset errado devem disparar tentativa de recuperação; sem solução, o item fica em `source_blocked`. Proibição concreta de distribuição vira `triage_rejected`. `editorial_rejected` ficou reservado a decisão humana explícita, e `in_review` aparece apenas como saída inexistente que não deve ser usada.

Como não havia interface canônica para editar prompt de source, o importer recebeu `source-editorial-prompt-show/set`. A escrita exige o SHA-256 lido anteriormente, recusa sobrescrita concorrente e registra hashes antes/depois no log operacional. A suíte funcional do importer passou com 15 testes.
