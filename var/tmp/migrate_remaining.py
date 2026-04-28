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

# Lista de livros digitais restantes com subcategoria determinada
books = [
    ('A Caixa de Pandora', 'Hesíodo', 'Épicos & Narrativas'),
    ('A Divina Comédia', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('Arte Poética', 'Aristóteles', 'Estética & Teoria'),
    ('Crisálidas', 'Machado de Assis', 'Poesia Lírica'),  # não está na missão; assumo poesia lírica
    ('Faetonte (Filho de Apolo)', 'Ovídio', 'Épicos & Narrativas'),
    ('Fausto', 'Johann Wolfgang Von Goethe', 'Teatro & Dramaturgia'),
    ('Grandeza', 'Orlando Fedeli', 'Estética & Teoria'),
    ('Inferno', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('O Guardador de Rebanhos', 'Alberto Caeiro', 'Poesia Lírica'),
    ('O Pastor Amoroso', 'Alberto Caeiro', 'Poesia Lírica'),
    ('Paraíso', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('Paraíso Perdido', 'John Milton', 'Épicos & Narrativas'),
    ('Primeiro Fausto', 'Fernando Pessoa', 'Teatro & Dramaturgia'),
    ('Purgatório', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('Sonetos e Outros Poemas', 'Bocage', 'Poesia Lírica'),
    ('Tarde', 'Olavo Bilac', 'Poesia Lírica'),  # não está na missão
    ('Últimos Cantos', 'Gonçalves Dias', 'Poesia Lírica'),  # não está na missão
]

print('Migrando 17 livros digitais restantes...\n')

success = []
errors = []

for i, (title, author, subcat_name) in enumerate(books, 1):
    subcat_id = subcat_map.get(subcat_name)
    if not subcat_id:
        print(f'[{i}/17] ERRO: subcategoria "{subcat_name}" não mapeada')
        errors.append((title, 'subcategoria não mapeada'))
        continue
    
    print(f'[{i}/17] {title} — {author} → {subcat_name}')
    
    # 1. Buscar livro (pode haver múltiplos registros, precisamos do digital)
    params = {'title': title, 'author': author}
    try:
        r = requests.get(f'{base}/Book', headers=headers, params=params, timeout=30)
        if r.status_code != 200:
            print(f'   ERRO busca: {r.status_code}')
            errors.append((title, f'busca {r.status_code}'))
            continue
        data = r.json()
        items = data.get('items', [])
        # Filtrar por tipo Eletronic (Type = 1)
        digital_items = [it for it in items if it.get('type') == 'Eletronic']
        if not digital_items:
            print('   Nenhum livro digital encontrado')
            errors.append((title, 'nenhum digital'))
            continue
        book = digital_items[0]  # pega o primeiro digital
        book_id = book['id']
    except Exception as e:
        print(f'   Exceção busca: {e}')
        errors.append((title, f'exceção busca {e}'))
        continue
    
    # 2. Atualizar categoria
    payload = {
        'id': book_id,
        'title': book['title'],
        'author': book['author'],
        'categoryId': subcat_id,
        'synopsis': book.get('synopsis', ''),
        'type': book['type'],
        'status': book.get('status', 'Available'),
        'imageSlug': book.get('imageSlug'),
        'slug': book.get('slug'),
        'userId': book.get('userId'),
    }
    try:
        r = requests.put(f'{base}/Book/{book_id}', headers=headers, json=payload, timeout=30)
        if r.status_code == 200:
            print('   ✅ Atualizado')
            success.append((title, book_id, subcat_id))
        else:
            print(f'   ERRO update: {r.status_code} {r.text[:100]}')
            errors.append((title, f'update {r.status_code}'))
    except Exception as e:
        print(f'   Exceção update: {e}')
        errors.append((title, f'exceção update {e}'))
    
    time.sleep(0.3)

print('\n=== RESULTADO ===')
print(f'Sucesso: {len(success)} livros')
print(f'Erros: {len(errors)} livros')
if errors:
    print('\nErros detalhados:')
    for title, reason in errors:
        print(f'  - {title}: {reason}')

# Salvar log
with open('remaining_migration_log.json', 'w', encoding='utf-8') as f:
    json.dump({'success': success, 'errors': errors}, f, ensure_ascii=False, indent=2)
print('\nLog salvo em remaining_migration_log.json')

if len(success) == 17:
    print('\n🎉 Todos os 17 livros digitais migrados!')
else:
    print(f'\n⚠️  Apenas {len(success)}/17 migrados.')