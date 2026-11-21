---
description: I2-html/I9/I11/I14 — monta o HTML do card e o comando de postagem
argument-hint: <etapa: I2-html|I9|I11|I14>
---

Etapa de HTML: **$ARGUMENTS**

Acione o subagente `escritor-evidencias` com a etapa e a trilha do card:

| Etapa | Arquivo | Conteúdo |
|---|---|---|
| **I2-html** *(completa)* | `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html` | plano nas 13 seções do guia — sem PNG |
| **I9** *(completa)* | `evidencias.html` | implementação + E2E |
| **I11** | `evidencias.html` | completa: bloco local **L01–LN** + E2E · curta: implementação + local |
| **I14** | `evidenciashomol.html` | E2E (se houve) + homol **U01–UN** |

Os prints vêm dos specs do `testador`; o escritor não navega. Nunca misture os blocos (`U01` no
bloco local, homol em `evidencias.html`, teste no `plano.html` são erro).

Depois valide com `validador-tecnico` (`cache_validacao.py rodada <ETAPA> <card>` → `Rodada N de 3`):
em I2-html é o **I2-val**; em I11 da curta, a rodada confere também código vs plano; I11 + I15
consolidam quando o homol vem na sequência (`fluxo-completo.md` § *Validação consolidada*).
Entregue o caminho do HTML e **pergunte**: *"Posto eu o `<arquivo>` no card `<n>`, ou te entrego o
comando?"* — poste só com "sim" (vale para aquela postagem). Subagente nunca posta.
