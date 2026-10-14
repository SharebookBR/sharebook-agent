# Unificação de Scripts e Renomeação do Corpus

**Status: concluído em 2026-10-14, aprovado pelo Raffa.**

## Problema original

O `sharebook-agent` tinha conhecimento operacional espalhado em dois lugares com lógicas diferentes: `playbooks/` (markdown) e `scripts/` (executáveis). A separação gerava custo cognitivo sem benefício real: dois lugares para procurar a mesma coisa, com nomes que não comunicavam o que cada coisa era.

## O que foi entregue

- **Scripts e playbooks unificados.** Script deixou de ser entidade de primeiro nível: mora junto do playbook que o explica (`PLAYBOOK.md` + `scripts/`), ou em `playbooks/_shared/scripts/` quando é utilitário transversal. Procura-se o playbook, e ele diz que script existe e como rodá-lo. A seção de Scripts solta no `AGENTS.md` deu lugar ao roteamento por família.
- **Corpus renomeado: a memória episódica vive em `sessions/`.** O Raffa está satisfeito com o resultado.

## O que foi abandonado (decisão do Raffa)

A proposta original de nomear as pastas como `memory-durable/` e `memory-episodic/` foi **desistida**. Os nomes canônicos continuam sendo `playbooks/` e `sessions/`. A "decisão pendente" do rascunho (renomear só `playbooks/` ou os dois) está encerrada por essa desistência.

## Para quem chegar depois

- Não reabrir a ideia `memory-durable/` / `memory-episodic/` sem motivo novo: foi considerada e descartada.
- Vocabulário vigente: **playbook** (conhecimento operacional versionado em `.md`), **família** (agrupamento com `INDEX.md`) e **sessions** (memória episódica). Está no `AGENTS.md`.
