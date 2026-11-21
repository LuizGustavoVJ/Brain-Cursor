---
description: S3 — investiga causa raiz e produz a análise técnica
argument-hint: <caminho do doc de fluxo>
---

Etapa **S3**. Documento de fluxo: $ARGUMENTS

Acione o subagente `analista-causa-raiz`, passando o caminho do fluxo.

Depois valide com `validador-tecnico` (S4), por **caminho**, com `Rodada N de 3`
(`cache_validacao.py rodada S4 <card>`). Antes, confira o cache:
`python3 .cursor/scripts/cache_validacao.py check S4 <arquivo>`.

Trilha curta: o fluxo entra como seção da análise, e a S4 valida análise **+** `evidencias.html`
numa rodada (substitui S2 e S6a-val). Se a análise concluir *implementação necessária*, peça ao
`analista-causa-raiz` as seções `## Mudança proposta` e `## Cenários de teste`.
