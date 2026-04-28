#!/usr/bin/env python3
"""
Atualiza o nome da categoria Artes para Poesia & Artes via SQL direto.
Require permissão RW.
"""
import subprocess
import sys

# Script de execução RW (precisa de input SIM)
script_path = '/data/workspace/sharebook-agent/scripts/sharebook_prod_pg_rw_exec.py'
sql = "UPDATE \"Categories\" SET \"Name\" = 'Poesia & Artes' WHERE \"Id\" = '8c347027-8bcb-49a8-a755-df55eeb1affd';"

print('⚠️  Atualizando categoria Artes → Poesia & Artes no banco de produção.')
print('SQL:', sql)
print('')

# Executar com input automático SIM
proc = subprocess.Popen(
    ['python3', script_path, '--sql', sql],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)
# Enviar SIM após a pergunta
output, error = proc.communicate(input='SIM\n')
print(output)
if error:
    print('Erro:', error)
sys.exit(proc.returncode)