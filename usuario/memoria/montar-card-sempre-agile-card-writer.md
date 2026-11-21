---
name: montar-card-sempre-agile-card-writer
description: "Desde 28/09/2026, montar card/épico/funcionalidade/história usa SEMPRE a skill agile-card-writer, no contexto principal; gatilho do usuário \"monta os cards disso:\""
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-28T12:29:07.747Z
---

Sempre que for preciso montar card (épico, funcionalidades, histórias EU/QUERO/PARA com DADO/QUANDO/ENTÃO), usar a skill `anthropic-skills:agile-card-writer`. O usuário aciona começando com "monta os cards disso:".

**Why:** decisão do usuário em 28/09/2026 ("coloque ela para sempre ser utilizada quando precisar montar card"). A regra "não invente nada" da skill evita card baseado em suposição.

**How to apply:** rodar no contexto principal, porque a skill pergunta e confirma o entendimento antes de gerar. Antes de perguntar, ler o mapa `dominio-*` do tema e não perguntar o que já está lá. Saída em `docs/backlog/<slug>.md`. No ADO, entregar o texto pronto para colar; o agente não cria work item. Encaixe detalhado em `.cursor/habilidades.md`.
