# Metadados de memória episódica v1

O parser aceita ausência de frontmatter para preservar compatibilidade: memórias
sem `+++` na primeira linha são legadas, continuam válidas e são classificadas
explicitamente como `legacy`. Para **novas memórias**, o frontmatter TOML v1 é
obrigatório. Quando a primeira linha é `+++`, o documento assume o contrato v1
completo.

## Contrato

| Campo | Tipo TOML | Semântica |
|---|---|---|
| `schema_version` | inteiro `1` | Versão do contrato |
| `session_date` | data local sem aspas | Data da sessão (`YYYY-MM-DD`) |
| `title` | string não vazia | Título humano da memória |
| `model` | string não vazia | Modelo usado na sessão |
| `runtime` | string não vazia | Habitat operacional |
| `skills_used` | array de strings | Skills consultadas ou acionadas |
| `skills_missed` | array de strings | Skills que deveriam ter sido acionadas antes |
| `skills_updated` | array de strings | Skills alteradas na sessão |
| `facts_changed` | array de strings | Verdades atualizadas ou substituídas |
| `open_loops` | array de strings | Pendências ainda abertas |
| `durable_candidates` | array de strings | Aprendizados candidatos a consolidação |
| `supersedes` | array de strings | Memórias ou fatos que esta entrada substitui |
| `evidence` | array de strings | Paths, comandos ou referências verificáveis |

Os 13 campos acima são exatamente o contrato v1: todos são obrigatórios, arrays
podem estar vazios e campos desconhecidos tornam a memória inválida. Isso evita
que um typo vire dado silenciosamente perdido. Evolução do contrato exige uma
nova `schema_version`. A prosa Markdown depois do segundo `+++` não é
interpretada nem reescrita pelo parser.

## Uso

```powershell
C:\Users\raffa\AppData\Local\Programs\Python\Python312\python.exe `
  skills\doctrine\harness-governance\scripts\episodic_memory_metadata.py `
  memory\2026-08-20-minha-sessao.md
```

Saídas possíveis: `LEGACY`, `V1` ou `INVALID`. O processo retorna `1` se ao
menos um arquivo for inválido; memórias legadas retornam sucesso.
