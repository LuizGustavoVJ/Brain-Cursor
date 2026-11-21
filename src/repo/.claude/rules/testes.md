---
paths:
  - "testes/**"
  - "tests/**"
  - "**/*.spec.ts"
  - "**/*.spec.js"
---

# Testes Playwright

- Rode pelo resumo: `.claude/scripts/resumo_testes.sh e2e|local|homol` — registre só N/N e a
  tabela de cenários. Stdout do Playwright não vai para chat, `.md` nem HTML.
- MCP Playwright só nas etapas de teste (I7, I10, I13, I14).
- Homol (I13) só depois do OK de deploy (I12) e do HTML local aprovado (I11).
- Depois de testar com patch local, e antes de qualquer commit ou MR:
  `.claude/scripts/local.sh restore-repo`.
- Teste de tela é QA ponta a ponta com dado real (abrir, preencher, enviar, conferir retorno),
  nunca foto de estado semeado ou produto fabricado.
- Operação do Docker e dos specs: skill `ambientes-e-testes`.
