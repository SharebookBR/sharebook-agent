# Missão — Tecnologia CC (livros com licença aberta clara)

## Objetivo
Construir uma nova frente de ingestão de livros de tecnologia com risco jurídico baixo, priorizando obras com licença Creative Commons explicitamente declarada na fonte oficial.

## Contexto
A frente anterior de tecnologia mostrou uma armadilha clara: material publicamente acessível nem sempre é material redistribuível com segurança. Para o Sharebook, a régua precisa ser mais dura.

Esta missão existe para montar um acervo de tecnologia que possa ser publicado sem gambiarra jurídica, sem depender de interpretação criativa de README e sem hospedar PDF cinzento.

## Princípio operacional
Só entra na fila principal o que tiver evidência suficiente de redistribuição permitida.

Regra prática:
- licença CC explícita na obra, PDF, site oficial ou repositório oficial → elegível
- licença ambígua, só gratuita, ou declaração vaga → fora da fila principal
- se a licença permitir leitura mas não redistribuição, não serve para o produto atual

## Critério de entrada
Cada item precisa passar por estes checks:
1. fonte oficial confirmada
2. licença identificada
3. tipo de licença compatível com redistribuição no Sharebook
4. formato disponível e estável (PDF, HTML estruturado, EPUB ou fonte conversível)
5. autoria e atribuição claras

## Critério de risco
### Verde
Pode redistribuir com atribuição e preservação da licença.
Ex.: CC BY, CC BY-SA, CC BY-NC, CC BY-NC-SA.

### Amarelo
Exige revisão manual antes de subir.
Ex.: licença declarada no repo mas não visível na obra; dúvida sobre artefato final; restrição operacional não resolvida.

### Vermelho
Não entra no fluxo atual.
Ex.: sem licença explícita; rights reserved; link gratuito sem autorização de redistribuição; licença incompatível com o modelo do produto.

## Observação importante sobre ND
Licenças com ND (NoDerivatives), como CC BY-NC-ND, exigem cuidado extra.
Se o fluxo do Sharebook implicar alterar arquivo, converter formato, reempacotar, mexer em capa, inserir branding, OCR, recompressão ou qualquer transformação na obra, tratar como **amarelo** até validar compatibilidade.
Se for redistribuição fiel do arquivo original com atribuição correta, pode ser elegível.

## Primeira safra candidata

### Candidatos levantados
1. Eloquent JavaScript — Marijn Haverbeke  
   Link: https://eloquentjavascript.net/  
   Licença informada: CC BY-NC

2. You Don’t Know JS Yet: Get Started — Kyle Simpson  
   Link: https://github.com/getify/You-Dont-Know-JS  
   Licença informada: CC BY-NC-ND 4.0

3. You Don’t Know JS Yet: Scope & Closures — Kyle Simpson  
   Link: https://github.com/getify/You-Dont-Know-JS  
   Licença informada: CC BY-NC-ND 4.0

4. Think Python (3rd ed) — Allen B. Downey  
   Link: https://greenteapress.com/wp/think-python-3rd-edition/  
   Licença informada: CC BY-NC-SA 4.0

5. Think Java (2nd ed) — Allen B. Downey, Chris Mayfield  
   Link: https://greenteapress.com/wp/think-java-2e/  
   Licença informada: CC BY-NC-SA 4.0

6. Think C++ — Allen B. Downey  
   Link: https://greenteapress.com/wp/think-c/  
   Licença informada: CC BY-NC-SA 4.0

7. Think DSP — Allen B. Downey  
   Link: https://greenteapress.com/wp/think-dsp/  
   Licença informada: CC BY-NC-SA 4.0

8. Think OS — Allen B. Downey  
   Link: https://greenteapress.com/wp/think-os/  
   Licença informada: CC BY-NC 3.0

9. Think Data Structures — Allen B. Downey  
   Link: https://greenteapress.com/wp/think-data-structures/  
   Licença informada: CC BY-NC-SA

10. Think Complexity (2nd ed) — Allen B. Downey  
    Link: https://greenteapress.com/wp/think-complexity-2e/  
    Licença informada: CC BY-NC-SA 4.0

11. Think Stats (2nd ed) — Allen B. Downey  
    Link: https://greenteapress.com/wp/think-stats-2e/  
    Licença informada: CC BY-NC-SA 4.0

12. Think Bayes (2nd ed) — Allen B. Downey  
    Link: https://greenteapress.com/wp/think-bayes/  
    Licença informada: CC BY-NC-SA 4.0

13. Modeling and Simulation in Python — Allen B. Downey  
    Link: https://greenteapress.com/wp/modsimpy/  
    Licença informada: CC BY-NC-SA 4.0

14. The Little Book of Semaphores — Allen B. Downey  
    Link: https://greenteapress.com/wp/semaphores/  
    Licença informada: CC BY-NC-SA 4.0

15. Elements of Data Science — Allen B. Downey  
    Link: https://greenteapress.com/wp/elements-of-data-science/  
    Licença informada: CC BY-NC-SA 4.0

16. SICP (JavaScript Edition) — Abelson, Sussman, Henz  
    Link: https://sicp.sourceacademy.org/sicpjs.pdf  
    Licença informada: CC BY-NC-SA 4.0

17. Invent Your Own Computer Games with Python — Al Sweigart  
    Link: https://inventwithpython.com/inventwithpython_3rd.pdf  
    Licença informada: CC BY-NC-SA 3.0

18. Making Games with Python & Pygame — Al Sweigart  
    Link: https://inventwithpython.com/makinggames.pdf  
    Licença informada: CC BY-NC-SA

19. The Recursive Book of Recursion — Al Sweigart  
    Link: https://inventwithpython.com/recursion/  
    Licença informada: CC BY-NC-SA 3.0

20. The Linux Command Line — William Shotts  
    Link: http://linuxcommand.org/tlcl.php  
    Licença informada: CC BY-NC-ND

## Estratégia de execução
### Fase 1 — validação jurídica mínima
Para cada item:
- abrir fonte oficial
- localizar licença na página e, se possível, dentro do PDF/obra
- confirmar se a licença vale para a obra e não só para o site/repo
- registrar evidência curta
- classificar em verde, amarelo ou vermelho

### Fase 2 — validação editorial e operacional
Para os verdes:
- validar formato real do livro
- verificar se a obra é boa o bastante para o acervo
- mapear categoria folha no Sharebook
- verificar se precisa capa própria ou se a original serve
- decidir estratégia de importação

### Fase 3 — lote piloto
Subir primeiro um lote pequeno, de preferência 3 a 5 livros, para validar:
- fluxo técnico
- padrão de metadados
- padrão de sinopse
- adequação da categoria
- impacto de licença NC/ND no produto

## Suspeitas úteis
- Green Tea Press parece promissora demais para ignorar.
- Obras do Al Sweigart também têm boa chance de virar lote forte.
- Itens com ND precisam de leitura fria, sem euforia.
- Se o Sharebook monetizar diretamente esse acervo, NC precisa revisão de compatibilidade comercial.

## Perguntas em aberto
- O modelo atual do Sharebook é compatível com obras NC?
- Recompressão, OCR, mudança de capa, conversão de formato ou padronização de arquivo contam como derivação relevante para ND no nosso fluxo?
- Vamos aceitar HTML-based books no acervo ou exigir artefato fechado tipo PDF/EPUB?

## Próximo passo recomendado
Validar juridicamente os 20 itens acima e produzir uma lista canônica com três estados:
- pode subir
- revisar
- descartar

## Definição de pronto desta missão
A missão fica madura quando existir:
- uma shortlist canônica de fontes/livros de tecnologia juridicamente utilizáveis
- um critério repetível de elegibilidade
- um primeiro lote piloto pronto para ingestão
