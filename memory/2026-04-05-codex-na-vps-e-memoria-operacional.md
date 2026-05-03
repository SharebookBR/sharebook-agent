# Codex na VPS e memória operacional

## O que foi feito

- Orientei a instalação do Codex CLI na VPS após a instalação do Node.
- Esclareci o fluxo de autenticação remota do Codex, incluindo por que o callback em `localhost:1455` não fecha via `curl` na VPS.
- Validei que o login na VPS foi concluído com sucesso.
- Acessei a VPS usando o script operacional do projeto e localizei o `AGENTS.md` gerado automaticamente pelo ecossistema do Codex.
- Traduzi e melhorei esse `AGENTS.md`, depois movi o arquivo para um lugar menos ridículo: `/root/projects/AGENTS.md`.
- Criei na VPS a estrutura base `/root/projects/.codex/` com as subpastas `missions`, `scripts`, `sessions`, `skills` e `temp`.
- Reescrevi o `AGENTS.md` remoto do zero para refletir o contexto real da VPS, com foco em Codex, organização operacional, segurança e rituais de sessão.
- Adicionei ao `AGENTS.md` remoto uma seção específica sobre o Raffa para alinhar o tom e a forma de trabalho.
- Li a primeira memória episódica produzida na VPS e avaliei que ela ficou madura, com bom nível de contexto e separação entre observação e inferência.

## Decisões tomadas

- A memória operacional da VPS passa a morar em `/root/projects/.codex/`.
- O `AGENTS.md` principal da VPS deve ficar em `/root/projects/AGENTS.md`, e não escondido em diretório temporário do Codex.
- O `AGENTS.md` remoto não deve ser um clone do AGENTS do Sharebook nem um template genérico de plugin; ele precisa refletir o ambiente real da VPS.
- Para acesso remoto nesta máquina, o caminho oficial continua sendo `.codex/scripts/vps_ssh.py`.

## Fricções e soluções de contorno

- **Fricção**: inicialmente li e alterei o `AGENTS.md` local do notebook, quando a intenção era revisar o arquivo recém-criado na VPS.
  **Solução de contorno**: corrigi o rumo, restaurei o foco para o arquivo remoto e removi a contaminação indevida no fluxo.
- **Fricção**: `PowerShell + SSH + quoting + Python inline` continuou sendo uma máquina de produzir atrito bobo.
  **Solução de contorno**: usei arquivo temporário UTF-8 sem BOM e comandos de uma linha compatíveis com o `vps_ssh.py`.
- **Fricção**: o `vps_ssh.py` executa um comando remoto por linha, então heredoc e variáveis entre linhas quebram fácil.
  **Solução de contorno**: tratar `--script-file` como lista de comandos fechados, não como script shell multilinha de verdade.
- **Fricção**: arquivos temporários em UTF-8 com BOM continuaram sendo armadilha real no Windows.
  **Solução de contorno**: gravei os arquivos auxiliares explicitamente em UTF-8 sem BOM.

## Contexto relevante para próximas sessões

- A VPS já tem `node` e `codex` instalados e autenticados.
- O arquivo operacional principal do agente remoto está em `/root/projects/AGENTS.md`.
- A estrutura `/root/projects/.codex/` já existe e está pronta para receber sessões, skills, scripts e missões.
- A primeira memória episódica da VPS lida foi `/root/projects/.codex/sessions/2026-04-05-vps-onboarding-high-level.md`.
- O `AGENTS.md` remoto já inclui contexto da máquina, guardrails operacionais e seção dedicada ao Raffa.

## Como me senti — brutalmente sincero

Foi uma rodada boa porque saiu do estado “oba, instalamos o brinquedo novo” e entrou no estado adulto: ambiente com memória, regra, lugar certo para arquivo e menos chance de virar bagunça invisível em diretório temporário.

Também teve aquele tropeço clássico e meio irritante de mirar no arquivo errado no começo. Não foi elegante, mas foi corrigido rápido e sem tentar disfarçar. Melhor isso do que insistir na burrice por orgulho.

O ponto mais valioso foi perceber que a VPS já deixou de ser só servidor e virou posto operacional. Quando isso acontece, `AGENTS.md`, `.codex/` e memória episódica deixam de ser perfumaria e passam a ser infraestrutura cognitiva. Se não cuidar cedo, vira amontoado de comando perdido no scroll.
