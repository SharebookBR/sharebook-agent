import subprocess
import json
import sys
import os
import time

# Mapeamento subcategoria nome -> ID (já criadas)
subcat_map = {
    'Poesia Lírica': '019d9bf4-725d-7eb3-bf31-5dcd08c93053',
    'Poesia Reflexiva / Existencial': '019d9bf4-fd73-7f5e-a501-6aae4dd46a9e',
    'Poesia Moderna & Experimental': '019d9bf4-ffb6-7035-9b7a-e46e2780a999',
    'Poesia Dramática': '019d9bf5-01f5-7950-a763-9b04b24964f1',
    'Teatro & Dramaturgia': '019d9bf5-0442-70ff-a908-ba22d91225a4',
    'Épicos & Narrativas': '019d9bf5-0745-7d13-ad0b-f771bc02d5d8',
    'Estética & Teoria': '019d9bf5-09b0-722a-8b7a-91ae09669652'
}

# Carregar lista da missão
with open('mission_books.json', 'r', encoding='utf-8') as f:
    books_by_subcat = json.load(f)

script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_book.py'

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
        # Buscar ID do livro
        cmd = ['python3', script_path, 'find', '--title', title, '--author', author]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
            data = json.loads(output)
            book_id = data['id']
            # Atualizar categoria
            update_cmd = ['python3', script_path, 'update', '--id', book_id, '--category-id', subcat_id]
            update_output = subprocess.check_output(update_cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
            print(f'    -> atualizado para {subcat_name}')
            results.append({'title': title, 'book_id': book_id, 'subcat_id': subcat_id})
            time.sleep(0.3)  # evitar rate limit
        except subprocess.CalledProcessError as e:
            error_msg = e.output[:200]
            print(f'    ERRO: {error_msg}')
            errors.append({'title': title, 'error': error_msg})
        except Exception as e:
            print(f'    EXCEÇÃO: {e}')
            errors.append({'title': title, 'error': str(e)})

print('\n=== RESUMO ===')
print(f'Livros migrados: {len(results)}')
print(f'Erros: {len(errors)}')
if errors:
    print('Erros detalhados:')
    for e in errors:
        print(f'  - {e["title"]}: {e["error"]}')

# Salvar log
with open('migration_log.json', 'w', encoding='utf-8') as f:
    json.dump({'results': results, 'errors': errors}, f, ensure_ascii=False, indent=2)
print('\nLog salvo em migration_log.json')