import subprocess
import json
import time

# IDs das categorias destino
category_ids = {
    'Amor': '5bccd102-e31d-49ec-96e2-984b3601a20e',
    'Artes': '8c347027-8bcb-49a8-a755-df55eeb1affd',
    'Conhecimento & Carreira': '019d7e18-3fd3-7434-8033-28750c0881b5',
    'Drama': '019d7dbc-78c0-7735-8821-a3cdc10c9aef',
    'Ficção': '097ecf66-eb64-4ab6-85e0-0a07e874f0ce',
    'Filosofia': 'bd088da6-cec6-443e-8bf4-06eb8a7456fd',
    'Infantil/Juvenil': '88ee3012-2875-4546-a271-869efef7f4c6',
    'Sociedade & Mundo': '019d7e18-400e-7ad9-acb2-e5add38d9da7',
    'Tecnologia': '1dc0f9e3-70d9-4bc8-a76c-90d7144e318c',
    'Vida & Bem-estar': '019d7e18-4046-7afc-bd48-f5315d832a33',
}

# Mapeamento ID -> categoria destino (baseado no título)
mapping = [
    ('8824c8c5-d9b5-42a1-543f-08d60de7c01e', 'Beijo Noir', 'Ficção'),
    ('87a9316b-27a6-4a45-5441-08d60de7c01e', 'Série Paranaenses Nº 4', 'Artes'),
    ('2854c50d-5593-4793-5443-08d60de7c01e', 'Composições para meus amigos', 'Artes'),
    ('5a3c93ea-8aa8-4da9-cf23-08d66016b73f', 'O Príncipe', 'Filosofia'),
    ('6ed60879-f52d-4abe-c530-08d6cd04fb21', '50 TONS DE CINZA', 'Ficção'),
    ('c883a809-9579-456a-ea2d-08d724b27a87', 'Tributo À Solidão', 'Artes'),
    ('64437224-9534-4ce3-6ed1-08d7466ccf53', 'Forgotten Realms', 'Ficção'),
    ('86fc5b54-d9aa-4a73-6ed2-08d7466ccf53', 'Livro dos Monstros', 'Ficção'),
    ('10790847-f16d-4474-970b-08d8001c6a98', 'Antonio parreiras pinturas e desenhos', 'Artes'),
    ('720907dd-adc8-4110-0b3f-08d803646b51', 'Como desenhar super-heróis', 'Artes'),
    ('cb448de6-a71d-40b5-8049-08d85528ed50', 'Louco por viver', 'Vida & Bem-estar'),
    ('f442a311-f928-42d1-3174-08d8ae7b56a2', 'O Sabor da Saúde', 'Vida & Bem-estar'),
    ('3006bc96-9b19-4c91-cd56-08d8fc88fc73', 'A garota do trem', 'Ficção'),
    ('cf033f3f-a817-417a-a456-08d9038fbe62', 'Nova antologia poética', 'Artes'),
    ('c816a617-dfa1-4315-78ca-08d904caf54c', 'José de Alencar- O guarani', 'Ficção'),
    ('2018f412-d37b-45a6-92b1-08d91ea9abfa', 'Auto da Compadecida', 'Drama'),
    ('25393c47-75d6-455e-bc31-08d926b97410', 'O ex-estranho', 'Artes'),
    ('de628e76-51fa-4e04-83f2-08d92c0ad77b', 'Um Brasil do outro mundo', 'Sociedade & Mundo'),
    ('97480373-1672-4f6d-abf3-08d93fdde6fc', 'As cem melhores cronicas brasileiras', 'Ficção'),
    ('c0949a92-762e-42f2-202e-08d9e6845334', 'Pluft, o fantasminha', 'Infantil/Juvenil'),
    ('10508bd7-8a54-4714-c6b0-08da9b3a979e', 'Oi tia ??', 'Infantil/Juvenil'),
]

script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_book.py'

success = []
errors = []

for i, (book_id, title, cat_name) in enumerate(mapping, 1):
    cat_id = category_ids.get(cat_name)
    if not cat_id:
        print(f'[{i}/21] ERRO: categoria "{cat_name}" não encontrada')
        errors.append((title, 'categoria não encontrada'))
        continue
    
    print(f'[{i}/21] {title} → {cat_name}')
    
    # Atualizar categoria
    cmd_update = ['python3', script_path, 'update', '--id', book_id, '--category-id', cat_id]
    try:
        output = subprocess.check_output(cmd_update, stderr=subprocess.STDOUT, text=True, timeout=30)
        print('   ✅ Atualizado')
        success.append((title, book_id, cat_id))
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

with open('physical_by_id_log.json', 'w', encoding='utf-8') as f:
    json.dump({'success': success, 'errors': errors}, f, indent=2)