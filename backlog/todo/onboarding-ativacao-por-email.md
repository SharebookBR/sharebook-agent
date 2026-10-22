# Onboarding e ativação por e-mail

## Objetivo

Transformar um cadastro novo em primeiro valor percebido no Sharebook: a pessoa encontra e solicita/baixa um livro ou começa uma doação. O cadastro não pode terminar numa tela silenciosa, deixando a pessoa sem saber como participar.

É uma jornada de **onboarding e ativação por e-mail** (também chamada de *drip campaign* ou fluxo de nutrição), não uma newsletter genérica.

---

## MVP — sequência de cinco e-mails

Cada e-mail tem uma ação principal, link rastreável e deve levar à superfície exata do produto.

| Quando | Tema | Ação principal |
|---|---|---|
| Imediato | Boas-vindas: como o Sharebook funciona | Explorar o acervo / começar uma doação |
| Dia 1 | Encontrar o próximo livro | Buscar, navegar por categorias e solicitar ou baixar |
| Dia 3 | Fechar o ciclo | Entender como doar e cadastrar um livro físico |
| Dia 5 | Participar sem frustração | Entender regras reais: solicitação não é reserva, escolha da pessoa doadora e prazos |
| Dia 7 | Conhecer a comunidade | Entrar voluntariamente na comunidade/Canal do WhatsApp, se ela existir |

O e-mail imediato não substitui comunicações transacionais obrigatórias, como confirmação de conta ou recuperação de senha.

---

## Regras de comportamento

- A sequência começa uma única vez quando a conta é criada.
- Cancelar os e-mails restantes quando a pessoa se descadastrar de comunicações não essenciais, desativar a conta ou tiver e-mail em supressão/bounce.
- Não enviar instrução que já perdeu relevância: após baixar/solicitar livro, não insistir em “como solicitar”; após cadastrar doação, não insistir em “como doar”.
- V1 pode trocar o conteúdo pelo próximo passo mais útil; não precisa criar dezenas de ramificações. O requisito é não repetir uma aula concluída.
- O convite de WhatsApp é estritamente **opt-in**. Nunca adicionar número automaticamente, importar contatos nem tratar o grupo como canal obrigatório de suporte.
- A comunidade só entra na sequência quando houver proposta, moderação e canal efetivamente prontos. Sem isso, o quinto e-mail fecha a jornada no próprio Sharebook.
- O rodapé canônico, descadastro e regras de envio do Sharebook continuam obrigatórios.

---

## Escopo técnico

- Modelar estado individual da jornada: entrada, etapa, agendamento, envio, cancelamento e motivo de supressão.
- Disparar os envios pelo mecanismo de fila/e-mail já existente; não chamar SMTP diretamente no fluxo de cadastro.
- Job idempotente: reexecução não pode duplicar etapa para a mesma pessoa.
- Registrar eventos mínimos de ativação: cadastro, abertura/clique quando disponíveis, primeira solicitação, primeiro download e primeira doação cadastrada.
- Criar templates próprios, responsivos e consistentes com os e-mails transacionais atuais.
- Linkar para destinos reais e autenticados quando necessário; nada de CTA que desembarca numa página morta ou exige que a pessoa redescubra o caminho.
- Administrador deve conseguir consultar o estado da jornada e interrompê-la para um usuário sem editar banco manualmente.

---

## Fora do MVP

- Pontuação, badges, gamificação ou campanhas sazonais.
- Automação por WhatsApp, chatbot ou inscrição automática em grupos.
- Personalização por IA.
- Funil sofisticado de múltiplas personas; a primeira versão adapta apenas pelo comportamento essencial.
- Newsletters recorrentes.

---

## Métrica de sucesso

Medir coortes de novos cadastros e comparar antes/depois da sequência:

- % que alcança ativação em 7 dias: primeira solicitação, download ou doação cadastrada;
- tempo até a primeira ação de valor;
- entrega, abertura e clique por etapa;
- descadastros, bounces e reclamações;
- conversão do convite de comunidade, se o canal existir.

O objetivo não é taxa de abertura bonita: é mais gente participando do ciclo do Sharebook sem precisar pedir socorro.

---

## Critérios de aceite

- Novo cadastro elegível recebe no máximo uma vez cada uma das cinco etapas, nas datas planejadas.
- Quem se desinscreve, fica suprimido ou desativa a conta não recebe etapas futuras.
- Quem já executou a ação ensinada não recebe o mesmo conteúdo como próximo passo.
- Falha ou retry do job não duplica e-mail.
- Todos os CTAs foram testados logado e deslogado.
- E-mails renderizam no formato visual atual, têm rodapé canônico e testes de template.
- Dashboard/consulta administrativa permite verificar, por usuário, quais etapas foram enviadas e por quê.
