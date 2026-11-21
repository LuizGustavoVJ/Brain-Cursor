---
name: patches-locais-cit-fora-do-git
description: Patches para rodar o cit localmente ficam em /home/luizfinotello/patches-locais-cit/ (fora do git); nunca commitar
metadata: 
  node_type: memory
  type: project
  originSessionId: fd39086c-f603-40a1-86da-ad7a8b7afca9
  modified: 2026-07-31T14:48:18.056Z
---

O repositório `cit` **não tem** mecanismo de patch local versionado (não existe `docs/ambiente-local/` nem `local.sh` — ao contrário do que o CLAUDE.md genérico sugere). Os ajustes necessários para rodar local ficam em `/home/luizfinotello/patches-locais-cit/`, com README explicando cada mudança:

- `ajustes-locais-cit.patch` — diff único, aplicar com `git apply` (sem commit)
- `0001-Ajuste-local.patch` / `0002-Ajuste-local.patch` — formato `format-patch`, para `git am`

O patch mais crítico é em `index.php`: torna o carregamento de `cit-<ENV>.env` opcional (`safeLoad` + `is_readable`). **Sem ele o app local não sobe**, porque `/var/www/html/cit-development.env` não existe na máquina e o código de `origin/master` faz `$dotenv->load()` obrigatório. Os demais desligam o profiler no `SessionHook`, liberam métodos de `termo_aceite` do bypass de sessão e ajustam log/cron.

**Why:** em 19/06/2026 esses ajustes foram commitados por engano no `master` local (commits "Ajuste local" `a3a8704b9` e `d75b323c1`) e chegaram a ir para a branch remota `158930_release_ajuste_recebimetno_deal_cnpj`. Em 31/07/2026 a branch remota foi excluída pelo usuário e o `master` local foi sincronizado com `git reset --hard origin/master`.

**How to apply:** ao criar branch nova (inclusive a partir de `origin/staging`), aplicar o patch com `git apply` e **nunca commitá-lo**; reverter com `git apply -R` antes de qualquer commit ou MR. Ver [[cit-branching-staging-vs-master]].
