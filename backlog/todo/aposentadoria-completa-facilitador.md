# Aposentadoria completa do conceito de facilitador

## Decisão

Em 22/08/2026 foi decidido aposentar o conceito de facilitador. A primeira etapa remove a função da experiência visível nos e-mails. A remoção estrutural fica para uma rodada própria, para não misturar revisão editorial com mudança de domínio e migração de dados.

## Por que importa

- O facilitador introduz um intermediário permanente onde doador(a) e ganhador(a) podem se coordenar diretamente.
- Parte do produto trata o papel como obrigatório e outra parte já aceita sua ausência, criando comportamento e código contraditórios.
- Jobs e e-mails já falharam quando um livro não tinha facilitador.
- Manter o conceito no domínio depois de aposentá-lo na experiência gera dívida silenciosa e incentiva novas dependências.

## Responsabilidades após a aposentadoria

- Dúvidas sobre entrega: contato direto entre doador(a) e ganhador(a).
- Dúvidas sobre a plataforma: Fale Conosco.
- Exceções operacionais: administração, sem apresentar uma pessoa como intermediária fixa da doação.

## Escopo da rodada futura

- [ ] Inventariar referências a `Facilitator`, `UserFacilitator` e equivalentes nos repositórios backend, frontend e agente.
- [ ] Remover o papel de contratos, view models, permissões, telas e filtros.
- [ ] Remover dependências em jobs, relatórios administrativos, notificações e testes.
- [ ] Definir e executar a migração das colunas e relacionamentos persistidos.
- [ ] Verificar dados existentes antes de remover a estrutura do banco.
- [ ] Atualizar documentação, skills e glossário que ainda descrevam o facilitador.
- [ ] Validar os fluxos completos de solicitação, escolha, envio, rastreio, recebimento, atraso e cancelamento sem intermediário.

## Critérios de aceite

- Nenhum fluxo depende de facilitador para concluir uma doação.
- Nenhuma API ou tela expõe o papel.
- Banco, entidades, jobs, testes e documentação não carregam referências obsoletas.
- Doador(a), ganhador(a), Fale Conosco e administração têm responsabilidades claras e não sobrepostas.
