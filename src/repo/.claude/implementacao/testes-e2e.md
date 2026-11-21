# Testes E2E — implementação

Guia da **etapa I7** do [fluxo-implementacao.md](fluxo-implementacao.md).

**Testes local (URL)** — matriz na URL L0 — são fase separada, etapa **I10**: [testes-local.md](testes-local.md).
**Testes homol remoto** — etapa **I13**: [testes-homol.md](testes-homol.md).

> **Como executar (obrigatório):** `.claude/scripts/resumo_testes.sh e2e` — o stdout completo do Playwright **não entra no contexto**. Registrar apenas `N/N`, tempo e falhas. Ver [testes-resumido.md](testes-resumido.md).

---

## Quando executar

**Somente após I6 aprovada** (subagente validou o código contra o plano).

---

## Escopo desta etapa (I7)

Apenas o project **`e2e`** — testes de validator / AC em browser **sem** depender do homol Docker:

```bash
cd testes
npm run test:e2e
```

A pasta `testes/homol/` **não** entra na I7 — executar na **I13**, após I12.

---

## Ferramenta e estrutura

**Playwright** — pasta **`testes/`** na raiz:

```
testes/
├── E2E/specs/{card-id}/*.spec.ts   ← I7
└── homol/                          ← I13 (não executar aqui)
```

Instalação (primeira vez):

```bash
cd testes
npm install
npx playwright install --with-deps chromium
```

---

## Execução (I7)

```bash
cd testes
npm run test:e2e
```

Salvar stdout para o documento I8.

**Critério de saída:** **100% pass** no project `e2e`.

Se falhar: corrigir código → **revalidar I6** se mudança substancial → reexecutar I7.

---

## Evidência visual E2E (obrigatória na I9)

Após **100% pass**, gerar o print do relatório Playwright para o HTML de evidências:

| Item | Valor |
|------|--------|
| Relatório | `testes/playwright-report/index.html` |
| PNG destino | `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/{card-id}-e2e-playwright.png` |
| HTML | `figure.evidence` + `h3` “1. Relatório Playwright — execução completa” + tabela “Detalhamento dos cenários” |

Padrão completo: [documento-evidencias-html.md](documento-evidencias-html.md#padrão-e2e-obrigatório-todos-os-cards-todos-os-repositórios). Referência: `evidencias.html` de um card já validado.

**Proibido** avançar para I10 sem print + tabela detalhada no `evidencias.html`.

---

## Próximas etapas (ordem)

| Etapa | Ação |
|-------|------|
| **I8** | `testes-e2e.md` com resultado E2E |
| **I9** | `evidencias.html` — impl + E2E (print + tabela) — ver [documento-evidencias-html.md](documento-evidencias-html.md) |
| **I10** | Testes local URL — ver [testes-local.md](testes-local.md) |
| **I11** | Subagente valida HTML local + E2E → gate homol I12 |

---

## Registro no plano

Secção **`## Testes E2E`** — specs em `testes/E2E/`, AC cobertos, comando `npm run test:e2e`.

Secção **`## Testes homol (URL)`** — matriz de rotas, comando `npm run test:homol` (execução na I13).
