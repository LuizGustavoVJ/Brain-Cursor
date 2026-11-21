---
name: aba-unica-por-card-obrigatoria
description: Aba única por card é OBRIGATÓRIA (25/09/2026) — o agente deve alertar o usuário sempre que ele mudar de card/assunto na mesma aba
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T17:43:27.033Z
---

Uma aba (sessão) = um card. Se o usuário trouxer outro card ou outro assunto na mesma aba, o agente **alerta antes de seguir**: "Você mudou do card X para o Y nesta aba — abra uma aba nova para o Y (a regra é aba única por card)". Não recusa o trabalho; alerta e aguarda a decisão.

**Why:** a análise do Brain (25/09) mostrou 3 sessões com 95% do volume, 11–20 dias cada, misturando cards — contexto inflado, medidor com fase do card errado, destilação nunca feita.

**How to apply:** conferir o card da sessão a cada mensagem (hook UserPromptSubmit cobra de forma determinística); o estado da fase/card é por sessão, não por repo. Relaciona-se com [[destilacao-obrigatoria-a-cada-card]] — ao trocar de card, o card anterior precisa ter sido destilado.
