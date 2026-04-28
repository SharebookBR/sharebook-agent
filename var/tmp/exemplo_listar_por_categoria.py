#!/usr/bin/env python3
"""
Exemplo de como listar livros por categoria usando a rota correta da API Sharebook.
Endpoint: GET /api/Book/Category/{categoryId}/{page}/{items}
"""
import requests
import sys
from pathlib import Path

def load_env():
    env = {}
    with open(Path(__file__).parent.parent.parent / '.env') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                env[k] = v
    return env

def list_books_by_category(category_id, page=1, items=50):
    env = load_env()
    token = env.get('SHAREBOOK_PROD_ACCESS_TOKEN')
    if not token:
        print('Token não encontrado')
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f'https://api.sharebook.com.br/api/Book/Category/{category_id}/{page}/{items}'
    
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f'Erro {r.status_code}: {r.text[:200]}')
        return
    
    data = r.json()
    total = data.get('totalItems', 0)
    books = data.get('items', [])
    print(f'Categoria {category_id}')
    print(f'Total de livros: {total}')
    print(f'Página {page} (itens por página: {items})')
    print('---')
    for b in books:
        print(f"  {b['title']} — {b.get('author', '')} (ID: {b['id']})")
    return books

if __name__ == '__main__':
    # Exemplo: listar livros da subcategoria Poesia Lírica
    subcat_id = '019d9bf4-725d-7eb3-bf31-5dcd08c93053'
    if len(sys.argv) > 1:
        subcat_id = sys.argv[1]
    list_books_by_category(subcat_id)