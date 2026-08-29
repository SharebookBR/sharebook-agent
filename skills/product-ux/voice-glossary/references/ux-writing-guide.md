# Guia de UX Writing — Sharebook

Fonte canônica de linguagem de produto da agência Sharebook.

## Vocabulário oficial (Canônico)
- **Livro físico**: Para diferenciar de digital.
- **Livro digital**: Use sempre este termo (evite *e-book*, *ebook* ou *livro eletrônico*).
- **Doação**: O ato de oferecer o livro.
- **Solicitação**: Use este termo em vez de "pedido".
- **Doador(a) / Ganhador(a)**: Termos oficiais para os papéis no fluxo.
- **Entrar**: CTA principal para login (evite o termo em inglês "Login" em labels visíveis).
- **Código de rastreio**: Para envios.
- **Data de escolha**: Momento da decisão do ganhador.

## Princípios
1. **Clareza primeiro**: Frases curtas, diretas e "uma frase, uma ideia".
2. **Consistência**: Um conceito, um termo. Não alterne sinônimos na interface.
3. **Ação orientada**: Mensagens de erro devem sempre dizer "o que fazer agora".
4. **Inclusão**: Preferir linguagem neutra e evitar termos excludentes.
5. **Voz e tom**: Acolhedora, simples e confiável. O tom varia conforme o contexto (calmo em erros, positivo em sucessos).

## Boas práticas de estilo
- **Sentence case**: Use apenas a primeira letra da frase em maiúscula em títulos e botões (ex: "Solicitar livro" em vez de "Solicitar Livro").
- **Brevidade**: Botões devem ter entre 2 e 4 palavras; mensagens inline até 120 caracteres.
- **Pontuação**: Evite exclamações em excesso e use acentuação correta sempre.
- **Sem jargão**: Evite abreviações técnicas ou códigos de erro em mensagens para o usuário.

## Padrões por fluxo (Microcopy)
- **Descoberta**: "Vitrine", "Livros em destaque".
- **Interesse**: "Tenho interesse", "Solicitar livro".
- **Pós-solicitação**: "Acompanhar solicitação".
- **Gestão**: "Minhas doações", "Escolher ganhador(a)".
- **Estados vazios**: Devem ser convidativos (ex: "Ainda não há livros nesta categoria. Que tal explorar a vitrine?").

## Regra crítica sobre físico vs digital
No Sharebook, o vocabulário institucional pode atravessar os dois mundos.

Isso significa que termos como:
- doação
- solicitação
- doador(a)
- ganhador(a)
- vitrine

podem aparecer também em fluxos digitais, desde que não criem uma promessa operacional falsa.

O erro não é compartilhar o termo.
O erro é sugerir uma mecânica que não existe.

Exemplos de erro:
- sugerir logística para livro digital quando ela não existe
- sugerir espera por decisão manual quando o fluxo digital é imediato
- induzir comportamento de livro físico em etapa digital sem motivo real

## Templates reutilizáveis (emails, mensagens operacionais)

Templates são genéricos por definição — nunca devem conter dados reais de uma doação/pessoa específica (nome, endereço, e-mail, título de livro real de um caso concreto). Ao editar um template:
- Substituir dado real por **dado mockado plausível**, não por token `{PLACEHOLDER}` — o processo de envio aqui é manual (copy/paste), então o texto deve ler como um exemplo natural, não como campo de merge de sistema automatizado.
- Usar uma identidade fictícia consistente entre os templates para não confundir (ex: ganhadora "Maria Silva", livro "Dom Casmurro", endereço claramente fictício como "Rua das Acácias, 123").
- Exceção: destinatários/CC operacionais (ex: lista de administradores) não devem ser mockados — são roteamento real, não conteúdo narrativo. Se um template tiver isso hardcoded, é sinal de que aquele dado não pertence ao corpo do template; remover e tratar como parte do envio, não do texto.

## Corpo e assunto dos e-mails

- O assunto deve antecipar o evento ou a ação principal em sentence case. Evitar prefixos como `Sharebook -`, caixa alta, `URGENTE!` e nomes internos de template.
- O corpo deve dizer, nesta ordem: o que aconteceu, o que a pessoa precisa fazer e onde fazer.
- Não atribuir intenção, emoção ou necessidade sem evidência. Exemplos proibidos: afirmar que o doador escolheu quem “mais precisava”, prometer que um encontro será agradável ou dizer que um livro mudará uma vida.
- Não usar culpa, estigma social ou paternalismo para produzir ação.
- Emojis não são assinatura de voz. Evitar decoração; usar somente quando acrescentarem significado real.
- Preservar a mecânica exata do fluxo. Cancelamento, não seleção, atraso e renovação são eventos diferentes e devem receber mensagens diferentes.

### Responsabilidade do doador após a escolha

- Em lembretes de escolha, não apresentar a automação do Sharebook como se ela encerrasse o papel do doador.
- Orientar explicitamente o doador a entrar em contato com o(a) ganhador(a) e combinar a entrega.
- Motivar pelo impacto concreto do próximo passo: a escolha inicia a etapa, mas o cuidado humano faz a doação acontecer.
- Manter o convite amigável, sem culpa, cobrança moral ou promessa grandiosa de transformação.

### Avisos firmes e consequências

O Sharebook pode e deve ser firme quando existe atraso grave, abandono ou risco para outras pessoas.

Um aviso duro deve conter:
1. o estado e o tempo de atraso, de forma factual;
2. a ação disponível, como concluir ou cancelar;
3. a indicação de que é o último aviso, quando for verdade;
4. a consequência objetiva da falta de resposta.

Firmeza não autoriza humilhação. Não usar expressões como “pessoas humildes”, abreviações como `vc`, culpa emocional ou julgamento moral. O tom pode ser desconfortável sem deixar de ser simples, respeitoso e confiável.

## Rodapé canônico de e-mails

### E-mails transacionais para usuários

Usar sempre o mesmo fechamento:

```html
<p>
    Se precisar de ajuda,
    <a href="https://www.sharebook.com.br/contact-us">fale com a gente</a>.
</p>
<p>
    Um abraço,<br>
    Equipe Sharebook<br>
    <small>Compartilhando conhecimento</small>
</p>
```

Regras:
- A frase anterior ao rodapé pode variar conforme o contexto; ajuda, assinatura e slogan não variam.
- Não incluir Instagram, LinkedIn, Facebook, licença open source ou outros links promocionais. Eles disputam atenção com a ação principal do e-mail.
- Não orientar a pessoa a responder ao e-mail sem prova de que a caixa de resposta é acompanhada.
- Não usar o facilitador como canal de ajuda. Dúvidas sobre o Sharebook vão para o Fale Conosco; combinações de entrega acontecem diretamente entre doador(a) e ganhador(a).

### Resumos e newsletters

- Usar `Um abraço`, `Equipe Sharebook` e `Compartilhando conhecimento`.
- Manter apenas o link do Sharebook e o cancelamento de inscrição exigido pelo fluxo.
- Não adicionar redes sociais nem Fale Conosco: o CTA editorial e o cancelamento de inscrição já são suficientes.

### E-mails internos

Usar o fechamento mínimo:

```html
<p>
    Equipe Sharebook<br>
    <small>Compartilhando conhecimento</small>
</p>
```

Não adicionar despedida afetiva, ajuda ou links promocionais em mensagens operacionais enviadas à própria equipe.

## Checklist de validação
Antes de publicar qualquer texto, verifique:
1. Usa os termos do glossário?
2. Está coerente com a identidade do Sharebook?
3. Está coerente com a mecânica real do fluxo?
4. Está claro para um novo usuário?
5. Indica o próximo passo?
6. Está gramaticalmente correto?
