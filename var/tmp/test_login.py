import urllib.request
import urllib.error
import json
import ssl
import os
from pathlib import Path

env_path = Path('/data/workspace/sharebook-agent/.env')
env = {}
with open(env_path) as f:
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v

user = env.get('SHAREBOOK_PROD_USER')
password = env.get('SHAREBOOK_PROD_PASSWORD')
print('User:', user)
print('Password:', '***' if password else 'missing')

payload = {'Email': user, 'Password': password}
headers = {'Content-Type': 'application/json', 'x-requested-with': 'web', 'client-version': 'v0.0.0'}
data = json.dumps(payload).encode('utf-8')

req = urllib.request.Request('https://sharebook.com.br/api/Account/Login/', data=data, headers=headers, method='POST')
context = ssl._create_unverified_context()

try:
    with urllib.request.urlopen(req, timeout=30, context=context) as resp:
        body = resp.read().decode('utf-8')
        print('Status:', resp.status)
        print('Response:', body)
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code)
    print('Response:', e.read().decode('utf-8')[:500])