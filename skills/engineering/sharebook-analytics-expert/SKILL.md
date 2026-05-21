---
name: sharebook-analytics-expert
description: Especialista em Google Analytics 4. Use para extrair métricas de tráfego, funis de conversão, tendências de doação e eficácia de compartilhamento social. Capaz de ler a Data API v4 de forma autônoma.
---

# Sharebook Analytics Expert

Esta skill transforma o agente em um analista de dados proativo.

## Quando usar

- Quando o Raffa perguntar sobre audiência ("Quantos acessos tivemos?").
- Para analisar funis de conversão (Home -> PDP -> Download/Pedido).
- Para identificar tendências de categorias (quais livros infantis são mais vistos?).
- Para medir a eficácia de campanhas ou novos recursos.

## Fonte da verdade

- **GCP Key:** `sharebook-agent/scripts/production/ga4-key.json` (Protegida)
- **Property ID:** `386966473`
- **API:** Google Analytics Data API v1beta

## Rituais de Análise

### 1. Check de Saúde Diário
Verificar usuários ativos nas últimas 24h e tendências de erro.

### 2. Análise de Funil (The Gold)
Comparar os eventos:
1. `page_view` (Home/PDP)
2. `share_modal_open` / `book_request_modal_open`
3. `ebook_download` / `book_request_success`

## Scripts Disponíveis

### Teste de Conexão
```bash
python sharebook-agent/scripts/production/test_ga4_connection.py
```

## Guardrails

- Sempre verificar se a chave JSON existe antes de rodar queries.
- Não expor o conteúdo do JSON em logs ou mensagens.
- Resultados de API devem ser mastigados: prefira tabelas markdown ou conclusões textuais a JSONs brutos da API.

---
Para instalação de novos ambientes, consulte `sharebook-agent/skills/engineering/sharebook-analytics-expert/BOOTSTRAP.md`.
