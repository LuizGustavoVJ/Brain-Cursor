---
name: local-sh-patches-cit
description: cit tem .claude/scripts/local.sh (status/apply/restore-repo) que reverte só o patch local, sem git restore
metadata:
  type: project
---

Criado em 21/08/2026: `.claude/scripts/local.sh` no cit — `status`, `apply`, `restore-repo`. Torna
executável o gate do CLAUDE.md "rodar `local.sh restore-repo` antes de commit/PR", que até então
citava um script inexistente (os outros repos têm o deles em `docs/ambiente-local/scripts/`).

O patch vive fora do repo, em `~/patches-locais-cit/ajustes-locais-cit.patch`
(`PATCHES_LOCAIS_CIT` sobrescreve), e toca 8 arquivos — `index.php` (dotenv opcional, sem ele o app
não sobe) e `SessionHook.php` entre eles.

**Nunca usar `git restore`/`git checkout --` para limpar o patch:** `SessionHook.php` costuma ter
patch local **e** trabalho de card ao mesmo tempo, e o restore apagaria os dois. O script reverte
pelo próprio patch (`git apply -R`) e para com erro se estiverem misturados de forma inseparável.
Round-trip apply→restore verificado byte a byte. Ver [[patches-locais-cit-fora-do-git]] e
[[reverter-commit-sem-git-checkout]].
