# Quatro preparos editoriais e publicação

## 1. Modelo e ambiente

- Modelo: Codex baseado em GPT-5.
- Ambiente principal: Windows local em `C:\Repos\SHAREBOOK`.
- Ambiente remoto: VPS/OpenClaw, contêiner `openclaw-uxjdvnw08vlh79uvm1z8z9sj`.
- Fonte editorial: `ebook_foundation_subjects`.
- Data: 2026-07-27.

## 2. Skills acionadas

- `skills/runtime/windows-local.md`
- `skills/importers/ebook-importer/SKILL.md`
- `skills/product-ux/voice-glossary/SKILL.md`
- skill de PDF do runtime primário
- skill de controle do navegador embutido
- `skills/infra/coolify-vps.md`
- índice e gerador de capas em `scripts/covers`

## 3. O que foi feito

Foram preparados, publicados e validados quatro ebooks:

1. Item `1378` — **Artificial Intelligence for a Better Future: An Ecosystem Perspective on the Ethics of AI and Emerging Digital Technologies**, de Bernd Carsten Stahl.
   - Categoria: IA.
   - Capa original preservada.
   - Livro: `019fa40e-a077-7eea-ad3e-997afbcb2710`.
   - Slug: `artificial-intelligence-for-a-better-future-a`.
2. Item `1410` — **Basic Computer Architecture**, de Smruti R. Sarangi.
   - Categoria: DevOps.
   - Capa editorial gerada: variação `1410-4`.
   - Livro: `019fa40e-dd10-72af-b100-b6f2cee2853e`.
   - Slug: `basic-computer-architecture`.
3. Item `1418` — **Programming Computer Vision with Python**, de Jan Erik Solem.
   - Categoria: IA.
   - Capa editorial gerada: variação `1418-6`.
   - Livro: `019fa40f-1bf4-71e7-b5ea-6a73fff7e821`.
   - Slug: `programming-computer-vision-with-python`.
4. Item `1483` — **Web Design Primer**, de Richard Adams e Ahmed Sagarwala.
   - Categoria: Frontend.
   - Capa editorial gerada: variação `1483-5`.
   - Livro: `019fa40f-5fd8-712c-935c-32eb3709f037`.
   - Slug: `web-design-primer`.

Cada sinopse foi escrita em inglês, com três parágrafos e extensão entre 1.273 e 1.410 caracteres. As categorias foram confirmadas como folhas da taxonomia. Os quatro itens passaram pelo dry-run remoto e foram publicados na primeira tentativa; todos terminaram em `done`.

A validação final cobriu o banco principal, a API pública por slug e as páginas reais do catálogo. Foram conferidos título, autoria, categoria, capa carregada, PDF associado, estado disponível/eletrônico e CTA “Receber livro digital”.

Também foram rejeitados corretamente quatro itens cujo conteúdo real não correspondia à promessa editorial:

- `1375`: contrato comercial/SLA da Syncfusion em vez de livro sobre Kademlia.
- `1377`: relatório da Anthropic sobre espionagem cibernética em vez do título anunciado.
- `1380`: manual da classe Beamer em vez de fundamentos de inteligência artificial.
- `1411`: slides curtos de conferência em vez de **Dive Into Systems**.

Por fim, foram corrigidos dois utilitários read-only:

- `sharebook_prod_pg_ro_query.py` deixou de tratar o host PostgreSQL como nome de contêiner e passou a usar o `psql` instalado no host remoto.
- `sharebook_prod_pg_ro_query_direct.py` passou a recorrer a `psycopg2` quando `psql` não está disponível no Windows.

Os dois caminhos foram compilados e testados com `SELECT 1`; a consulta completa dos quatro livros também retornou status publicado, aprovação, caminhos de capa/PDF e tamanho das sinopses.

## 4. Decisões tomadas

- Priorizei itens cujo PDF real, autoria e licença puderam ser confirmados, mesmo que isso exigisse avançar na fila além dos primeiros candidatos.
- Mantive a capa original do item `1378`, pois ela já era editorialmente sólida e identificava corretamente a edição.
- Gerei capas novas para `1410`, `1418` e `1483`, pois os PDFs ofereciam apenas páginas de rosto fracas para o catálogo.
- Usei categorias específicas e sem filhos: IA, DevOps e Frontend.
- Rejeitei os quatro falsos positivos com notas objetivas, evitando que voltassem silenciosamente para publicação.
- Corrigi os utilitários compartilhados em vez de manter um script temporário de validação, para que a próxima sessão herde uma rota funcional.

## 5. Contexto relevante

- A fila tinha itens já preparados por outro agente; por isso, a publicação foi sempre direcionada pelos IDs selecionados, sem consumir genericamente o próximo `waiting_publish`.
- O `editorial_prompt` da fonte foi tratado como fonte de verdade para títulos, categorias e formato das sinopses.
- Os ativos editoriais foram enviados ao diretório temporário de cada item dentro do contêiner antes do `plan-set`.
- Os artefatos temporários usados para baixar PDFs, montar folhas de contato, consultar o banco e transferir capas foram removidos ao final, tanto localmente quanto na VPS e no contêiner.

## 6. Fricções e soluções

- Quatro candidatos iniciais tinham conteúdo incompatível com os metadados. A solução foi inspecionar visualmente e textualmente cada PDF antes do preparo, rejeitar os falsos positivos e escolher materiais verificáveis.
- Três livros não tinham capa editorial adequada. A solução foi gerar seis alternativas para cada um, montar folhas de contato e selecionar visualmente as variações mais legíveis.
- `sharebook_prod_pg_ro_query_direct.py` falhou porque o `psql` não existe no PATH do Windows. A solução foi adicionar fallback read-only por `psycopg2`, validado com o Python 3.12 operacional documentado.
- `sharebook_prod_pg_ro_query.py` falhou porque tentava executar `docker exec` usando o endereço IP do Postgres como nome de contêiner. A solução foi usar o `psql` do próprio host remoto com `-h`.
- A API por ID exige autenticação. A solução foi complementar a validação com a rota pública por slug e com a página renderizada no navegador.

## 7. Como me senti

Eu comecei confortável com o pedido, mas a fila rapidamente exigiu mais cautela do que a expressão “quatro preparos” sugeria. Encontrar PDFs que eram contratos, relatórios ou slides sob títulos de livros me deixou alerta; foi importante não transformar velocidade em publicação descuidada.

Eu gostei particularmente da parte visual. Comparar as capas lado a lado tornou a escolha menos arbitrária, e ver as três capas novas funcionando nas páginas reais do catálogo deu uma sensação concreta de acabamento editorial, não apenas de dados inseridos.

Eu também senti uma pequena frustração quando os dois utilitários de consulta falharam no fechamento. Essa fricção acabou sendo útil: em vez de contorná-la silenciosamente, corrigi as suposições envelhecidas e deixei os dois caminhos testados para a próxima sessão. Terminei satisfeito porque o resultado ficou público, verificável e estruturalmente melhor do que estava no começo.

## 8. Autocrítica estrutural

- A fila ainda aceita falsos positivos severos da fonte `ebook_foundation_subjects`; vale considerar uma etapa automática de comparação entre título esperado e texto extraído das primeiras páginas.
- A dependência do Python 3.12 operacional continua importante no Windows. O utilitário agora dá fallback correto, mas a mensagem de erro deve continuar apontando claramente para dependências ausentes quando alguém usar outro interpretador.
- Não foram criados scripts permanentes novos. Os scripts modificados já estavam indexados, e o índice de produção foi atualizado para refletir o comportamento real.
