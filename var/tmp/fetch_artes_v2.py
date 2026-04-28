import os
import sys
import json
import requests
from pathlib import Path

env_path = Path(__file__).parent.parent.parent / '.env'
env = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                k, v = line.split('=', 1)
                env[k] = v

token = env.get('SHAREBOOK_PROD_ACCESS_TOKEN')
if not token:
    print('Token não encontrado')
    sys.exit(1)

base = 'https://sharebook.com.br/api'
headers = {'Authorization': f'Bearer {token}'}

# 1. Buscar lista de categorias (endpoint simples)
r = requests.get(f'{base}/Category', headers=headers)
if r.status_code != 200:
    print('Falha ao buscar categorias:', r.status_code, r.text)
    sys.exit(1)

categories = r.json()
print('Categorias:')
for cat in categories:
    print(f"  {cat['id']} - {cat['name']} (pai: {cat.get('parentCategoryId', 'Nenhum')})")

# 2. Encontrar Artes
artes = None
for cat in categories:
    if cat['name'] == 'Artes':
        artes = cat
        break

if not artes:
    print('Categoria Artes não encontrada')
    sys.exit(1)

print(f"\nCategoria Artes encontrada:")
print(f"  ID: {artes['id']}")
print(f"  Nome: {artes['name']}")
print(f"  Slug: {artes.get('slug', 'N/A')}")
print(f"  Pai: {artes.get('parentCategoryId', 'Nenhum')}")

# 3. Buscar livros da categoria Artes
r = requests.get(f'{base}/Book', params={'categoryId': artes['id']}, headers=headers)
if r.status_code != 200:
    print('Falha ao buscar livros:', r.status_code, r.text)
    sys.exit(1)

books = r.json()
print(f"\nTotal de livros na categoria Artes: {len(books)}")
for i, b in enumerate(books, 1):
    print(f"  {i}. {b['title']} — {b['author']} (ID: {b['id']})")

# Salvar lista completa para referência
with open('artes_books.json', 'w', encoding='utf-8') as f:
    json.dump(books, f, ensure_ascii=False, indent=2)
print('\nLista completa salva em artes_books.json')

# 4. Verificar se há subcategorias (filhas de Artes)
subcats = [c for c in categories if c.get('parentCategoryId') == artes['id']]
if subcats:
    print(f"\nSubcategorias existentes de Artes ({len(subcats)}):")
    for sc in subcats:
        print(f"  {sc['id']} - {sc['name']}")
else:
    print("\nNenhuma subcategoria existente para Artes.")