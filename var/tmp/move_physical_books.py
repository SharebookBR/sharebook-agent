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

# Mapeamento título -> categoria destino (julgamento editorial)
# Baseado na lista anterior
mapping = [
    ('101 coisas para fazer com as criança antes que elas cresçam', 'Roberta Faria', 'Infantil/Juvenil'),
    ('50 TONS DE CINZA', 'E L James', 'Ficção'),
    ('A garota do trem', 'Sr john', 'Ficção'),
    ('Antonio parreiras pinturas e desenhos', 'Arte no Brasil', 'Artes'),  # Estética & Teoria? manter Artes
    ('Artesãos da sapucaí', 'André Nazareth, Carlos Feijó', 'Sociedade & Mundo'),
    ('As artes do Entusiasmo', 'MUNIZ, FERNANDO', 'Vida & Bem-estar'),
    ('As cem melhores cronicas brasileiras', 'Joaquim ferreia fos santos', 'Ficção'),
    ('Auto da Compadecida', 'Ariano Suassuna', 'Drama'),
    ('Beijo Noir', 'Kiko Ferreira', 'Ficção'),
    ('Chapeuzinho Esfarrapada', 'Apaginostore', 'Infantil/Juvenil'),
    ('Como desenhar super-heróis', 'Alexandre Jubran', 'Artes'),
    ('Composições para meus amigos', 'Paulo Venturelli', 'Artes'),
    ('Eu me chamo Antônio', 'Pedro Gabriel', 'Infantil/Juvenil'),
    ('Forgotten Realms', 'Greenwood, Reynolds, Williams and Heinsoo', 'Ficção'),
    ('José de Alencar- O guarani', 'José de Alencar', 'Ficção'),
    ('LIVRO A CONSPIRAÇÃO FRANCISCANA', 'John SAke', 'Filosofia'),
    ('Letramentos de reexistência', 'Ana Lúcia Silva Souza', 'Conhecimento & Carreira'),
    ('Livee Pensador', 'Grupo de Autores', 'Filosofia'),
    ('Livro dos Monstros', 'Wizards of the coast', 'Ficção'),
    ('Louco por viver', 'Roberto shinyashiki', 'Vida & Bem-estar'),
    ('Nova antologia poética', 'Mário Quintana', 'Artes'),
    ('O Príncipe', 'Maquiavel', 'Filosofia'),
    ('O Sabor da Saúde', 'Eunice Leme Vidal', 'Vida & Bem-estar'),
    ('O ex-estranho', 'Paulo Leminski', 'Artes'),  # poesia? manter Artes
    ('Oi tia ??', 'Iska', 'Infantil/Juvenil'),
    ('Pluft, o fantasminha', 'Maria Clara Machado', 'Infantil/Juvenil'),
    ('Série Paranaenses Nº 4', 'Sérgio Rubens Sossélla', 'Artes'),
    ('Tributo À Solidão', 'Pismel, Ana', 'Artes'),
    ('Um Brasil do outro mundo', 'Silvia La Regina', 'Sociedade & Mundo'),
]

script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_book.py'

success = []
errors = []

for i, (title, author, cat_name) in enumerate(mapping, 1):
    cat_id = category_ids.get(cat_name)
    if not cat_id:
        print(f'[{i}/29] ERRO: categoria "{cat_name}" não encontrada')
        errors.append((title, 'categoria não encontrada'))
        continue
    
    print(f'[{i}/29] {title} — {author} → {cat_name}')
    
    # Buscar livro físico específico (pode haver múltiplos, pegar o primeiro com Type=0)
    cmd_find = ['python3', script_path, 'find', '--title', title, '--author', author]
    try:
        output = subprocess.check_output(cmd_find, stderr=subprocess.STDOUT, text=True, timeout=30)
        data = json.loads(output)
        # Verificar se é físico (type Printed)
        if data.get('type') != 'Printed':
            print('   Não é físico, pulando')
            errors.append((title, 'não físico'))
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

with open('physical_migration_log.json', 'w', encoding='utf-8') as f:
    json.dump({'success': success, 'errors': errors}, f, indent=2)