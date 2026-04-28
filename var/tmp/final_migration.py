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

# Lista de livros com subcategoria (hardcoded a partir da missão)
books = [
    # Poesia Lírica (4) - um já migrado
    ('As Primaveras', 'Casimiro de Abreu', 'Poesia Lírica'),
    ('Sonetos e Outros Poemas', 'Bocage', 'Poesia Lírica'),
    ('O Guardador de Rebanhos', 'Alberto Caeiro', 'Poesia Lírica'),
    ('O Pastor Amoroso', 'Alberto Caeiro', 'Poesia Lírica'),
    # Poesia Reflexiva / Existencial (4)
    ('Eu', 'Augusto dos Anjos', 'Poesia Reflexiva / Existencial'),
    ('Eu e Outras Poesias', 'Augusto dos Anjos', 'Poesia Reflexiva / Existencial'),
    ('Mensagem', 'Fernando Pessoa', 'Poesia Reflexiva / Existencial'),
    ('Livro de Mágoas', 'Florbela Espanca', 'Poesia Reflexiva / Existencial'),
    # Poesia Moderna & Experimental (6)
    ('Cancioneiro', 'Fernando Pessoa', 'Poesia Moderna & Experimental'),
    ('O Eu Profundo e Outros Eus', 'Fernando Pessoa', 'Poesia Moderna & Experimental'),
    ('Poemas de Álvaro de Campos', 'Fernando Pessoa', 'Poesia Moderna & Experimental'),
    ('Poemas de Ricardo Reis', 'Fernando Pessoa', 'Poesia Moderna & Experimental'),
    ('Poesias Inéditas', 'Fernando Pessoa', 'Poesia Moderna & Experimental'),
    ('Broquéis', 'Cruz e Sousa', 'Poesia Moderna & Experimental'),
    # Poesia Dramática (2)
    ('O Navio Negreiro', 'Castro Alves', 'Poesia Dramática'),
    ('A Mensageira das Violetas', 'Florbela Espanca', 'Poesia Dramática'),
    # Teatro & Dramaturgia (5)
    ('Otelo', 'William Shakespeare', 'Teatro & Dramaturgia'),
    ('Rei Lear', 'William Shakespeare', 'Teatro & Dramaturgia'),
    ('Auto da Barca do Inferno', 'Gil Vicente', 'Teatro & Dramaturgia'),
    ('Fausto', 'Johann Wolfgang von Goethe', 'Teatro & Dramaturgia'),
    ('Primeiro Fausto', 'Fernando Pessoa', 'Teatro & Dramaturgia'),
    # Épicos & Narrativas (7)
    ('A Divina Comédia', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('Inferno', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('Purgatório', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('Paraíso', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('Paraíso Perdido', 'John Milton', 'Épicos & Narrativas'),
    ('A Caixa de Pandora', 'Hesíodo', 'Épicos & Narrativas'),
    ('Faetonte (Filho de Apolo)', 'Ovídio', 'Épicos & Narrativas'),
    # Estética & Teoria (2)
    ('Arte Poética', 'Aristóteles', 'Estética & Teoria'),
    ('Grandeza', 'Orlando Fedeli', 'Estética & Teoria'),
]

print('Iniciando migração de 30 livros...\n')

success = []
errors = []

for i, (title, author, subcat_name) in enumerate(books, 1):
    subcat_id = subcat_map.get(subcat_name)
    if not subcat_id:
        print(f'[{i}/30] ERRO: subcategoria "{subcat_name}" não mapeada')
        errors.append((title, 'subcategoria não mapeada'))
        continue
    
    print(f'[{i}/30] {title} — {author} → {subcat_name}')
    
    # 1. Buscar livro
    params = {'title': title, 'author': author}
    try:
        r = requests.get(f'{base}/Book', headers=headers, params=params, timeout=30)
        if r.status_code != 200:
            print(f'   ERRO busca: {r.status_code}')
            errors.append((title, f'busca {r.status_code}'))
            time.sleep(1)
            continue
        data = r.json()
        items = data.get('items', [])
        if not items:
            print('   Livro não encontrado')
            errors.append((title, 'não encontrado'))
            continue
        book = items[0]
        book_id = book['id']
    except Exception as e:
        print(f'   Exceção busca: {e}')
        errors.append((title, f'exceção busca {e}'))
        continue
    
    # 2. Atualizar categoria (PUT com payload completo)
    # Precisamos enviar todos os campos obrigatórios. Vamos usar o book atual e modificar categoryId.
    payload = {
        'id': book_id,
        'title': book['title'],
        'author': book['author'],
        'categoryId': subcat_id,
        'synopsis': book.get('synopsis', ''),
        'type': book.get('type', 'Eletronic'),
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
    
    time.sleep(0.5)  # pausa para não sobrecarregar

print('\n=== RESULTADO FINAL ===')
print(f'Sucesso: {len(success)} livros')
print(f'Erros: {len(errors)} livros')
if errors:
    print('\nDetalhes dos erros:')
    for title, reason in errors:
        print(f'  - {title}: {reason}')

# Salvar log
with open('final_migration_log.json', 'w', encoding='utf-8') as f:
    json.dump({'success': success, 'errors': errors}, f, ensure_ascii=False, indent=2)
print('\nLog salvo em final_migration_log.json')

if len(success) == 30:
    print('\n🎉 TODOS os 30 livros foram migrados com sucesso!')
else:
    print(f'\n⚠️  Apenas {len(success)}/30 migrados.')