# 📚 Sharebook — Plano de Evolução de Categorias

## 🎯 Objetivo
Vamos escalar o acervo para 1000 livros digitais. Antes disso precisamos repensar as categorias.

---

## ⚙️ Criar feature de subcategorias 

- Auto relacionamento. 
- Exemplo: Tecnologia > Linguagens de programação
- Entidade Book continua como está. 
- Na hora de mostrar a categoria no front, vamos ter que pensar em algo engenhoso e elegante.

### Estrutura desejada:

Criar essas subcategorias quando a feature for entregue.

#### Tecnologia
- Backend
- Frontend
- Cloud
- Dados
- IA
- DevOps

#### Ficção
- Terror
- Fantasia
- Ficção científica
- Mistério / Suspense
- Aventura
- Drama


---

# 🧠 Princípios de arquitetura

## Categoria
- Define intenção principal de navegação
- Poucas, claras e estáveis

## Subcategoria
- Refinamento dentro da categoria
- Organiza sem poluir



---

# 🔥 Estratégia geral

1. Crescer acervo rapidamente
2. Preparar estrutura sem impactar UX
3. Ativar organização apenas quando houver volume
4. Evoluir baseado em comportamento real dos usuários

---

# ⚠️ Riscos

- Overengineering precoce
- Excesso de categorias
- Refatoração desnecessária sem base em dados

---

# 🧾 Conclusão

- Curto prazo: volume + estrutura invisível
- Médio prazo: ativar subcategorias e tags
- Longo prazo: otimizar com base em uso real

> Você não está organizando livros  
> Você está organizando intenção de leitura