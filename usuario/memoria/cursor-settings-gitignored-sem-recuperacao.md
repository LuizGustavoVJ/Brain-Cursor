---
name: cursor-settings-gitignored-sem-recuperacao
description: .cursor/ é gitignored em 7 dos 8 repos Solides — sobrescrever settings.json sem backup é perda definitiva
metadata: 
  node_type: memory
  type: project
  originSessionId: bf552633-6d14-4b82-a516-6360c1c3f001
  modified: 2026-08-05T21:21:38.318Z
---

Em 2026-08-05, `.cursor/settings.json` estava **gitignored** na maioria dos repositórios Solides — só alguns tinham o arquivo versionado. Não há histórico git para restaurar.

**Why:** qualquer sobrescrita de `.cursor/` nesses repos é irreversível pelo git; o único caminho de volta é um backup feito antes.

**How to apply:** antes de propagar ou sobrescrever `.cursor/`, copiar a pasta e o `AGENTS.md` de todos os projetos para um diretório datado fora dos repos (ex.: `~/backup-cursor-AAAAMMDD-HHMMSS`). Confirmar com `git check-ignore -q .cursor/settings.json` por projeto antes de assumir que há histórico. Ver [[padronizacao-cursor-cross-repo]] e [[proibido-git-sem-autorizacao]].
