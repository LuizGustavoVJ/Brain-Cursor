---
name: github-actions-cicd
description: >-
  Esteira GitHub Actions do Brain-Cursor: CI antes de merge, auto-merge,
  gate pós-merge com rollback, promoção staging→main e notificações. Use ao
  editar workflows em `.github/workflows/`, explicar full-auto sem /approve,
  depurar falha de CI ou rollback, ou alinhar com gestor-de-risco.
---

# CI/CD — GitHub Actions (Brain-Cursor)

Espelha os princípios de [gitlab-deploy-cicd](../gitlab-deploy-cicd/SKILL.md) para este repositório.

## Ordem dos gates (não inverter)

1. **CI no PR** (`ci.yml`, job `lint-and-test`) — bloqueia auto-merge.
2. **Auto-merge** (`auto-merge.yml`) — só após CI verde; 0 revisões humanas.
3. **Pós-merge** (`post-merge-verify.yml`) — revalida lint/test no HEAD de `staging`/`main`.
4. **Promoção** (`promote-main.yml`) — só após pós-merge verde em `staging`.
5. **CI no PR staging→main** — falha **não** mergeia (sem rollback; nada entrou em `main`).

## Rollback

- Falha pós-merge em `staging` ou `main` → `git revert` automático + alerta `[ROLLBACK]`.
- Decisão de *estratégia* e irreversíveis externos → agente `gestor-de-risco`.
- Não desfaz: deploy fora do repo, dados em banco, webhooks já enviados.

## Documentação

- `docs/esteira-full-auto.md` — fluxo completo e passo a passo de rollback.
- `docs/operacao-repositorio.md` — branches, secrets, alertas.

## Checklist ao alterar workflow

- [ ] Test/lint **antes** de qualquer merge automático
- [ ] Falha de workflow notifica (e-mail/Slack)
- [ ] Não remover gate pós-merge sem plano de risco
- [ ] `promote-main` não dispara em push cru — só após pós-merge OK
- [ ] Nomes de status check alinhados a `lint-and-test`