import requests
import json
import time
from pathlib import Path

env_path = Path(__file__).parent.parent.parent / '.env'
env = {}
with open(env_path) as f:
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

token = env.get('SHAREBOOK_PROD_ACCESS_TOKEN')
if not token:
    print('Token não encontrado')
    exit(1)

base = 'https://api.sharebook.com.br/api'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

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

results = []
errors = []

for subcat_name, books in books_by_subcat.items():
    subcat_id = subcat_map.get(subcat_name)
    if not subcat_id:
        print(f'ERRO: subcategoria "{subcat_name}" não mapeada')
        continue
    print(f'\n--- {subcat_name} ({len(books)} livros) ---')
    for b in books:
        title = b['title']
        author = b['author']
        print(f'  {title} — {author}')
        # Buscar livro via API (endpoint de busca)
        params = {'title': title, 'author': author}
        r = requests.get(f'{base}/Book', headers=headers, params=params)
        if r.status_code != 200:
            print(f'    ERRO busca: {r.status_code} {r.text[:100]}')
            errors.append({'title': title, 'error': f'busca {r.status_code}'})
            continue
        data = r.json()
        items = data.get('items', [])
        if not items:
            print('    Livro não encontrado')
            errors.append({'title': title, 'error': 'não encontrado'})
            continue
        book = items[0]
        book_id = book['id']
        # Atualizar categoria via PUT /Book/{id}
        payload = {'categoryId': subcat_id}
        r = requests.put(f'{base}/Book/{book_id}', headers=headers, json=payload)
        if r.status_code == 200:
            print(f'    -> atualizado')
            results.append({'title': title, 'book_id': book_id, 'subcat_id': subcat_id})
        else:
            print(f'    ERRO update: {r.status_code} {r.text[:100]}')
            errors.append({'title': title, 'error': f'update {r.status_code}'})
        time.sleep(0.2)

print('\n=== RESUMO ===')
print(f'Livros migrados: {len(results)}')
print(f'Erros: {len(errors)}')

# Salvar log
with open('migration_api_log.json', 'w', encoding='utf-8') as f:
    json.dump({'results': results, 'errors': errors}, f, ensure_ascii=False, indent=2)
print('Log salvo em migration_api_log.json')

# Verificar total
if len(results) == 30:
    print('\n✅ TODOS os 30 livros foram migrados para as subcategorias!')
else:
    print(f'\n⚠️  Apenas {len(results)}/30 migrados. Verifique erros.')