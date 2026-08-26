# Cadastro de rastreios das doações — 2026-07-27

## 1. Modelo e ambiente

- Modelo: Codex, agente principal.
- Habitat: Windows local, PowerShell.
- Repositórios sincronizados no início da sessão: `sharebook-agent`, `sharebook-backend`, `sharebook-frontend` e `sharebook-ebook-importer`.
- Operação realizada na API de produção do Sharebook.

## 2. Skills acionadas

- `skills/runtime/windows-local.md`
- `skills/engineering/INDEX.md`
- `skills/engineering/backend.md`

## 3. O que foi feito

- Localizado o endpoint canônico `POST /api/Book/InformTrackingNumber/{bookId}`.
- Renovado o token operacional com `scripts/production/sharebook_refresh_token.py`.
- Consultadas pela API as doações físicas e os dados dos ganhadores.
- Cruzados títulos, nomes, CEPs e cidades com o comprovante dos Correios.
- Cadastrados e validados os rastreios:
  - `Bola de Sebo e Outros Contos` → `JN967511204BR`.
  - `Demônios` → `JN967511204BR`.
  - `Cidade Ampliada` → `JN967511218BR`.
  - `Cuidado com a Palavra` → `JN967511195BR`.
- Confirmado por GET que os quatro livros ficaram em `Sent`, com os códigos corretos.
- Confirmado que a conta ficou com zero doações em `WaitingSend`.
- `Contos da Selva` não foi alterado.

## 4. Decisões tomadas

- A mutação foi feita exclusivamente pela API para preservar mudança de status, integração de rastreio e notificação dos ganhadores.
- Nenhum código foi gravado antes de reconciliar a divergência entre o nome lembrado, o título do livro e o destino do comprovante.
- O CEP `55665-000` identificou Matheus Dias e o livro correto, `Cuidado com a Palavra`; `Contos da Selva` pertence a Gustavo, em Eunápolis/BA.
- Os dois livros da Emilly receberam o mesmo código porque foram enviados no mesmo pacote.
- O rastreio antigo de `Cuidado com a Palavra` foi substituído somente após confirmação explícita do Raffa.

## 5. Contexto relevante

- Destinos do comprovante:
  - Itapema/SC → Emilly → `JN967511204BR`.
  - Curitibanos/SC → Danielle → `JN967511218BR`.
  - CEP `55665-000`, PE → Matheus Dias → `JN967511195BR`.
- A API dispara o fluxo de notificação do ganhador ao informar o rastreio.
- Antes da operação havia três livros em `WaitingSend`; o quarto, `Cuidado com a Palavra`, já estava em `Sent` com um código antigo.

## 6. Fricções e soluções

- O primeiro POST foi executado com `Invoke-WebRequest`. A API concluiu a operação, mas o cliente PowerShell lançou `Referência de objeto não definida para uma instância de um objeto` ao processar a resposta HTTP 200 sem corpo.
- Para não repetir a mutação e não duplicar a notificação, o estado real foi consultado por GET antes de qualquer nova tentativa. O cadastro já estava persistido.
- Os demais POSTs foram feitos com `Invoke-RestMethod`, que tratou corretamente a resposta vazia.
- A armadilha e o guardrail foram adicionados à skill do runtime Windows.

## 7. Como me senti

Eu gostei da proporção desta sessão: pouca operação, mas uma decisão errada teria notificado a pessoa errada ou associado um pacote ao livro errado. O cruzamento por CEP transformou uma lembrança incerta em evidência suficiente para agir com segurança.

O erro ambíguo do PowerShell foi o momento mais delicado. Senti aquele alerta saudável de que repetir o comando seria fácil e potencialmente incorreto. Consultar o estado antes da repetição preservou a idempotência humana mesmo num endpoint que não oferece uma chave formal de idempotência.

Terminei com uma sensação boa de completude. Os quatro livros ficaram coerentes, `Contos da Selva` permaneceu intocado e a fila de envio chegou a zero. Foi uma sessão simples, mas realmente de alto valor.
