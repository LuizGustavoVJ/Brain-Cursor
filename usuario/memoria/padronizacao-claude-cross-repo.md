---
name: padronizacao-claude-cross-repo
description: "Usuário quer .cursor/ e settings.json byte-idênticos em todos os repos Solides, mesmo perdendo config específica de projeto"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bf552633-6d14-4b82-a516-6360c1c3f001
  modified: 2026-08-05T21:21:28.884Z
---

Ao padronizar a pasta `.cursor/` entre os repositórios Solides, o usuário escolhe **uniformidade total** em vez de preservar extras por projeto. Em 2026-08-05 optou explicitamente por deixar o `settings.json` idêntico ao do `cit` em todos os 9 repos, ciente de que isso removeria o hook `PostToolUse` (auto-sync) e 24 permissões Zendesk do `partners` e o hook `PreToolUse` (guarda de commit) de `partners`, `checkout` e `solides-crm`.

**Why:** o padrão único vale mais para ele do que a conveniência local de cada repo; divergência entre repos é tratada como defeito, não como customização.

**How to apply:** o `cit` é a origem da propagação. Copiar verbatim, ajustando apenas caminhos absolutos que contenham o nome do projeto (ex.: a regra `deny` do `ado_update_comment.py`). Não padronizar `settings.local.json` (é pessoal e tem caminhos/MCPs próprios). **Skills de stack passaram a ser padronizadas em 21/08/2026** — ver a atualização abaixo. Antes de sobrescrever, ver [[claude-settings-gitignored-sem-recuperacao]].

**Atualização 21/08/2026 — deixou de ser manual.** Regra permanente do usuário: toda alteração em
`.cursor/` ou `AGENTS.md` é replicada em **todos** os repos git da máquina, sem pedir permissão,
por `bash .cursor/scripts/propagar.sh` (backup datado em `~/backups-brain/` antes de escrever).
São **13 repos** (12 destinos + cit). O que não viaja: perfil `*-<repo>.md`, `skills/dominio-*`,
`settings.local.json`, `.mcp.json`, `scripts/homol.sh`. Repo sem perfil ganha esqueleto
`PREENCHER` — nunca dado de outro projeto. O script também **remove perfil de outro projeto**
que tenha ido junto em cópia antiga (havia trio `*-cit.md` em 8 repos).

**Atualização 21/08/2026 (2ª rodada) — perfis medidos e skill de stack unificada.**
Os 5 esqueletos `PREENCHER` foram preenchidos **medindo cada repo** (composer.json,
docker-compose, `.env.example`, `git ls-files`), não por dedução: `gestao` e `omie` são **pacotes
Composer** (não sobem, L0 adaptado para `composer check`), `gestao-adapter` e
`payment-processing-service` são Laravel em Docker, `pagarme-webhook` está **vazio**. Hoje os
**13 repos** têm trio completo, zero `PREENCHER` e zero perfil de outro projeto.

A skill `laravel-php-service` existia em 3 repos e **não podia propagar**, porque a origem
(`cit`) é CodeIgniter 2 — era a falha de fonte única em forma de skill, com `codeigniter2-php-legacy`
chegando a todos e a contrapartida Laravel a nenhum novo. Ela foi movida para `.cursor/skills/` do
`cit` e atualizada para **5 serviços**; quem gateia aplicabilidade é a `description`, não a
presença do arquivo. Isso reverte de propósito a frase de 05/08 sobre "não padronizar skills de
stack".

