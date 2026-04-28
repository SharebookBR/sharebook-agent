import re
import json

with open('/data/workspace/sharebook-agent/missions/03-refatoracao-categoria-artes.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Extrair seções de subcategorias
pattern = r'### (.*?) \((?:\d+)\)\s*\n(.*?)(?=\n###|\n---|\n##|\n\Z)'
sections = re.findall(pattern, content, re.DOTALL)

books_by_subcat = {}
for subcat, lines in sections:
    subcat = subcat.strip()
    # Encontrar linhas com traço
    book_lines = re.findall(r'-\s+(.*?)\s*—\s*(.*?)\s*$', lines, re.MULTILINE)
    books = []
    for title, author in book_lines:
        books.append({'title': title.strip(), 'author': author.strip()})
    if books:
        books_by_subcat[subcat] = books

# Imprimir
for subcat, books in books_by_subcat.items():
    print(f'{subcat} ({len(books)}):')
    for b in books:
        print(f'  - {b["title"]} — {b["author"]}')
    print()

# Salvar JSON
with open('mission_books.json', 'w', encoding='utf-8') as f:
    json.dump(books_by_subcat, f, ensure_ascii=False, indent=2)
print('Salvo em mission_books.json')

# Total de livros
total = sum(len(books) for books in books_by_subcat.values())
print(f'Total de livros na missão: {total}')