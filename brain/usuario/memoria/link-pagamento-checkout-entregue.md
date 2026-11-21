---
name: link-pagamento-checkout-entregue
description: A rota link-pagamento do checkout existe desde 20/08/2026 na branch 162940_ats, já mergeada em staging; usa CHECKOUT_JWT_TOKEN e claim iss
metadata:
  type: project
---

A ponta do `checkout` que o card 162988 do CIT esperava **existe**. Foi entregue pelo Wilker
na branch `162940_ats` do repositório `solides/backend/checkout` (commits de 18 a 21/08/2026,
"Estrutura padrão", "contexto ganho", "Implementação de contexto de ganho", "Ajustes env") e
já está mergeada em `staging`, ou seja, em homologação. A branch `161899_release` continua
parada em `f7d9cf36` (04/08) e **não** é onde o código está — não existe branch `162988` lá.

O desenho é genérico: `link-pagamento/<contexto>/<jwt>` (`application/config/routes.php`),
com `finalizar` e `sucesso` no mesmo prefixo. O contexto `ganho` tem handler próprio em
`application/libraries/LinkPagamentoLib/Contexts/ganho/GanhoHandler.php` (684 linhas) e
`schema.json` apontando as views. Sistema integrador se declara pelo claim `iss` do JWT,
autorizado em `application/config/link_pagamento.php` — hoje `gestao` e `cit`, os dois com o
mesmo segredo, lido de **`CHECKOUT_JWT_TOKEN`**, a mesma env que o CIT já usa (ver
[canal-jwt-cit-para-checkout]).

O formato de URL que o CIT já montava (`CHECKOUT_URL/link-pagamento/ganho/<jwt>`) casa com a
rota entregue. O que precisa de conferência é o **conteúdo** do payload, o `metadata` da order
na Pagar.me e quem avisa o CIT depois do pagamento — ver [cartao-retorno-via-webhook-lambda].

**Why:** o documento cross-repo do card afirmava que a rota não existia e que o AC3 estava
bloqueado por peça de outro time; isso deixou de ser verdade em 20/08/2026.

**How to apply:** antes de afirmar que o fluxo do cartão está bloqueado no checkout, conferir
`origin/162940_ats` e `origin/staging` (não a `161899_release`). O repositório local em
`/var/www/html/checkout` precisa de VPN ligada para o fetch; sem VPN o GitLab interno
(10.10.6.154) dá timeout.
