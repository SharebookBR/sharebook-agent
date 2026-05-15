# Missão — Aposentar `position` como chave operacional no importer

## Objetivo
Eliminar o uso de `position` como chave operacional de escrita no importer do Sharebook, migrando os fluxos críticos para `id` e blindando contaminação entre sources.

## Contexto
O incidente de 2026-05-15 mostrou um problema estrutural no importer:
- `plan-set` e `status-set` escrevem por `position` global
- múltiplas sources podem ter o mesmo `position`
- isso permite vazamento cruzado de planejamento editorial, status e metadados entre catálogos diferentes

Na prática:
- `position` deve existir apenas como ordenação e referência humana local da source
- a identidade operacional única deve ser o `id`
- quando a ergonomia humana exigir `position`, a resolução precisa ser explícita para `id` ou, no mínimo, para `source_id + position`

## Escopo

### Backend / CLI / Worker
- Revisar todos os pontos de escrita no importer que hoje dependem de `position`
- Migrar writes críticos para `id`
- Onde `position` ainda for aceito por ergonomia, exigir escopo explícito da source e resolver internamente para `id`
- Proibir `UPDATE` e `SELECT` de escrita com `WHERE position = ?` solto

### Banco / camada de acesso
- Endurecer `set_plan`, `set_status` e operações afins para usar `id`
- Revisar helpers e consultas auxiliares para garantir que `position` nunca seja tratado como chave global
- Considerar constraint/guardrail adicional para evitar ambiguidade operacional em writes

### Dashboard / UX operacional
- Continuar mostrando `position` como número amigável da fila
- Expor `id` onde fizer sentido para auditoria, debug e comandos operacionais
- Evitar que telas ou automações incentivem uso cego de `position` sem source

### Skills / playbooks / agentes
- Atualizar skills do importer e de preparer editorial para deixar explícito:
  - `id` é a referência operacional confiável
  - `position` é local à source
  - ações de escrita não devem usar `position` solto
- Revisar prompts/skills que possam induzir agentes a operar como se `position` fosse identidade global

## Critérios de aceite
- `plan-set` e `status-set` não fazem mais write por `position` global
- não existe mais nenhum write crítico no importer usando `WHERE position = ?` sem escopo
- fluxo editorial/preparer não consegue contaminar outra source ao atuar em um item
- documentação operacional reflete a nova regra
- caso de teste cobrindo colisão de mesmo `position` em sources diferentes

## Ordem segura de execução
1. Mapear todos os pontos de escrita e seus chamadores
2. Mudar backend/camada de acesso para `id`
3. Ajustar CLI e automações
4. Atualizar skills/playbooks
5. Validar com caso real/sintético de colisão entre sources

## Leitura curta
`position` não é chave global. É só etiqueta humana. O importer precisa parar de tratar número de fila como identidade operacional.
