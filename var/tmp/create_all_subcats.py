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

parent_id = '8c347027-8bcb-49a8-a755-df55eeb1affd'

subcategories = [
    {'name': 'Poesia Reflexiva / Existencial', 'slug': 'poesia-reflexiva-existencial'},
    {'name': 'Poesia Moderna & Experimental', 'slug': 'poesia-moderna-experimental'},
    {'name': 'Poesia Dramática', 'slug': 'poesia-dramatica'},
    {'name': 'Teatro & Dramaturgia', 'slug': 'teatro-dramaturgia'},
    {'name': 'Épicos & Narrativas', 'slug': 'epicos-narrativas'},
    {'name': 'Estética & Teoria', 'slug': 'estetica-teoria'},
]

created = []
for sub in subcategories:
    print(f'Criando: {sub["name"]}')
    payload = {
        'name': sub['name'],
        'parentCategoryId': parent_id,
        'slug': sub['slug']
    }
    r = requests.post(f'{base}/Category', headers=headers, json=payload)
    if r.status_code == 200:
        data = r.json()['value']
        created.append({'name': data['name'], 'id': data['id'], 'slug': data.get('slug')})
        print(f'  OK -> ID {data["id"]}')
    else:
        print(f'  Erro {r.status_code}: {r.text[:200]}')
    time.sleep(0.5)

print('\n=== Subcategorias criadas ===')
for c in created:
    print(f'{c["name"]}: {c["id"]}')

# Salvar mapeamento
with open('subcategories_created.json', 'w', encoding='utf-8') as f:
    json.dump(created, f, ensure_ascii=False, indent=2)
print('\nMapeamento salvo em subcategories_created.json')