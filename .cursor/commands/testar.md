---
description: I7/I8/I10/I13 — roda a suíte, escreve o anexo do E2E e devolve só o placar
argument-hint: e2e | local | homol
---

Alvo de teste: **$ARGUMENTS**

Rode `.cursor/scripts/fase.sh` da etapa correspondente (e2e→I7, local→I10, homol→I13) e
acione o subagente `testador` com o alvo e a trilha. Trilha curta: não há `e2e` — o `local` (I10)
é o teste antes do homol.

O gate é **100% pass**. Traga ao chat apenas `N/N`, tempo e falhas — **nunca** o stdout do
Playwright.

Em `e2e`, o **I8** (`testes-e2e.md`) sai na mesma passada: quem rodou a suíte tem o número, e o
orquestrador não redige anexo que ele não mediu.
