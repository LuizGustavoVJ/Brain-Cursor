---
name: ambientes-e-testes
description: >-
  Opera o Docker do ambiente local Solides e escreve/executa os testes
  Playwright ponta a ponta nos três alvos: E2E (I7), local (I10) e homol
  remoto (I13). Use sempre que o usuário mencionar subir ambiente local,
  Docker, criar ou depurar spec Playwright, rodar `npm run test:e2e` /
  `test:local` / `test:homol`, montar a matriz L01–LN / U01–UN de evidências,
  ou perguntar qual URL/porta/BD usar em cada etapa de teste. Homol é
  **externo** (sem Docker, acesso só por URL). URLs, portas e BD ficam sempre
  no perfil `arquitetura/ambiente-local-{projeto}.md` — nunca copiar de outro
  projeto.
---

# Ambiente local e testes Playwright — Solides

> **Docker só existe no ambiente local.** Homol é **externo** (acesso por URL + usuário/senha, sem subir ambiente).
> **URLs, portas, BD e comandos** são específicos de cada projeto → ver o perfil `arquitetura/ambiente-local-{projeto}.md` do projeto atual.

## Subir ambiente local (Docker)

Comando e porta variam por projeto — ver o perfil `arquitetura/ambiente-local-{projeto}.md` (§ Gate L0). Antes de commit/PR: restaurar patches locais conforme o mesmo perfil.

## Três projects Playwright

Cada projeto Solides com suíte Playwright define os mesmos três `projects` em `testes/playwright.config.ts` (no cit: `testes/E2E/specs/`, `testes/local/specs/`, `testes/homol/specs/`):

| Project | Etapa | Alvo | Comando |
|---------|-------|------|---------|
| `e2e` | I7 | URL **local** do projeto (validator/AC) | `npm run test:e2e` |
| `local` | I10 | URL **local** do projeto (matriz L01–LN) | `npm run test:local` |
| `homol` | I13 | URL **homol remota** do projeto (matriz U01–UN, só após I12) | `npm run test:homol` |

```bash
cd testes
npm install
npx playwright install --with-deps chromium

npm run test:e2e     # I7
# I10 — URL local L0 (URL do perfil arquitetura/ambiente-local-{projeto}.md)
PLAYWRIGHT_BASE_URL={url-local-do-perfil} npm run test:local
# I13 — somente após I12 OK deploy homol (URL homol do perfil)
PLAYWRIGHT_BASE_URL={url-homol-do-perfil} npm run test:homol
```

**Nunca** apontar `PLAYWRIGHT_BASE_URL` para localhost na etapa **I13**.

## Critérios de saída

- **I7:** 100% pass `e2e` → I8 → I9
- **I10:** 100% pass `local` → I11 — ver regras da matriz abaixo
- **I13:** 100% pass `homol` → I14 → restaurar patches locais conforme o perfil `arquitetura/ambiente-local-{projeto}.md` — **mesmas regras** que I10 (prefixo **U**)

## Regras da matriz URL (I10 / I13)

Aplicam-se a **qualquer card** — detalhes no plano § Testes local/homol:

| Regra | O quê |
|-------|--------|
| **Escopo** | Matriz L/U **somente** rotas/views/assets **alterados pela demanda** |
| **Login** | Via `auth.setup` — **não** é cenário L/U com tela vazia |
| **Preenchimento** | Cadastro/filtro/edição/exibição: print **após** aplicar **dados de teste do plano/AC** |
| **HTTP** | **200** na rota principal e em assets — 401/403/404/500 = **falha** |
| **Pass** | **100%** na suíte — zero skip |
| **Cadastro/edição** | **2 prints + GET + POST** — sem toasts de erro |
| **Filtro** | 1 print + GET — **sem submit** que dispare alerta |

**Proibido:** login vazio como evidência; rota genérica não alterada pelo card; `status < 500` como critério de pass.

## Estrutura de spec

```
testes/E2E/specs/{card-id}/
testes/local/specs/{card-id}/     # prefixo L, mesma matriz que homol
testes/homol/specs/{card-id}/     # prefixo U
```

## Dois HTML de evidências

| Arquivo | Etapas | Conteúdo |
|---------|--------|----------|
| `evidencias.html` | S3, I9, I11 | Diagnóstico + impl + **E2E (print+tabela)** + **local L01–LN** |
| `evidenciashomol.html` | I14, I15 | **E2E (print+tabela)** + **homol U01–UN** |

## Ordem no fluxo

1. **I10** — `npm run test:local` (matriz na URL local)
2. **I11** — bloco local em `evidencias.html` + validação E2E + subagente `validador-tecnico`
3. **I12** — pedir OK do usuário para deploy homol
4. **I13** — `npm run test:homol` (somente após I12)

## Referência

- [testes-e2e.md](../../implementacao/testes-e2e.md) — I7/I8
- [testes-local.md](../../implementacao/testes-local.md) — I10/I11
- [testes-homol.md](../../implementacao/testes-homol.md) — I13/I14
- o perfil `arquitetura/ambiente-local-{projeto}.md`
