---
name: book-lifecycle
description: Operar com segurança o ciclo de vida de livros e doações existentes: aprovar, rejeitar, cancelar, acompanhar envio, rastreio, entrega e encaminhar a escolha de pessoa ganhadora.
---

# Ciclo de Vida de Livros e Doações

Este playbook conduz mutações operacionais de um livro ou de sua doação. Cadastro, pesquisa editorial, imagem e sinopse pertencem à família `importers`; aqui começa quando há um registro existente cujo estado precisa mudar.

## Princípios

- Confirmar o estado real pela API oficial antes de qualquer mutação.
- Confirmar o livro exato e a intenção da pessoa autorizada. Aprovar, rejeitar, cancelar, informar rastreio e marcar entrega mudam a experiência de outras pessoas.
- Usar scripts oficiais ou wrappers versionados. Nunca atualizar estado diretamente no banco nem improvisar chamada bruta à API em produção.
- Após timeout ou resposta ambígua, consultar o estado antes de repetir a mutação.
- Operações irreversíveis ou que encerram solicitações exigem autorização explícita imediatamente antes da execução.

## Roteamento por operação

| Necessidade | Dono deste fluxo |
| --- | --- |
| Cadastrar, pesquisar, escolher categoria, escrever sinopse ou enviar foto de um livro novo | `../../importers/physical-book-importer/PLAYBOOK.md` |
| Aprovar ou agendar um livro já cadastrado | esta página |
| Rejeitar ou cancelar um livro/doação | esta página |
| Escolher a pessoa ganhadora entre solicitações | `../winner-selection/PLAYBOOK.md` |
| Informar rastreio, confirmar recebimento ou entrega | esta página |

## Aprovação e agendamento

1. Localizar o livro pelo identificador ou slug e conferir que ainda está no estado que permite aprovação.
2. Verificar categoria, imagem, frete e sinopse antes de publicar. Se a pendência for editorial, voltar ao playbook de importação para corrigi-la.
3. Quando a intenção for publicar agora, usar o wrapper compartilhado:

```powershell
python C:\Repos\SHAREBOOK\sharebook-agent\playbooks\_shared\scripts\production\sharebook_prod_book.py approve --id "<ID>"
```

4. Para livro físico com abertura futura, usar `--release-date YYYY-MM-DD` junto da aprovação. Confirmar `Scheduled` e a data no retorno; sem data futura, confirmar `Available`.
5. Validar a transição pelo payload ou uma consulta oficial. Só então comunicar a conclusão.

## Rejeição, cancelamento, envio e entrega

Os endpoints existem no produto, mas o wrapper versionado atual ainda não expõe todos esses comandos. Antes de operar:

1. Abrir o script compartilhado e confirmar se há subcomando seguro para a ação pedida.
2. Se não houver, não usar `curl` nem uma mutação ad hoc. Criar ou estender o wrapper com validação proporcional, testar sem efeitos colaterais e só então executar com autorização explícita.
3. Registrar a razão fornecida para rejeição ou cancelamento na superfície oficial; não inventar justificativa.
4. Depois de qualquer transição, consultar o estado final e conferir as consequências esperadas para solicitações e notificações.

## Escolha de pessoa ganhadora

Quando o livro estiver aguardando decisão da pessoa doadora, este playbook só faz o roteamento. O anonimato, a qualidade mínima da shortlist, a autorização em duas etapas e a mutação de escolha estão em `../winner-selection/PLAYBOOK.md`.

## Limites

- Não mover regras de voz, layout, marca ou UX writing para esta família: elas pertencem a `product-ux`.
- Não colocar triagem editorial, escrita de sinopse, PDF ou importação de source aqui: elas pertencem a `importers`.
- Não usar o fato de uma operação afetar uma tela como motivo para classificá-la como UX.
