import requests
import json
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

artes_id = '8c347027-8bcb-49a8-a755-df55eeb1affd'
new_name = 'Poesia & Artes'

# Primeiro, buscar categoria atual (usando endpoint que funciona)
r = requests.get(f'{base}/Category/{artes_id}', headers=headers)
if r.status_code != 200:
    print(f'Falha ao buscar categoria: {r.status_code} {r.text[:200]}')
    # Tentar lista geral
    r = requests.get(f'{base}/Category', headers=headers)
    if r.status_code == 200:
        cats = r.json()['items']
        for cat in cats:
            if cat['id'] == artes_id:
                print('Categoria atual:', cat)
                break
    exit(1)

cat = r.json()
print('Categoria atual:', json.dumps(cat, indent=2, ensure_ascii=False))

# Atualizar nome (PUT pode não funcionar, tentar POST com id?)
payload = {
    'id': artes_id,
    'name': new_name,
    'parentCategoryId': None,
    'slug': 'artes'  # manter slug
}
print('\nTentando PUT /Category/{id}...')
r = requests.put(f'{base}/Category/{artes_id}', headers=headers, json=payload)
print(f'PUT -> {r.status_code}')
if r.status_code == 200:
    print('Sucesso!')
    print('Resposta:', r.json())
else:
    print('Erro:', r.text[:500])
    # Tentar POST /Category (update)
    print('\nTentando POST /Category (update)...')
    r = requests.post(f'{base}/Category', headers=headers, json=payload)
    print(f'POST -> {r.status_code}')
    if r.status_code == 200:
        print('Sucesso!')
        print('Resposta:', r.json())
    else:
        print('Erro:', r.text[:500])