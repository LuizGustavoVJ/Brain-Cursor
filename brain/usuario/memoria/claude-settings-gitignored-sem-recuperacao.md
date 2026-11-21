---
name: claude-settings-gitignored-sem-recuperacao
description: .claude/ é gitignored em 7 dos 8 repos Solides — sobrescrever settings.json sem backup é perda definitiva
metadata: 
  node_type: memory
  type: project
  originSessionId: bf552633-6d14-4b82-a516-6360c1c3f001
  modified: 2026-08-05T21:21:38.318Z
---

Em 2026-08-05, `.claude/settings.json` estava **gitignored** em `cit`, `debt-processing-service`, `gestao`, `hubspot-adapter`, `ibc-assessment`, `omie-adapter`, `partners` e `solides-crm` — só o `checkout` tinha o arquivo versionado. Não há histórico git para restaurar.

**Why:** qualquer sobrescrita de `.claude/` nesses repos é irreversível pelo git; o único caminho de volta é um backup feito antes.

**How to apply:** antes de propagar ou sobrescrever `.claude/`, copiar a pasta e o `CLAUDE.md` de todos os projetos para um diretório datado fora dos repos (ex.: `~/backup-claude-AAAAMMDD-HHMMSS`). Confirmar com `git check-ignore -q .claude/settings.json` por projeto antes de assumir que há histórico. Ver [[padronizacao-claude-cross-repo]] e [[proibido-git-sem-autorizacao]].
