---
name: gitlab-deploy-cicd
description: >-
  Entende o pipeline GitLab do projeto atual (deploy fica fora do fluxo do
  agente) e o estado — hoje inexistente — de Playwright rodando em CI. Use ao
  revisar `.gitlab-ci.yml`, explicar o fluxo de homologação e produção,
  adicionar/depurar um job de teste E2E no pipeline, ou decidir se um gate
  automatizado substitui os gates manuais I7/I10/I13.
---

# CI/CD — GitLab Deploy e Playwright em CI

> **Branches, scripts e URLs de deploy variam por projeto** → conferir o `.gitlab-ci.yml` do repositório e o perfil `arquitetura/estado-projeto-{projeto}.md` / `ambiente-local-{projeto}.md`.

## Documentação oficial

| Tema | URL |
|------|-----|
| GitLab CI/CD | https://docs.gitlab.com/ee/ci/ |
| `.gitlab-ci.yml` reference | https://docs.gitlab.com/ee/ci/yaml/ |
| Environments | https://docs.gitlab.com/ee/ci/environments/ |
| GitLab Runner tags | https://docs.gitlab.com/runner/ |
| Playwright CI intro | https://playwright.dev/docs/ci |
| Playwright Docker image | https://playwright.dev/docs/docker |

## Pipeline (repo)

O deploy é definido no `.gitlab-ci.yml` do repositório e executado **fora do fluxo do agente**. O ciclo S1–S6 / I1–I15 **encerra na validação das evidências (I15)** — o agente **não** faz merge, deploy nem altera branch.

No **cit** (`.gitlab-ci.yml:1-58`), o pipeline tem hoje **só um stage ativo**, `deploy` — `test` está comentado (`.gitlab-ci.yml:11`). Dois jobs, cada um restrito por `only`:

| Job | `only` | Script |
|-----|--------|--------|
| `deploy to staging` | `staging` | `.gitlab-deploy-staging.sh` |
| `deploy to prod` | `master` | `.gitlab-deploy.sh` |

Há um job `test-e2e` **inteiro comentado** (`.gitlab-ci.yml:23-38`) que dispara (`trigger:`) o pipeline de outro projeto GitLab, `solides/qualityassurance/cit-ui-tests`, em vez de rodar Playwright localmente no runner do cit — sinal de que a intenção original era um pipeline E2E **externo**, não um job Playwright dentro deste `.gitlab-ci.yml`. Confirmar o estado desse projeto satélite antes de reativar.

Detalhes do pipeline (jobs, scripts, ambientes) variam por projeto → ver o `.gitlab-ci.yml` do repositório atual antes de generalizar o que está descrito acima para outro repo.

## O que o CI **não** faz hoje

- Não executa Playwright **dentro deste** `.gitlab-ci.yml` (testes são locais — I7/I10; ver skill [ambientes-e-testes](../ambientes-e-testes/SKILL.md))
- Não roda linter PHP
- Não faz build de assets modernos

## Playwright em CI — proposta (ainda não implementada)

Isto é **roadmap**, não o estado do repositório — não afirmar em evidência de card que o CI já valida E2E. Ao implementar, alinhar a imagem Docker com a versão real do `@playwright/test` em `testes/package.json` (no cit, **1.49.0** — não copiar uma versão de imagem sem checar o `package.json` primeiro):

```yaml
stages:
  - test
  - deploy

playwright-e2e:
  stage: test
  image: mcr.microsoft.com/playwright:v1.49.0-jammy
  tags:
    - aws-linux
  script:
    - cd testes
    - npm ci
    - npx playwright install --with-deps chromium
    - npm run test:e2e
  artifacts:
    when: on_failure
    paths:
      - testes/playwright-report/
      - testes/test-results/
  only:
    - merge_requests
    - staging
    - master
```

### Homol no CI (limitação)

Project `homol` exige deploy na URL homol remota do projeto (ver perfil `arquitetura/ambiente-local-{projeto}.md`). **Não** rodar homol no CI sem infraestrutura equivalente — recomendação inicial é só `test:e2e` (URL local) no CI; homol permanece manual, na URL remota (I13).

### Variáveis úteis

| Variável | Uso |
|----------|-----|
| `CI` | Playwright config: `forbidOnly`, `retries: 1` (já é assim em `testes/playwright.config.ts`, independente de rodar em CI) |
| `PLAYWRIGHT_BASE_URL` | Homol (se infra existir) |

### Checklist ao adicionar job

- [ ] Stage `test` **antes** de `deploy`
- [ ] Imagem Playwright compatível com a versão real de `@playwright/test` em `testes/package.json`
- [ ] `npm ci` (não `npm install`) para reprodutibilidade
- [ ] Artifacts de report em falha
- [ ] Não quebrar deploy existente (jobs `only`/`rules` explícitos)
- [ ] Decidir se reativa o `test-e2e` (trigger para `cit-ui-tests`) em vez de duplicar um job local

Mesmo com CI, o fluxo humano I7–I11 permanece até decisão formal de substituir gates locais por pipeline.

## MR checklist

Template: `.gitlab/merge_request_templates/Checklist.md`

## Relação com sustentação

- Evidências e E2E são **pré-requisito humano** antes de merge — não gate automatizado
- Patches Docker/homol local **não** vão para staging/prod
