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

# Primeiro, buscar categoria atual para ver estrutura
r = requests.get(f'{base}/Category/{artes_id}', headers=headers)
if r.status_code != 200:
    print(f'Falha ao buscar categoria: {r.status_code} {r.text[:200]}')
    exit(1)

cat = r.json()
print('Categoria atual:', json.dumps(cat, indent=2, ensure_ascii=False))

# Atualizar nome
payload = {'name': new_name}
r = requests.put(f'{base}/Category/{artes_id}', headers=headers, json=payload)
print(f'PUT /Category/{artes_id} -> {r.status_code}')
if r.status_code == 200:
    print('Sucesso! Categoria renomeada.')
    print('Resposta:', r.json())
else:
    print('Erro:', r.text[:500])