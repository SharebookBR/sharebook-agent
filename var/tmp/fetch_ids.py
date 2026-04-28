import subprocess
import json
import time

# Carregar lista da missão limpa
with open('mission_books_clean.json', 'r', encoding='utf-8') as f:
    books_by_subcat = json.load(f)

# Remover chave lixo
if 'Categoria pai - **Poesia & Artes** --- ### Subcategorias 1. Poesia Lírica 2. Poesia Reflexiva / Existencial 3. Poesia Moderna & Experimental 4. Poesia Dramática 5. Teatro & Dramaturgia 6. Épicos & Narrativas 7. Estética & Teoria --- ## 📊 Distribuição dos livros ### Poesia Lírica' in books_by_subcat:
    books = books_by_subcat.pop('Categoria pai - **Poesia & Artes** --- ### Subcategorias 1. Poesia Lírica 2. Poesia Reflexiva / Existencial 3. Poesia Moderna & Experimental 4. Poesia Dramática 5. Teatro & Dramaturgia 6. Épicos & Narrativas 7. Estética & Teoria --- ## 📊 Distribuição dos livros ### Poesia Lírica')
    books_by_subcat['Poesia Lírica'] = books

script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_book.py'

id_map = {}
for subcat_name, books in books_by_subcat.items():
    for b in books:
        key = f'{b["title"]}|{b["author"]}'
        if key in id_map:
            continue
        print(f'Buscando {b["title"]}...')
        cmd = ['python3', script_path, 'find', '--title', b['title'], '--author', b['author']]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
            data = json.loads(output)
            id_map[key] = data['id']
            print(f'  ID: {data["id"]}')
        except Exception as e:
            print(f'  ERRO: {e}')
        time.sleep(0.2)

# Salvar mapeamento
with open('book_ids.json', 'w', encoding='utf-8') as f:
    json.dump(id_map, f, ensure_ascii=False, indent=2)
print(f'\nTotal de IDs: {len(id_map)}')