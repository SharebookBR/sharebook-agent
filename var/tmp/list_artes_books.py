import sys
import json
import requests
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
    sys.exit(1)

base = 'https://sharebook.com.br/api'
headers = {'Authorization': f'Bearer {token}'}

# ID da categoria Artes
artes_id = '8c347027-8bcb-49a8-a755-df55eeb1affd'

# Tentar endpoint que lista livros com filtro
params = {'categoryId': artes_id, 'page': 1, 'itemsPerPage': 200}
r = requests.get(f'{base}/Book', headers=headers, params=params)
print('Status:', r.status_code)
if r.status_code != 200:
    print('Response:', r.text[:500])
    sys.exit(1)

data = r.json()
total = data['totalItems']
print(f'Total de livros na categoria Artes: {total}')
books = data['items']
for i, b in enumerate(books, 1):
    print(f"{i:3}. {b['title']} — {b['author']} (ID: {b['id']})")

# Salvar para referência
with open('artes_books.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)
print(f'\nLista salva em artes_books.json')

# Verificar se há mais páginas
if total > len(books):
    print(f'Atenção: há {total} livros, mas só foram listados {len(books)}. Precisa de paginação.')