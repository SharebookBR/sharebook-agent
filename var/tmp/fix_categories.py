#!/usr/bin/env python3
import requests, json, sys, time
from pathlib import Path

env = {}
with open(Path('/data/workspace/sharebook-agent/.env')) as f:
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v
token = env.get('SHAREBOOK_PROD_ACCESS_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Mapeamento título → nova categoria ID
mapping = {
    'O Homem que Sabia Javanês': '019d7dbe-bed0-7682-aec8-e8284f930202',
    'Inocência': '019d7dbe-bea3-73a6-8abf-ad65f1367c90',
    'O Sertanejo': '019d7dc9-55cb-7532-b98d-cb3709d67baf',
    'O Saci': '88ee3012-2875-4546-a271-869efef7f4c6',
    'Marquês de Rabicó': '88ee3012-2875-4546-a271-869efef7f4c6',
    'Coletânea de Contos Crônicas': '019d7dbe-bea3-73a6-8abf-ad65f1367c90',
    'Canção do Exílio': '019d9bf4-725d-7eb3-bf31-5dcd08c93053',  # já corrigido
    'O Caso da Vara': '019d7dbe-bed0-7682-aec8-e8284f930202',
    'Caçadas de Pedrinho': '88ee3012-2875-4546-a271-869efef7f4c6',
    'Contos Populares do Brasil': '019d7dbe-bea3-73a6-8abf-ad65f1367c90',
    'Contos Fora da Moda': '019d7dbe-bea3-73a6-8abf-ad65f1367c90',
    'A Chave do Tamanho': '88ee3012-2875-4546-a271-869efef7f4c6',
    'Guerra dos Mascates': '019d7dc9-55cb-7532-b98d-cb3709d67baf',
    'Sonhos d\'Ouro': '019d7dbe-bea3-73a6-8abf-ad65f1367c90',
    'A Condessa Vésper': '019d7dbe-bed0-7682-aec8-e8284f930202',
}

def update_book(title, new_category_id):
    # Buscar livro por título (assumindo autor conhecido)
    params = {'title': title}
    r = requests.get('https://api.sharebook.com.br/api/Book', headers=headers, params=params)
    if r.status_code != 200:
        print(f'❌ Erro ao buscar {title}')
        return False
    data = r.json()
    items = data.get('items', [])
    if not items:
        print(f'❌ Livro não encontrado: {title}')
        return False
    book = items[0]
    book_id = book['id']
    # Verificar se já está na categoria correta
    if book.get('categoryId') == new_category_id:
        print(f'⏭️  {title} já está na categoria correta')
        return True
    # Atualizar
    payload = {
        'id': book_id,
        'title': book['title'],
        'author': book['author'],
        'categoryId': new_category_id,
        'synopsis': book.get('synopsis'),
        'type': book['type'],
        'status': book.get('status', 'Available'),
        'imageSlug': book.get('imageSlug'),
        'slug': book.get('slug'),
    }
    if book.get('userId'):
        payload['userId'] = book['userId']
    r2 = requests.put(f'https://api.sharebook.com.br/api/Book/{book_id}', headers=headers, json=payload)
    if r2.status_code == 200:
        print(f'✅ {title} → {new_category_id}')
        return True
    else:
        print(f'❌ Erro ao atualizar {title}: {r2.status_code} {r2.text[:200]}')
        return False

# Executar
print('Corrigindo categorias de livros em "Sociedade & Mundo"...')
for title, cat_id in mapping.items():
    update_book(title, cat_id)
    time.sleep(0.5)  # evitar rate limit
print('Concluído.')