#!/usr/bin/env python3
import requests, json, sys
from pathlib import Path

env = {}
with open(Path('/data/workspace/sharebook-agent/.env')) as f:
    for line in f:
        if '=' in line:
            k, v = line.strip().split('=', 1)
            env[k] = v
token = env.get('SHAREBOOK_PROD_ACCESS_TOKEN')
if not token:
    print('Token não encontrado')
    sys.exit(1)

headers = {'Authorization': f'Bearer {token}'}

# Buscar livros criados nos últimos 3 dias (via API? mais fácil via banco, mas vamos usar API de busca por data? não tem)
# Vamos buscar todos os livros e filtrar por data? Pesado.
# Alternativa: usar a lista de títulos fornecida e buscar por slug.
# Vou buscar por título+autor usando endpoint /Book?title=...

books = [
    ('O Sertanejo', 'José de Alencar'),
    ('O Saci', 'Monteiro Lobato'),
    ('Marquês de Rabicó', 'Monteiro Lobato'),
    ('Coletânea de Contos Crônicas', 'Vários autores'),
    ('Canção do Exílio', 'Gonçalves Dias'),
    ('O Caso da Vara', 'Machado de Assis'),
    ('Caçadas de Pedrinho', 'Monteiro Lobato'),
    ('Contos Populares do Brasil', 'Sílvio Romero'),
    ('Contos Fora da Moda', 'Artur de Azevedo'),
    ('A Chave do Tamanho', 'Monteiro Lobato'),
    ('Guerra dos Mascates', 'José de Alencar'),
    ('Sonhos d\'Ouro', 'José de Alencar'),
    ('A Condessa Vésper', 'Aluísio Azevedo'),
    ('O Mulato', 'Aluísio Azevedo'),
    ('Emília no País da Gramática', 'Monteiro Lobato'),
    ('Uns Braços', 'Machado de Assis'),
    ('A Normalista', 'Adolfo Caminha'),
    ('Diva', 'José de Alencar'),
    ('O Gaúcho', 'José de Alencar'),
    ('O Enfermeiro', 'Machado de Assis'),
    ('Teoria do Medalhão', 'Machado de Assis'),
    ('Tarde', 'Olavo Bilac'),
    ('Últimos Cantos', 'Gonçalves Dias'),
    ('O Japão', 'Aluísio Azevedo'),
    ('Uma Lágrima de Mulher', 'Aluísio Azevedo'),
    ('O Empréstimo', 'Machado de Assis'),
    ('Crisálidas', 'Machado de Assis'),
    ('Contrabandista', 'João Simões Lopes Neto'),
    ('Peter Pan', 'Monteiro Lobato'),
    ('Aritmética da Emília', 'Monteiro Lobato'),
    ('Vidas Secas', 'Graciliano Ramos'),
    ('Broquéis', 'Cruz e Sousa'),
    ('O Minotauro', 'Monteiro Lobato'),
    ('Um Cinturão', 'Graciliano Ramos'),
    ('A Cartomante', 'Machado de Assis'),
    ('A Filha do Barão', 'Pedro Nolasco Maciel'),
    ('Salve Seu Casamento', 'Amor e Finanças'),
]

print('Revisão de sinopses - livros novos (últimos 3 dias)\n')
print('='*80)

for title, author in books:
    params = {'title': title, 'author': author}
    try:
        r = requests.get('https://api.sharebook.com.br/api/Book', headers=headers, params=params, timeout=30)
        if r.status_code != 200:
            print(f'❌ Erro {r.status_code} para {title}')
            continue
        data = r.json()
        items = data.get('items', [])
        if not items:
            print(f'⚠️  Livro não encontrado: {title}')
            continue
        book = items[0]  # assume primeiro
        synopsis = book.get('synopsis', '').strip()
        length = len(synopsis)
        # Critérios de sinopse ruim:
        # - Muito curta (< 200 chars)
        # - Contém apenas descrição factual
        # - Não tem parágrafos (ou só um)
        paragraphs = synopsis.count('\n\n') + 1
        status = '✅ OK'
        if length < 200:
            status = '❌ CURTA'
        elif paragraphs < 2:
            status = '⚠️  POUCOS PARÁGRAFOS'
        elif 'domínio público' in synopsis.lower() or 'obra' in synopsis.lower() and 'autor' in synopsis.lower():
            status = '⚠️  GENÉRICA'
        
        print(f'{status} {title} — {author}')
        print(f'   Caracteres: {length}, Parágrafos: {paragraphs}')
        if status != '✅ OK':
            preview = synopsis[:150].replace('\n', ' ')
            print(f'   Prévia: {preview}...')
        print()
    except Exception as e:
        print(f'Erro ao processar {title}: {e}')
        continue

print('Fim da revisão.')