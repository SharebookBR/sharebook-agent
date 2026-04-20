# ShareBook Book Preparer

Agente curador que prepara livros para importação no ShareBook.

## Propósito

Garantir qualidade no acervo do ShareBook através de:
1. **Validação cuidadosa** de metadados (título, autor)
2. **Categorização apropriada** (sempre categoria folha)
3. **Sinopses sexy mas fiéis** (3 parágrafos envolventes)
4. **Prevenção de erros** como associações automáticas incorretas

## Fluxo

```
Agente (Preparador) → Worker (Executor)
     ↓                      ↓
Curadoria              Cadastro técnico
     ↓                      ↓
PostgreSQL (planejamento)  ShareBook (produção)
```

## Caso de Uso Exemplo

**Problema:** Livro "Carolina" com:
- `planned_author`: "Carolina Maria de Jesus" (errado)
- `planned_synopsis`: Sobre favela/periferia (errado)

**Solução do Preparador:**
1. Ler fonte: autor é "Casimiro de Abreu", obra é romance século XIX
2. Corrigir `planned_author`
3. Escolher categoria "Drama Psicológico/Moral"
4. Escrever sinopse sexy sobre paixão proibida, destino feminino
5. Atualizar PostgreSQL, marcar como `waiting_process`

## Arquitetura

- **Entrada:** Itens com `status IN ('waiting_editor', 'editing')` no PostgreSQL
- **Processamento:** Validação fonte → Categorização → Sinopse
- **Saída:** PostgreSQL atualizado com `planned_*` campos completos e `status='waiting_process'`
- **Próximo passo:** Worker executa cadastro com dados curados

## Dependências

- Acesso ao PostgreSQL do importador (`sharebook_importer` database)
- Token de API do ShareBook (para consultar categorias)
- Acesso à internet (para ler fontes BaixeLivros)

## Métricas de Qualidade

- **Acurácia:** 100% de correspondência título/autor com fonte
- **Categorização:** 100% categorias folha apropriadas
- **Sinopse:** 100% com 3 parágrafos, tom sexy, fidelidade
- **Velocidade:** ~10-15 minutos por livro (com atenção)

---

*"Um acervo de qualidade começa com curadoria atenta, não com automação cega."*