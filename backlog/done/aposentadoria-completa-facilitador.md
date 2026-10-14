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

- Backend removeu endpoints, view models, propriedades de domínio, includes, jobs/e-mails e a relação persistida `Books.UserIdFacilitator`. **`FacilitatorNotes` não foi removida: os comentários da administração são valiosos e viraram `AdminNotes`** (coluna renomeada, dados preservados).
- Frontend removeu seleção de facilitador, exibição em listagem/admin, modelo de usuário principal e chamada `Account/ListFacilitators`. O modal "Comentários" foi mantido como `admin-notes`, apontando para `POST /api/Book/AddAdminNotes`.
- Playbooks e scripts de produção deixaram de exigir ou aceitar `--facilitator-id`.
- Migração adicionada no backend: `RetireFacilitatorFromBooks`. Dropa FK, índice e `UserIdFacilitator` e renomeia `FacilitatorNotes` → `AdminNotes`.
- O e-mail diário de atrasos (`LateDonationNotification`) voltou a exibir a coluna "ANOTAÇÕES", lendo `AdminNotes`.

## Correção de rota e incidente (2026-10-14)

A primeira versão da remoção (commit `4a2579a`) removeu também as anotações, que eram a feature "Comentários" da administração, e entrou na master sem o `.Designer.cs` da migration. Sem os atributos `[DbContext]`/`[Migration]` o EF não enxerga a migration, então ela não rodou e nada falhou em silêncio. Corrigido no mesmo dia: anotações renomeadas para `AdminNotes` (backend `a54c478`, frontend `09f71d3`) e migration regenerada com Designer.

Esse deploy derrubou a API em produção por cerca de 27 min (01:06 a 01:33 UTC): a migration corrigida dava `DROP INDEX "IX_Books_UserIdFacilitator"` e esse índice **não existe no banco de produção** (Postgres `42704` no `Migrate()` do startup, crash loop). Hotfix `b0a0ac6`: drops com `IF EXISTS` e rename condicional de `FacilitatorNotes`. Sem rollback; API de volta às 01:33 UTC.

Pontos em aberto:
- Causa provável de o índice não existir com aquele nome em produção: as tabelas anteriores ao port SQL Server → Postgres têm índices/constraints com prefixo físico `idx_17657_` (regra já documentada em `playbooks/engineering/backend.md`, incidente de 2026-07-22). **Não confirmado**: o agente não lê o banco de produção pelo habitat cloud. Como `DROP COLUMN` leva índices e FKs junto, não deve ter sobrado objeto órfão; uma consulta em `pg_indexes` confirma.
- Os comentários existentes em `AdminNotes` não foram conferidos em produção pelo agente. Sinal indireto: `POST /api/book/AddAdminNotes` respondeu 200 em produção às 01:51 UTC de 2026-10-14, então o modal está em uso; falta abrir uma doação que já tinha notas para ver o histórico antigo.

## Critérios de aceite

- Nenhum fluxo depende de facilitador para concluir uma doação.
- Nenhuma API ou tela expõe o papel.
- Banco, entidades, jobs, testes e documentação não carregam referências obsoletas ao facilitador (as anotações administrativas permanecem, como `AdminNotes`).
- Doador(a), ganhador(a), Fale Conosco e administração têm responsabilidades claras e não sobrepostas.
