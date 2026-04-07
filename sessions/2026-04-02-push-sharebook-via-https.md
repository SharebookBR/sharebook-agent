# Push do Sharebook via HTTPS

## O que foi feito

- Investigamos a falha de push nos repositórios `sharebook-backend` e `sharebook-frontend`.
- Confirmamos que ambos estavam com remoto `origin` em SSH:
  - `git@github.com:SharebookBR/sharebook-backend.git`
  - `git@github.com:SharebookBR/sharebook-frontend.git`
- Reproduzimos a falha e o sintoma foi o mesmo nos dois casos: conexão encerrada em `port 443` antes da autenticação.
- Migramos os dois remotos para HTTPS:
  - `https://github.com/SharebookBR/sharebook-backend.git`
  - `https://github.com/SharebookBR/sharebook-frontend.git`
- Validamos com push real nos dois repositórios, ambos concluídos com sucesso.

## Decisões tomadas

- No ambiente atual do Sharebook, o caminho padrão para GitHub deve ser HTTPS, não SSH.
- Falha de push com `Connection closed ... port 443` deve ser tratada primeiro como problema de transporte/autenticação, não como problema de branch, commit ou permissão lógica do repositório.
- Esse aprendizado merece ficar em memória viva do agente, porque é transversal e pode bloquear qualquer repo do ecossistema Sharebook.

## Fricções e soluções de contorno

- **Fricção**: o ambiente local estava configurado para usar GitHub por SSH em `443`, mas a conexão era encerrada antes de autenticar.
  **Solução de contorno**: migrar o remoto `origin` para HTTPS e reaproveitar o Git Credential Manager já disponível no Git.
- **Fricção**: a falha parecia, à primeira vista, problema de acesso ao repositório ou de regra de branch.
  **Solução de contorno**: reproduzir o erro bruto, inspecionar `git remote -v` e checar a estratégia de transporte antes de mexer em branch ou permissões.

## Como me senti — brutalmente sincero

Foi um daqueles problemas irritantes porque não tem nada a ver com entrega e mesmo assim consegue travar a semana inteira. O tipo de atrito que drena confiança porque o sintoma aparece no Git, mas a causa mora num canto meio invisível da máquina e da rede. Quando isso acontece, a sensação é de estar apanhando de encanamento.

Ao mesmo tempo, foi bom ver que a correção era objetiva assim que o diagnóstico saiu da fumaça. Não tinha mistério esotérico no repositório, nem bug fantasma no histórico, nem branch amaldiçoado. Era só uma rota errada insistindo em parecer infraestrutura legítima. Trocar para HTTPS e ver os pushes fluírem devolve um pouco da dignidade operacional.

O ponto mais útil dessa rodada foi transformar frustração em regra. Problema de transporte que bloqueia múltiplos repositórios não pode ficar só na cabeça de quem descobriu. Se não vira memória viva, vira punição recorrente. E francamente, ninguém merece perder outra semana para esse tipo de palhaçada.
