import psycopg2

conn = psycopg2.connect(
    host="212.85.23.202", port=5432, dbname="sharebook_importer",
    user="sharebook_ai_rw", password="F%Ljy9oxTA3iR#npW%4W9iaSaJKU", sslmode="disable"
)
conn.autocommit = False
cur = conn.cursor()

# --- 1. ALTER TABLE ---
print("1. Adicionando coluna editorial_prompt...")
cur.execute("""
    ALTER TABLE importer.sources
    ADD COLUMN IF NOT EXISTS editorial_prompt TEXT
""")
print("   OK.")

# --- 2. Editorial prompts ---

PROMPT_BAIXELIVROS = """
# Preparo Editorial — baixelivros (Literatura Brasileira)

## Fonte
URL: https://www.baixelivros.com.br/biblioteca/literatura-brasileira
Perfil: clássicos e contemporâneos da literatura brasileira em domínio público ou livre distribuição.

## Categorias disponíveis (usar apenas folhas)

### Ficção
- Aventura       → `019d636c-efb8-76f6-b9f7-f35a2c5f8c09`
- Comédia        → `019d7db3-80ae-7e9d-99c7-db7381a35261`
- Fantasia       → `019d636c-ede8-7864-9a63-7b3e0766e01c`
- Ficção Científica → `019d636e-6573-704a-b093-7bc4c8c7c52a`
- Mistério/Suspense → `019d636e-6623-7c74-9c73-92b90bf3e2fa`
- Terror         → `019d636c-ed38-7396-af63-f9305793a31f`

### Drama
- Drama Moral / Ético      → `b5cdac27-d43b-4b99-96d9-285a8053e8bc`
- Drama Psicológico        → `00a5cf45-b334-453a-96c3-76a134224f64`
- Drama Satírico / Irônico → `123dfbc8-3c1a-43a3-8dc3-30d1409662a4`
- Drama Social             → `3a7cedce-b30a-4742-ad96-1213e8061bd9`
- Drama Trágico            → `234b8d86-7aef-41bb-a620-7bca29806b2e`

### Poesia & Artes
- Poesia Lírica                 → `019d9bf4-725d-7eb3-bf31-5dcd08c93053`
- Poesia Dramática              → `019d9bf5-01f5-7950-a763-9b04b24964f1`
- Poesia Moderna & Experimental → `019d9bf4-ffb6-7035-9b7a-e46e2780a999`
- Poesia Reflexiva / Existencial → `019d9bf4-fd73-7f5e-a501-6aae4dd46a9e`
- Épicos & Narrativas           → `019d9bf5-0745-7d13-ad0b-f771bc02d5d8`

### Outros
- Filosofia           → `bd088da6-cec6-443e-8bf4-06eb8a7456fd`
- Sociedade & Mundo   → `019d7e18-400e-7ad9-acb2-e5add68d9da7`

## Guia de decisão rápida
- Romance, narrativa pessoal, conflito interpessoal → Drama (escolher subtipo pelo tom)
- Aventura, ação, viagens → Ficção > Aventura
- Versos, poemas, odes → Poesia (escolher subtipo pelo estilo)
- Sátira, humor literário → Drama Satírico / Irônico ou Ficção > Comédia
- Ensaio filosófico, reflexão moral → Filosofia
- Dúvida entre drama e ficção → preferir Drama se o peso emocional dominar

## Sinopse
- 3 parágrafos.
- Tom literário, sem clichês ("Nesta obra emocionante...").
- Parágrafo 1: situar obra e autor no contexto da literatura brasileira.
- Parágrafo 2: o que o leitor encontra — conflito central, estilo, personagens marcantes.
- Parágrafo 3: por que vale ler hoje.
- Sem datas, sem "século XIX", sem "foi publicado em".
""".strip()

PROMPT_BAIXELIVROS_INFANTIL = """
# Preparo Editorial — baixelivros_infantil

## Fonte
URL: https://www.baixelivros.com.br/biblioteca/infantil
Perfil: literatura infantil e juvenil, foco em PDFs com ilustrações. A triagem entrega preview_pages (PNGs) e local_cover_path — usar esses artefatos como insumo primário.

## Ordem de uso dos artefatos (obrigatória)
1. preview_pages (PNGs das primeiras páginas)
2. local_cover_path (capa baixada)
3. context_text (texto extraído)
4. local_pdf_path (fallback manual — registrar "preparer-baixelivros (via manual pdf read)" no planned_by)

## Categorias disponíveis (usar apenas folhas)

### Infantil/Juvenil
- Bebês e Crianças Pequenas    → `019df04c-7a39-7bd3-8b72-c840e27f46e7`
- Valores e Emoções             → `019df04c-7a81-756b-932a-f424d916ef8e`
- Animais e Natureza            → `019df04c-7a72-729d-ae85-3c0c8de910f5`
- Educativos / Aprendizado      → `019df04c-7a4d-7d00-b11f-902eaca73586`
- Cultura Brasileira / Folclore → `019df04c-7a90-7247-bf39-ee4a160446e7`
- Clássicos Infantis            → `019df04c-79d2-7a9a-8f6e-49dc89cbda71`
- Aventuras e Fantasia          → `019df04c-7a5f-71e7-8c68-d7679d562d10`
- Inclusão e Diversidade        → `019e16e6-09db-7a64-9261-03e375f09192`
- Diversão e Humor              → `019df04c-7aab-7889-a6a5-7579e8594e4a`
- HQs e Mangás                  → `019df089-8268-73b1-871d-80bd395c752a`
- Poesia Infantil               → `019e3b3f-39df-7c06-8252-d402cb34ecff`

### Fallback (usar apenas se não couber em nenhuma infantil)
- Poesia Lírica      → `019d9bf4-725d-7eb3-bf31-5dcd08c93053`
- Drama Moral / Ético → `b5cdac27-d43b-4b99-96d9-285a8053e8bc`

## Guia de decisão rápida
- Aconchego, rotina, descoberta → Bebês e Crianças Pequenas
- Lição, ensino, hábito → Educativos / Aprendizado
- Sentimentos, medos, amizade → Valores e Emoções
- Bichos falantes, floresta → Animais e Natureza
- Saci, Curupira, lendas BR → Cultura Brasileira / Folclore
- Poemas, versos, rimas, cantigas, parlendas → Poesia Infantil
- HQ, tirinha, gibi, mangá → HQs e Mangás

## Sinopse
- 3 parágrafos.
- Tom leve, envolvente, adequado ao público infantil/familiar.
- Se context_text for muito pobre, mencionar isso com elegância — nunca inventar dados.
""".strip()

PROMPT_EBOOK_FOUNDATION = """
# Preparo Editorial — ebook_foundation

## Fonte
URL: https://raw.githubusercontent.com/EbookFoundation/free-programming-books/main/books/free-programming-books-pt_BR.md
Perfil: livros técnicos gratuitos em PT-BR. Foco em tecnologia. Sem preview_pages — insumo primário é o índice extraído do PDF.

## Regra absoluta: ler o índice antes de escrever
Antes de qualquer parágrafo, extrair e ler o índice completo do PDF.
Responder estas 3 perguntas com base no índice:
1. Estrutura: sequência de capítulos do começo ao fim?
2. Autoria: único autor, coletivo, institucional?
3. Diferencial inesperado: algo que não está no título?

O primeiro parágrafo da sinopse DEVE conter algo específico do índice.

## Categorias disponíveis (Tecnologia — usar apenas folhas)
- DevOps   → `019d636c-640a-7e2f-babd-c22d3b37c226` (Linux, shell, redes, Docker, Git, CI/CD)
- IA       → `019d636c-6365-74c5-9323-14be85d8b0a3` (ML, NLP, IA)
- Frontend → `019d636c-616a-7dcb-af70-77619c9dbaf5` (HTML, CSS, JavaScript)
- Backend  → `019d636c-5fdd-7505-9c76-e02944d9b618` (algoritmos, Java, C#, Python, PHP)
- Dados    → `019d636c-62c1-71e9-9a51-099d3304753e` (estruturas de dados, SQL, BI)
- Cloud    → `019d636c-6206-7f05-ade0-14ed095dd21c` (AWS, Azure, GCP)
- Geral    → `019dcbfc-0a09-702e-a0ab-090acb5597b6` (dúvida genuína entre subcategorias)

NUNCA usar "Conhecimento & Carreira" (`019d7e18-3fd3-7434-8033-28750c0881b5`) para livros de tecnologia.

## Deduplicação semântica
Dois PDFs diferentes podem ser duplicatas se cobrem o mesmo assunto no mesmo nível (básico/intermediário/avançado).
Regra: só é duplicata se mesmo nível + mesma categoria. Caso contrário, convivem.

## Sinopse
- 3 parágrafos. Máximo 2000 caracteres. Ideal: 1200–1800.
- Parágrafo 1: gancho com a dor do leitor + algo específico do índice.
- Parágrafo 2: conteúdo real (tópicos principais, descobertas inesperadas do índice).
- Parágrafo 3: valor do material, diferencial, o que o leitor leva.
- Proibido: subtítulos nos parágrafos, datas/épocas, "Neste livro", sinopse genérica.
- Revisar acentos antes de publicar.

## Capa
Gerada localmente com Pillow (cover_generate.py). Gerar 6 variações, analisar visualmente, escolher a melhor.
Paletas: tron, deep-ocean, lava, frost, matrix, sunset, graphite, cyber, forest, platinum.
planned_cover_mode deve ser 'source'. Detalhes da capa em metadata_json.
""".strip()

PROMPT_BAIXELIVROS_QUADRINHOS = """
# Preparo Editorial — baixelivros_quadrinhos

## Fonte
URL: https://www.baixelivros.com.br/biblioteca/quadrinhos
Perfil: HQs, gibis, tirinhas e graphic novels em domínio público ou livre distribuição.
A triagem entrega preview_pages (PNGs) e local_cover_path — usar como insumo primário.

## Ordem de uso dos artefatos (obrigatória)
1. preview_pages (PNGs das primeiras páginas — melhor atalho visual)
2. local_cover_path (capa baixada)
3. context_text (texto extraído)
4. local_pdf_path (fallback manual — registrar "preparer-quadrinhos (via manual pdf read)" no planned_by)

## Categorias disponíveis (usar apenas folhas)

### Principal
- HQs e Mangás → `019df089-8268-73b1-871d-80bd395c752a`

### Fallback (se o conteúdo claramente não for HQ — ex.: texto narrativo ilustrado)
- Aventuras e Fantasia (infantil) → `019df04c-7a5f-71e7-8c68-d7679d562d10`
- Clássicos Infantis             → `019df04c-79d2-7a9a-8f6e-49dc89cbda71`
- Diversão e Humor               → `019df04c-7aab-7889-a6a5-7579e8594e4a`

## Guia de decisão rápida
- HQ, gibi, tirinha, graphic novel, mangá → HQs e Mangás (padrão desta source)
- Narrativa ilustrada sem balões, estilo livro infantil → Aventuras e Fantasia ou Clássicos Infantis
- Humor, piadas em quadrinhos → Diversão e Humor

## Sinopse
- 3 parágrafos.
- Tom leve e visual: descrever o universo, personagens e estilo gráfico quando os previews permitirem.
- Parágrafo 1: apresentar o universo e o protagonista.
- Parágrafo 2: conflito ou aventura central, estilo visual e narrativo.
- Parágrafo 3: para quem é, por que vale ler/baixar.
- Nunca inventar dados se os previews forem insuficientes — mencionar com elegância.
""".strip()

# --- 3. UPDATE sources existentes ---
print("2. Populando editorial_prompt das sources existentes...")

updates = [
    ("baixelivros",           PROMPT_BAIXELIVROS),
    ("baixelivros_infantil",  PROMPT_BAIXELIVROS_INFANTIL),
    ("ebook_foundation",      PROMPT_EBOOK_FOUNDATION),
]
for name, prompt in updates:
    cur.execute(
        "UPDATE importer.sources SET editorial_prompt = %s WHERE name = %s",
        (prompt, name)
    )
    print(f"   {name}: {cur.rowcount} row(s) updated.")

# --- 4. INSERT baixelivros_quadrinhos ---
print("3. Criando source baixelivros_quadrinhos...")
cur.execute("""
    INSERT INTO importer.sources (name, url, enabled, created_at, updated_at, editorial_prompt)
    VALUES (%s, %s, %s, NOW(), NOW(), %s)
    ON CONFLICT DO NOTHING
""", (
    "baixelivros_quadrinhos",
    "https://www.baixelivros.com.br/biblioteca/quadrinhos",
    True,
    PROMPT_BAIXELIVROS_QUADRINHOS
))
print(f"   baixelivros_quadrinhos: {cur.rowcount} row(s) inserted.")

conn.commit()
print("\nDone. Tudo commitado.")
conn.close()
