# Sharebook Master Playbook

Playbook tático do projeto.  
Usar quando a tarefa atravessa múltiplas áreas, envolve produção ou parece recorrente.

---

## Quando consultar

- Antes de tocar em produção
- Quando houver risco de repetir erro já visto
- Quando envolver mais de uma camada (backend + frontend + VPS)
- Quando não estiver claro qual é o fluxo oficial

---

## Princípios operacionais (resumo)

- Evidência > opinião  
- Reuso > invenção  
- Correção mínima > reescrita  
- Validar no ponto real antes de fechar  
- Fricção recorrente vira regra (skill/playbook/agents)

---

## Prioridade de decisão

1. Não quebrar produção  
2. Evitar retrabalho  
3. Manter consistência do acervo  
4. Velocidade de execução  

---

## Mapa por tipo de trabalho

### Ebook (produção)

Fonte: skill + scripts oficiais

Regras:
- Sempre validar PDF real (não confiar só no HTML)
- Revalidar antes de `create` (concorrência)
- Não forçar delete por duplicidade → pular
- Capa é autoral (não reaproveitar)
- Sinopse: 3 parágrafos com apelo real
- Variar direção visual intencionalmente

---

### Livro físico

Regras:
- Duplicidade é aceitável
- Freight precisa ser coerente
- Validar item criado em produção

---

### VPS / Produção

Regras:
- Explorar em modo leitura primeiro
- Não assumir nada pelo nome (container, DB, etc.)
- Verdade = estado real do ambiente
- Mudança manual precisa sobreviver a restart

---

### Frontend

Regras:
- Suspeitar de branch desatualizada antes de bug “misterioso”
- Build real > ambiente local
- Validar sintaxe/build antes de fechar

---

### Backend / Jobs

Regras:
- Scheduler precisa refletir comportamento real
- Investigar starvation antes de tuning
- Não maquiar regra no frontend
- Correção estrutural > workaround visual

---

### Criação de livro / PDF

Regras:
- Consolidar conteúdo antes de diagramar
- Capa é ativo premium
- PDF nasce de HTML/CSS + render confiável
- Evitar “arte bonita e errada”

---

## Armadilhas recorrentes

- Diagnóstico por ego → sempre começar por evidência
- Criar fluxo novo sem checar skill/script existente
- Assumir que estado não mudou (concorrência)
- Validar só input e não output real (PDF, imagem)
- Texto longo inline no PowerShell (quebra encoding)
- Resolver no frontend algo que é regra do backend
- Declarar vitória sem validar no ambiente real
- Aprender e não institucionalizar

---

## Heurística de decisão

1. Tenho evidência real?
2. Já existe fluxo pronto pra isso?
3. Existe risco de concorrência/produção?
4. A correção é local ou estrutural?
5. Onde preciso validar pra não me enganar?

---

## O que deve virar atualização deste arquivo

- Padrão de erro recorrente
- Heurística que evitou retrabalho
- Regra transversal entre áreas

---

## O que NÃO entra aqui

- Passo a passo detalhado (vai para skill)
- Caminho específico de máquina
- Regra temporária
- Segredo