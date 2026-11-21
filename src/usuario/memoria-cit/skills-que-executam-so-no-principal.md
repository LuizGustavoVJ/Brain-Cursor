---
name: skills-que-executam-so-no-principal
description: code-review, security-review e simplify EXECUTAM (alteram working tree ou publicam em MR); nunca dentro de subagente, e os 3 agentes de revisao seguem sem a tool Skill
metadata:
  type: feedback
---

`code-review`, `security-review` e `simplify` (embutidas no CLI) não devolvem texto: rodam em
execução forkada. `code-review --comment` POSTA em PR/MR; `--fix` altera o working tree; `simplify`
altera o working tree SEMPRE, sem flag para desligar.

Por isso `revisor-codigo` e `especialista-seguranca` (o `especialista-refatoracao` foi aposentado na Fase 3, 25/09) continuam **sem a
ferramenta `Skill`** — a trava é estrutural, não instrução. Quem invoca é o contexto principal.
`Skill` dá o catálogo inteiro, inclusive `init`, que sobrescreveria o `CLAUDE.md`.

**Why:** esses agentes são somente leitura por desenho ("proponha, não aplique"); dar `Skill` abriria
por dentro da tool a escrita que a lista de ferramentas existe para impedir, e furaria o gate I4.

**How to apply:** invocar as três só no contexto principal, com working tree conhecido, nunca como
passo automático de etapa. Relacionado: [[habilidades-tres-origens]].
