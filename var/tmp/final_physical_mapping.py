import subprocess
import json
import time

# Mapeamento ID -> categoria folha ID
mapping = [
    # Beijo Noir -> Ficção (Mistério / Suspense)
    ('8824c8c5-d9b5-42a1-543f-08d60de7c01e', '019d636e-6623-7c74-9c73-92b90bf3e2fa'),
    # Série Paranaenses Nº 4 -> Artes (Estética & Teoria)
    ('87a9316b-27a6-4a45-5441-08d60de7c01e', '019d9bf5-09b0-722a-8b7a-91ae09669652'),
    # Composições para meus amigos -> Artes (Poesia Lírica)
    ('2854c50d-5593-4793-5443-08d60de7c01e', '019d9bf4-725d-7eb3-bf31-5dcd08c93053'),
    # O Príncipe -> Filosofia (folha)
    ('5a3c93ea-8aa8-4da9-cf23-08d66016b73f', 'bd088da6-cec6-443e-8bf4-06eb8a7456fd'),
    # 50 TONS DE CINZA -> Ficção (Romance? Não tem subcategoria romance, usar Mistério / Suspense)
    ('6ed60879-f52d-4abe-c530-08d6cd04fb21', '019d636e-6623-7c74-9c73-92b90bf3e2fa'),
    # Tributo À Solidão -> Artes (Poesia Lírica)
    ('c883a809-9579-456a-ea2d-08d724b27a87', '019d9bf4-725d-7eb3-bf31-5dcd08c93053'),
    # Forgotten Realms -> Ficção (Fantasia)
    ('64437224-9534-4ce3-6ed1-08d7466ccf53', '019d636c-ede8-7864-9a63-7b3e0766e01c'),
    # Livro dos Monstros -> Ficção (Fantasia)
    ('86fc5b54-d9aa-4a73-6ed2-08d7466ccf53', '019d636c-ede8-7864-9a63-7b3e0766e01c'),
    # Antonio parreiras pinturas e desenhos -> Artes (Estética & Teoria)
    ('10790847-f16d-4474-970b-08d8001c6a98', '019d9bf5-09b0-722a-8b7a-91ae09669652'),
    # Como desenhar super-heróis -> Artes (Estética & Teoria)
    ('720907dd-adc8-4110-0b3f-08d803646b51', '019d9bf5-09b0-722a-8b7a-91ae09669652'),
    # Louco por viver -> Vida & Bem-estar (folha)
    ('cb448de6-a71d-40b5-8049-08d85528ed50', '019d7e18-4046-7afc-bd48-f5315d832a33'),
    # O Sabor da Saúde -> Vida & Bem-estar
    ('f442a311-f928-42d1-3174-08d8ae7b56a2', '019d7e18-4046-7afc-bd48-f5315d832a33'),
    # A garota do trem -> Ficção (Mistério / Suspense)
    ('3006bc96-9b19-4c91-cd56-08d8fc88fc73', '019d636e-6623-7c74-9c73-92b90bf3e2fa'),
    # Nova antologia poética -> Artes (Poesia Lírica)
    ('cf033f3f-a817-417a-a456-08d9038fbe62', '019d9bf4-725d-7eb3-bf31-5dcd08c93053'),
    # José de Alencar- O guarani -> Ficção (Aventura)
    ('c816a617-dfa1-4315-78ca-08d904caf54c', '019d636c-efb8-76f6-b9f7-f35a2c5f8c09'),
    # Auto da Compadecida -> Drama (Drama de Crítica Social)
    ('2018f412-d37b-45a6-92b1-08d91ea9abfa', '019d7dbe-bea3-73a6-8abf-ad65f1367c90'),
    # O ex-estranho -> Artes (Poesia Lírica)
    ('25393c47-75d6-455e-bc31-08d926b97410', '019d9bf4-725d-7eb3-bf31-5dcd08c93053'),
    # Um Brasil do outro mundo -> Sociedade & Mundo (folha)
    ('de628e76-51fa-4e04-83f2-08d92c0ad77b', '019d7e18-400e-7ad9-acb2-e5add38d9da7'),
    # As cem melhores cronicas brasileiras -> Ficção (Drama em Narrativas Curtas)
    ('97480373-1672-4f6d-abf3-08d93fdde6fc', '019d7dc9-55cb-7532-b98d-cb3709d67baf'),
    # Pluft, o fantasminha -> Infantil/Juvenil (folha)
    ('c0949a92-762e-42f2-202e-08d9e6845334', '88ee3012-2875-4546-a271-869efef7f4c6'),
    # Oi tia ?? -> Infantil/Juvenil
    ('10508bd7-8a54-4714-c6b0-08da9b3a979e', '88ee3012-2875-4546-a271-869efef7f4c6'),
]

script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_book.py'

success = []
errors = []

for i, (book_id, cat_id) in enumerate(mapping, 1):
    print(f'[{i}/21] Atualizando livro {book_id[:8]}...')
    cmd_update = ['python3', script_path, 'update', '--id', book_id, '--category-id', cat_id]
    try:
        output = subprocess.check_output(cmd_update, stderr=subprocess.STDOUT, text=True, timeout=30)
        print('   ✅ OK')
        success.append(book_id)
    except subprocess.CalledProcessError as e:
        print(f'   ERRO: {e.output[:200]}')
        errors.append(book_id)
    except Exception as e:
        print(f'   Exceção: {e}')
        errors.append(book_id)
    time.sleep(0.5)

print('\n=== RESULTADO ===')
print(f'Sucesso: {len(success)}')
print(f'Erros: {len(errors)}')
if errors:
    print('IDs com erro:', errors)