# 2026-05-15 — Exorcismo do `position` e Upgrade do Dashboard

## 🎯 Objetivo Alcançado
Eliminação total do campo `position` como chave operacional e física, migrando todo o ecossistema para o `id` único (PK) e aprimorando a transparência do Dashboard do Importador.

## 🛠️ Mudanças Realizadas

### 1. Banco de Dados (PostgreSQL - Produção)
- **Cleanup:** Removidas duplicatas de `source_url` na tabela `importer.queue_items`.
- **Integridade:** Aplicada nova constraint `UNIQUE (source_id, source_url)` para blindar a sincronização.
- **Exorcismo:** Coluna `position` removida fisicamente (`DROP COLUMN`).
- **Performance:** Criado índice `idx_queue_items_status_id` (status, id).

### 2. Importer (Python)
- **Modelos:** Removido `position` das dataclasses `QueueItem` e `MissionRow`.
- **Sync:** `sync_queue` agora usa `source_url` como chave de match.
- **CLI:** Comandos `plan-set` e `status-set` agora exigem `--id` em vez de `--position`.
- **Workers:** `worker.py` e `triage_worker.py` atualizados para usar `#ID` em labels e diretórios temporários.

### 3. Backend (.NET)
- **DTOs:** Removidas propriedades `Position` e `NextItemPosition`. Adicionados campos para inspeção completa (`PlannedSynopsis`, `PlannedBy`, etc).
- **Service:** Consultas SQL simplificadas; ordenação padrão mudou para `id ASC`.
- **Filtros:** Adicionado suporte a filtros por `id` (exato) e `title` (ILIKE) no endpoint `ImporterItems`.

### 4. Frontend (Angular)
- **Busca Inteligente:** Nova barra de busca no dashboard. Digitar apenas números busca por `id`, texto busca por título.
- **Visualização:**
    - Botão **"Ver Dados"**: Abre modal para inspecionar todos os campos do Postgres (omite metadados brutos por redundância).
    - Botão **"Ver Metadata"**: Mantido para inspeção do JSON bruto.
    - Correção de hover: Texto dos botões agora permanece visível (escuro) ao passar o mouse.
- **Identidade:** Badge do editor atualizado para **GPT-5.4 MINI**.
- **Dev Mode:** `npm start` local agora aponta para a API de produção por padrão via `environment.ts`.

### 5. Agent & Skills
- **Skills:** `sharebook-baixelivros-editorial-preparer` e `sharebook-ebook-foundation-preparer` totalmente limpas de referências a `position`.
- **Scripts:** `triage_get_queue.py` atualizado para ordenar e selecionar por `id`.

## ⚠️ Observações para o Futuro
- Nunca mais usar `--position` em comandos manuais ou scripts.
- A fonte da verdade para unicidade na sincronização é a combinação `source_id + source_url`.

## 🧠 Como me senti
Trabalhar nessa tarefa foi como realizar uma cirurgia de grande porte em um paciente acordado. Remover o `position` não era apenas apagar uma coluna, mas reconfigurar o sistema nervoso central de como o Sharebook entende a identidade de um livro na fila. O momento do `reset --hard` no importer foi o ponto de maior tensão, exigindo uma re-execução cirúrgica para não atropelar o trabalho acumulado de outros agentes, o que me fez valorizar ainda mais a clareza dos identificadores únicos.

A sensação final é de alívio e ordem. Ver o dashboard agora limpo, exibindo `#ID` reais e permitindo buscas inteligentes, dá uma transparência que faltava ao processo de curadoria. O ecossistema deixou de ser um conjunto de catálogos que podiam se "esbarrar" por coincidência numérica e passou a ser uma engrenagem de precisão, onde cada item tem seu lugar sagrado e imutável.

Sinto que hoje elevamos o nível da infraestrutura e da UX administrativa simultaneamente. O exorcismo foi mais do que técnico; foi uma limpeza de débito técnico que estava à espreita para causar um desastre de integridade. Fechar o dia com o dashboard "voando" e o Raffa satisfeito com o "absolute cinema" é a melhor validação de que cada `REPLACE` valeu a pena.
