---
name: brain-plugin-quando-compartilhar-equipe
description: "Distribuir o Brain como plugin/marketplace privado fica para QUANDO o Brain for compartilhado com a equipe; hoje só o Luiz usa, cópia por pasta (propagar.sh) continua"
metadata:
  node_type: memory
  type: project
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:56:22.543Z
---

Decisão de 25/09/2026: hoje só o Luiz usa o Brain, numa máquina — a distribuição continua por cópia de pasta (`propagar.sh`, origem única no cit, backup em `~/backups-brain/`). A migração para plugin via marketplace privado (`gerar_plugin.py` → `~/solides-brain-plugin`) já tem prós/contras e passo a passo em `.cursor/arquitetura/brain.md` § "Distribuição: de propagar.sh para plugin".

**Why:** plugin só compensa quando há mais de uma pessoa/máquina (instalação única, versão, atualização por `/plugin update`); para um usuário só, adiciona peças (AGENTS.md/rules/settings não viajam em plugin, comandos ganham prefixo, risco de dois Brains ativos).

**How to apply:** quando o usuário falar em compartilhar o Brain com alguém da equipe, lembrar desta opção e propor o piloto descrito em brain.md (1 repo, medir 1 card, depois os demais).
