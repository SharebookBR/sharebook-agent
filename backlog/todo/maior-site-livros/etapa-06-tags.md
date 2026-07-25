## 2. Tags

- Precisamos permitir que cada livro tenha 3 tags.
- Que essa tag seja gerada automaticamente por IA.
- Precisamos mostrar as tags clicáveis na PDP.
- Precisamos deixar o usuário navegar por tags.

---

### 📌 Regras para tags (fase inicial)

- Lista controlada (sem criação livre pelo usuário)
- Evitar excesso (sem poluição)
- Só criar tag se fizer sentido real

#### Exemplos iniciais:
- .NET
- Java
- Node
- Python
- AWS
- Azure
- GCP
- SQL
- Docker
- Kubernetes

---

## Sobre Tags
- Flexível
- Multiuso (filtro, recomendação, busca)
- Representa tecnologia, linguagem, tema específico

---

## Evolução descoberta em 25/07/2026 — conhecimento estruturado

Não limitar o modelo futuro a três tags visíveis. O pipeline editorial já lê o
índice e aproximadamente 2.000 palavras do livro; esse material permite extrair:

- tópicos principais;
- nível;
- idioma;
- pré-requisitos;
- itens para a seção "Você aprenderá".

Persistir esses campos mesmo antes da exposição na interface. As três tags
continuam úteis como resumo visual controlado, enquanto o conhecimento
estruturado alimenta filtros, recomendações, páginas por assunto e busca
semântica.
