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

parent_id = '8c347027-8bcb-49a8-a755-df55eeb1affd'
subcat = {
    'name': 'Poesia Lírica',
    'parentCategoryId': parent_id,
    'slug': 'poesia-lirica'
}

print('Criando subcategoria:', subcat['name'])
r = requests.post(f'{base}/Category', headers=headers, json=subcat)
print(f'POST /Category -> {r.status_code}')
if r.status_code == 200:
    print('Sucesso!')
    print('Resposta:', json.dumps(r.json(), indent=2, ensure_ascii=False))
else:
    print('Erro:', r.text[:500])