---
name: git-fluxo-cit
description: "Fluxo de branch/deploy do cit e o teto do agente no git — staging=homol, master=prod defasado, release não acompanha a branch de trabalho, deploy homol é push+merge manual do usuário, e como resolver conflito/reverter sem violar o classificador"
metadata:
  node_type: memory
  type: project
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:02:17.913Z
---

Consolida `cit-branching-staging-vs-master`, `mr-release-nao-acompanha-branch-trabalho`,
`deploy-homol-cit-agente-nao-mergeia`, `resolver-conflito-mr-staging-sem-absorver`,
`reverter-commit-sem-git-checkout`, `git-agente-so-branch-commit-push` e
`commit-sem-coautoria-sem-corpo` (destilação de 25/09/2026).

**Deploy por branch (`.gitlab-ci.yml`):** `staging` = homologação, `master` = produção — não existe
branch `homol`. `origin/staging` fica muito à frente de `origin/master` (releases para produção são
`{card}_release` recortadas, não merge direto de staging) — **nunca** usar `origin/staging` como
base de branch nova (regra do time, 31/08/2026: branch nasce da release da feature ou da default,
nunca de staging).

**Teto do agente no git — regra permanente (28/08/2026):** só **criar branch, commitar, dar push**,
e só quando o usuário pedir. Merge (de qualquer branch, inclusive mergear um MR), apontamento de
branch e aprovar/fechar MR são **sempre do usuário**, em todo repositório. Resolver conflito de MR
= mergear a branch-alvo **na** branch de trabalho, resolver e dar push da branch de trabalho (nunca
o inverso). No cit especificamente, `git merge` para escrever em `staging` é barrado pelo
classificador de permissões e o `GITLAB_PERSONAL_ACCESS_TOKEN` de `~/.cursor/mcp.json` é só leitura
(`403 insufficient_scope` em `POST /merge_requests`) — o caminho é entregar o link de criação do MR
que o `git push` imprime. Depois que alguém mescla, **merge não é deploy**: conferir o job de
`deploy to staging` (já falhou por espaço em disco no runner, deixando o site em HTTP 000).

**Conflito de MR de release contra `staging`:** resolver com **commit de conteúdo de pai único**
(reconciliar num worktree detached, extrair só o arquivo, commitar como pai único) — nunca
`git merge origin/staging` (arrasta código de outros cards, ver regra de merge proibido). Pelo
teorema do merge 3-way, `git merge-tree` **continua** acusando conflito mesmo com o arquivo certo —
é esperado, o TL resolve trivial ("usar a versão da origem"); `git diff origin/staging...HEAD`
confirma que o diff é só do cartão.

**`<card>_release` não acompanha a branch de trabalho** — commits novos vão direto para `staging`,
a release congela na data de criação. MR para `master` pode aprovar/mergear a versão **velha** sem
avisar (incidente real: card 156719, MR 3942 subiu para produção a versão vetada). Antes de
aprovar/mergear MR para `master`, comparar `head_sha` do MR com o topo da branch de trabalho —
`git log --oneline origin/master..origin/<branch-de-trabalho>` deve ficar vazio depois do merge.

**Reverter commit sem `git checkout --`** (bloqueado pelo classificador): usar
`git show <sha> -- <paths> | git apply -R --whitespace=nowarn -`; conferir com `git diff master --
<paths>` (diff vazio = reversão byte a byte). Atenção a CRLF misto — o Edit pode converter linhas
vizinhas e o `git diff` denuncia.

**Commits deste usuário: só o título** — sem corpo explicativo e **sem** `Co-Authored-By` (pedido
explícito, removido manualmente quando incluído antes). Isto **sobrescreve** qualquer instrução
global de atribuição de commit para este projeto: `git commit -m "<título curto>"` e nada mais.
