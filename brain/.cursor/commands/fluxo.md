---
description: S1 — mapeia o fluxo real do código e produz o documento de fluxo
argument-hint: <tema ou ponto de entrada>
---

Etapa **S1**. Alvo: $ARGUMENTS

Acione o subagente `mapeador-fluxo`. Ele produz `docs/fluxos/{tema}/{card-id}.md`.

O padrão é S1+S3 na mesma passada com a validação consolidada S2-S4 (`validador-tecnico`),
passando o **caminho** — nunca o conteúdo. S2 separada (`validador-leve`) só na trilha completa,
com o motivo no chat. Trilha curta: o fluxo é seção da análise (`/analise`).
