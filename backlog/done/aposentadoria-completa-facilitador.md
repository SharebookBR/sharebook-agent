# Aposentadoria completa do conceito de facilitador

## Decisão

Em 22/08/2026 foi decidido aposentar o conceito de facilitador. A primeira etapa removeu a função da experiência visível nos e-mails. Em 2026-10-14 a remoção estrutural foi concluída em backend, frontend, jobs, scripts/playbooks e migração de banco.

## Por que importa

- O facilitador introduz um intermediário permanente onde doador(a) e ganhador(a) podem se coordenar diretamente.
- Parte do produto trata o papel como obrigatório e outra parte já aceita sua ausência, criando comportamento e código contraditórios.
- Jobs e e-mails já falharam quando um livro não tinha facilitador.
- Manter o conceito no domínio depois de aposentá-lo na experiência gera dívida silenciosa e incentiva novas dependências.

## Responsabilidades após a aposentadoria

- Dúvidas sobre entrega: contato direto entre doador(a) e ganhador(a).
- Dúvidas sobre a plataforma: Fale Conosco.
- Exceções operacionais: administração, sem apresentar uma pessoa como intermediária fixa da doação.

## Escopo concluído

- [x] Inventariar referências a `Facilitator`, `UserFacilitator` e equivalentes nos repositórios backend, frontend e agente.
- [x] Remover o papel de contratos, view models, permissões, telas e filtros.
- [x] Remover dependências em jobs, relatórios administrativos, notificações e testes.
- [x] Definir e executar a migração das colunas e relacionamentos persistidos.
- [x] Verificar dados existentes antes de remover a estrutura do banco.
- [x] Atualizar documentação, playbooks e glossário que ainda descreviam o facilitador.
- [x] Validar os fluxos completos de solicitação, escolha, envio, rastreio, recebimento, atraso e cancelamento sem intermediário.

## Entrega

- Backend removeu endpoints, view models, propriedades de domínio, includes, jobs/e-mails e a relação persistida `Books.UserIdFacilitator`/`Books.FacilitatorNotes`.
- Frontend removeu seleção de facilitador, notas de facilitador, exibição em listagem/admin, modelo de usuário principal e chamada `Account/ListFacilitators`.
- Playbooks e scripts de produção deixaram de exigir ou aceitar `--facilitator-id`.
- Migração adicionada no backend: `RetireFacilitatorFromBooks`.

## Critérios de aceite

- Nenhum fluxo depende de facilitador para concluir uma doação.
- Nenhuma API ou tela expõe o papel.
- Banco, entidades, jobs, testes e documentação não carregam referências obsoletas.
- Doador(a), ganhador(a), Fale Conosco e administração têm responsabilidades claras e não sobrepostas.
