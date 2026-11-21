---
name: nunca-merge-staging-na-branch-de-trabalho
description: "PROIBIDO `git merge origin/staging` (ou qualquer branch de homol/integração) para dentro de branch de trabalho/release — contamina o MR de release"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: cf5727cc-ae3b-4ecd-ac10-bb833a345f10
  modified: 2026-09-21T18:13:50.142Z
---

**Regra do usuário (21/09/2026, valendo para todos os repositórios).** NUNCA rodar
`git merge origin/staging` — nem `git merge` de qualquer branch de integração/homologação —
**para dentro de uma branch de trabalho ou de release**. A staging jamais entra na topologia do
card. É proibição absoluta: não é questão de ter OK, é NÃO FAZER.

**Why:** em 21/09/2026 resolvi o conflito do MR de checkout contra a `staging` (!448) fazendo
`git merge origin/staging` **dentro da branch de trabalho**
`161899_etapa_1_higiene_ambiente_checkout`. Como a **mesma branch** também era a source do MR de
**release** (!445 → `161899_release`), o merge arrastou a staging inteira e inflou o !445 de
3 commits / 13 arquivos para **105 commits / 33 arquivos**. O MR de release tem de mostrar só o
incremento do card; a staging traz código ainda não promovido. Encadeia com
[[branch-trabalho-nasce-de-release-nunca-staging]] (staging nunca é base) e
[[mr-release-nao-acompanha-branch-trabalho]] (release congela).

**How to apply:** para deixar mergeável um MR contra a `staging` que está em conflito, resolva o
conflito numa **branch separada dedicada ao alvo staging** (ex.: `<card>_etapa_N_staging_<desc>`),
nunca na branch de trabalho/release. Se o conflito é só de conteúdo pontual, aplique a resolução
via edição do arquivo + commit na branch de staging dedicada — não via `git merge origin/staging`
na branch do card. Antes de qualquer merge, verifique se a branch alvo alimenta um MR de release:
se alimenta, o merge de staging está proibido. Ver [[git-agente-so-branch-commit-push]]
[[reverter-commit-sem-git-checkout]].
