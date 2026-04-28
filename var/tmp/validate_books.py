import subprocess
import json
import sys
import os

# Carregar lista da missão
with open('mission_books.json', 'r', encoding='utf-8') as f:
    books_by_subcat = json.load(f)

script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_book.py'

results = {}
missing = []
for subcat, books in books_by_subcat.items():
    results[subcat] = []
    for b in books:
        title = b['title']
        author = b['author']
        print(f'Buscando: {title} — {author}')
        # Executar find
        cmd = ['python3', script_path, 'find', '--title', title, '--author', author]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
            data = json.loads(output)
            if data.get('id'):
                b['id'] = data['id']
                b['categoryId'] = data.get('categoryId')
                b['category'] = data.get('category')
                results[subcat].append(b)
                print(f'  OK: ID {data["id"]}, categoria {data.get("category")}')
            else:
                print(f'  Livro não encontrado')
                missing.append((subcat, title, author))
        except subprocess.CalledProcessError as e:
            print(f'  Erro: {e.output[:200]}')
            missing.append((subcat, title, author))
        except json.JSONDecodeError:
            print(f'  Resposta inválida')
            missing.append((subcat, title, author))
        except Exception as e:
            print(f'  Exceção: {e}')
            missing.append((subcat, title, author))

# Salvar resultados
with open('validated_books.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n=== RESUMO ===')
total_found = sum(len(books) for books in results.values())
print(f'Livros encontrados: {total_found}/30')
if missing:
    print('Livros não encontrados:')
    for subcat, title, author in missing:
        print(f'  - {title} — {author} ({subcat})')

# Verificar categoria
artes_id = '8c347027-8bcb-49a8-a755-df55eeb1affd'
wrong_cat = []
for subcat, books in results.items():
    for b in books:
        if b.get('categoryId') != artes_id:
            wrong_cat.append((b['title'], b['category']))
if wrong_cat:
    print('\nLivros fora da categoria Artes:')
    for title, cat in wrong_cat:
        print(f'  - {title} ({cat})')
else:
    print('\nTodos os livros encontrados estão na categoria Artes.')