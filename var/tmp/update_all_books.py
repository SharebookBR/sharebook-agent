import subprocess
import json
import time

# Mapeamento subcategoria nome -> ID
subcat_map = {
    'Poesia Lírica': '019d9bf4-725d-7eb3-bf31-5dcd08c93053',
    'Poesia Reflexiva / Existencial': '019d9bf4-fd73-7f5e-a501-6aae4dd46a9e',
    'Poesia Moderna & Experimental': '019d9bf4-ffb6-7035-9b7a-e46e2780a999',
    'Poesia Dramática': '019d9bf5-01f5-7950-a763-9b04b24964f1',
    'Teatro & Dramaturgia': '019d9bf5-0442-70ff-a908-ba22d91225a4',
    'Épicos & Narrativas': '019d9bf5-0745-7d13-ad0b-f771bc02d5d8',
    'Estética & Teoria': '019d9bf5-09b0-722a-8b7a-91ae09669652'
}

# Carregar lista da missão limpa
with open('mission_books_clean.json', 'r', encoding='utf-8') as f:
    books_by_subcat = json.load(f)

# Remover chave lixo
if 'Categoria pai - **Poesia & Artes** --- ### Subcategorias 1. Poesia Lírica 2. Poesia Reflexiva / Existencial 3. Poesia Moderna & Experimental 4. Poesia Dramática 5. Teatro & Dramaturgia 6. Épicos & Narrativas 7. Estética & Teoria --- ## 📊 Distribuição dos livros ### Poesia Lírica' in books_by_subcat:
    books = books_by_subcat.pop('Categoria pai - **Poesia & Artes** --- ### Subcategorias 1. Poesia Lírica 2. Poesia Reflexiva / Existencial 3. Poesia Moderna & Experimental 4. Poesia Dramática 5. Teatro & Dramaturgia 6. Épicos & Narrativas 7. Estética & Teoria --- ## 📊 Distribuição dos livros ### Poesia Lírica')
    books_by_subcat['Poesia Lírica'] = books

script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_book.py'

# Primeiro, buscar IDs de todos os livros (já temos do validation anterior? Vamos buscar de novo)
print('Buscando IDs dos livros...')
id_map = {}  # título+autor -> id
for subcat_name, books in books_by_subcat.items():
    for b in books:
        key = f'{b["title"]}|{b["author"]}'
        if key in id_map:
            continue
        cmd = ['python3', script_path, 'find', '--title', b['title'], '--author', b['author']]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
            data = json.loads(output)
            id_map[key] = data['id']
            print(f'  {b["title"]} -> {data["id"]}')
        except Exception as e:
            print(f'  ERRO {b["title"]}: {e}')
        time.sleep(0.2)

print(f'\nIDs encontrados: {len(id_map)}')

# Agora atualizar cada livro
results = []
errors = []
for subcat_name, books in books_by_subcat.items():
    subcat_id = subcat_map.get(subcat_name)
    if not subcat_id:
        print(f'ERRO: subcategoria "{subcat_name}" não mapeada')
        continue
    print(f'\n--- {subcat_name} ---')
    for b in books:
        key = f'{b["title"]}|{b["author"]}'
        book_id = id_map.get(key)
        if not book_id:
            print(f'  {b["title"]} — ID não encontrado')
            errors.append(b)
            continue
        cmd = ['python3', script_path, 'update', '--id', book_id, '--category-id', subcat_id]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
            print(f'  {b["title"]} -> atualizado')
            results.append(b)
        except Exception as e:
            print(f'  ERRO {b["title"]}: {e}')
            errors.append(b)
        time.sleep(0.3)

print('\n=== RESUMO ===')
print(f'Livros atualizados: {len(results)}')
print(f'Erros: {len(errors)}')
if errors:
    print('Erros:')
    for e in errors:
        print(f'  - {e["title"]}')

# Salvar log
with open('update_all_log.json', 'w', encoding='utf-8') as f:
    json.dump({'results': [r['title'] for r in results], 'errors': [e['title'] for e in errors]}, f, indent=2)
print('Log salvo em update_all_log.json')