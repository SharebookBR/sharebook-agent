import subprocess
import json
import time

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

books = [
    ('A Caixa de Pandora', 'Hesíodo', 'Épicos & Narrativas'),
    ('A Divina Comédia', 'Dante Alighieri', 'Épicos & Narrativas'),
    ('Arte Poética', 'Aristóteles', 'Estética & Teoria'),
    ('Crisálidas', 'Machado de Assis', 'Poesia Lírica'),
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
    ('Tarde', 'Olavo Bilac', 'Poesia Lírica'),
    ('Últimos Cantos', 'Gonçalves Dias', 'Poesia Lírica'),
]

script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_book.py'

success = []
errors = []

for i, (title, author, subcat_name) in enumerate(books, 1):
    subcat_id = subcat_map.get(subcat_name)
    if not subcat_id:
        print(f'[{i}/17] ERRO: subcategoria não mapeada')
        errors.append((title, 'subcategoria não mapeada'))
        continue
    
    print(f'[{i}/17] {title} — {author} → {subcat_name}')
    
    # 1. Buscar ID do livro digital
    cmd_find = ['python3', script_path, 'find', '--title', title, '--author', author]
    try:
        output = subprocess.check_output(cmd_find, stderr=subprocess.STDOUT, text=True, timeout=30)
        data = json.loads(output)
        # Verificar se é digital (type Eletronic)
        if data.get('type') != 'Eletronic':
            print('   Não é digital, pulando')
            errors.append((title, 'não digital'))
            continue
        book_id = data['id']
    except subprocess.CalledProcessError as e:
        print(f'   ERRO find: {e.output[:200]}')
        errors.append((title, 'find failed'))
        continue
    except Exception as e:
        print(f'   Exceção find: {e}')
        errors.append((title, 'find exception'))
        continue
    
    # 2. Atualizar categoria
    cmd_update = ['python3', script_path, 'update', '--id', book_id, '--category-id', subcat_id]
    try:
        output = subprocess.check_output(cmd_update, stderr=subprocess.STDOUT, text=True, timeout=30)
        print('   ✅ Atualizado')
        success.append((title, book_id, subcat_id))
    except subprocess.CalledProcessError as e:
        print(f'   ERRO update: {e.output[:200]}')
        errors.append((title, 'update failed'))
    except Exception as e:
        print(f'   Exceção update: {e}')
        errors.append((title, 'update exception'))
    
    time.sleep(0.5)

print('\n=== RESULTADO ===')
print(f'Sucesso: {len(success)}')
print(f'Erros: {len(errors)}')
if errors:
    for title, reason in errors:
        print(f'  - {title}: {reason}')

with open('remaining_script_log.json', 'w', encoding='utf-8') as f:
    json.dump({'success': success, 'errors': errors}, f, indent=2)