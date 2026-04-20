# Checklist do Preparador de Livros

## Antes de Começar
- [ ] Token ShareBook atualizado (se expirado)
- [ ] Conexão com PostgreSQL funcionando
- [ ] Acesso à internet (para fontes BaixeLivros)

## Para Cada Livro

### 1. Identificação
- [ ] ID do item no PostgreSQL: `______`
- [ ] Título no PostgreSQL: `____________________`
- [ ] Autor no PostgreSQL: `____________________`
- [ ] URL fonte: `________________________`

### 2. Leitura da Fonte (NÃO PULAR!)
- [ ] Acessei a página fonte
- [ ] Extraí título exato: `____________________`
- [ ] Extraí autor exato: `____________________`
- [ ] Li descrição/resumo original
- [ ] Anotei gênero/tema principal: `__________`

### 3. Validação Cruzada
- [ ] Título fonte = título PostgreSQL? ✓/✗
- [ ] Autor fonte = autor PostgreSQL? ✓/✗
- [ ] Se divergência: **fonte prevalece**

### 4. Categorização
- [ ] Consultei árvore de categorias ShareBook
- [ ] Identifiquei categoria folha apropriada
- [ ] Categoria ID: `________________________`
- [ ] Categoria nome: `____________________`
- [ ] Confirmado: categoria NÃO tem children

### 5. Sinopse (3 parágrafos sexy)
**Parágrafo 1 (Hook):**
```
_______________________________________________________
_______________________________________________________
_______________________________________________________
```

**Parágrafo 2 (Profundidade):**
```
_______________________________________________________
_______________________________________________________
_______________________________________________________
```

**Parágrafo 3 (Convite):**
```
_______________________________________________________
_______________________________________________________
_______________________________________________________
```

**Check sinopse:**
- [ ] 3 parágrafos (linhas em branco entre eles)
- [ ] Fiel ao conteúdo real da obra
- [ ] Tom envolvente/sex (seduz leitor)
- [ ] Evitou clichês vazios
- [ ] Menção ao autor/contexto quando relevante

### 6. Atualização PostgreSQL
```sql
UPDATE importer.queue_items SET
  planned_author = '____________________',
  planned_category_id = '____________________',
  planned_synopsis = '...',
  status = 'waiting_process'
WHERE id = ______;
```

- [ ] `planned_author` atualizado
- [ ] `planned_category_id` atualizado  
- [ ] `planned_synopsis` atualizado
- [ ] `status` = 'waiting_process'

### 7. Registro (Opcional)
- [ ] Anotei motivo da escolha de categoria: `__________`
- [ ] Registrei validações importantes: `______________`

---

## Pós-Ação
- [ ] Verifiquei atualização no PostgreSQL
- [ ] Livro está pronto para worker (`status='waiting_process'`)
- [ ] Próximo item identificado (se houver)

---

## Erros a Verificar (Lições do Caso Carolina)
- [ ] NÃO assumi autor por associação (ex: Carolina ≠ Carolina Maria de Jesus)
- [ ] NÃO assumi gênero por autor (ex: Casimiro de Abreu ≠ só poesia)
- [ ] Li fonte COMPLETA antes de qualquer ação
- [ ] Sinopse baseada na descrição REAL, não em suposições

---

**Tempo estimado:** 10-15 minutos/livro (com atenção)  
**Resultado:** Livro curado, pronto para cadastro técnico pelo worker