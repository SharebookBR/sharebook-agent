# Queries úteis (read-only)

## Top livros mais baixados

```sql
SELECT
  "Title" AS titulo,
  "Author" AS autor,
  "DownloadCount" AS downloads
FROM "Books"
ORDER BY "DownloadCount" DESC NULLS LAST, "Title" ASC
LIMIT 10;
```

## Top ebooks mais baixados

```sql
SELECT
  "Title" AS titulo,
  "Author" AS autor,
  "DownloadCount" AS downloads
FROM "Books"
WHERE "Type" = 'Eletronic'
ORDER BY "DownloadCount" DESC NULLS LAST, "Title" ASC
LIMIT 10;
```

## Livros criados por dia (últimos 30 dias)

```sql
SELECT
  date_trunc('day', "CreationDate")::date AS dia,
  COUNT(*) AS livros
FROM "Books"
WHERE "CreationDate" >= now() - interval '30 days'
GROUP BY 1
ORDER BY 1 DESC;
```

## Jobs recentes

```sql
SELECT
  "CreationDate" AS criado_em,
  "Type" AS tipo,
  "Message" AS mensagem
FROM "JobHistories"
ORDER BY "CreationDate" DESC
LIMIT 50;
```

## Descoberta de schema

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY 1, 2;
```

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_schema='public' AND table_name='Books'
ORDER BY ordinal_position;
```
