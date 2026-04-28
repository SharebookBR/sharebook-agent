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

base = 'https://sharebook.com.br/api'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

artes_id = '8c347027-8bcb-49a8-a755-df55eeb1affd'
new_name = 'Poesia & Artes'

# Payload baseado no que a API espera (modelo Category)
payload = {
    'id': artes_id,
    'name': new_name,
    'parentCategoryId': None,
    'slug': 'artes'  # manter slug para não quebrar URLs
}

print('Payload:', json.dumps(payload, indent=2, ensure_ascii=False))

r = requests.put(f'{base}/Category', headers=headers, json=payload)
print(f'PUT /Category -> {r.status_code}')
if r.status_code == 200:
    print('Sucesso! Categoria renomeada.')
    print('Resposta:', r.json())
else:
    print('Erro:', r.text[:500])