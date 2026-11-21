# Testes local (URL) — implementação

Guia das etapas **I10** e **I11** do [fluxo-implementacao.md](fluxo-implementacao.md).

**Paridade com homol:** as **mesmas regras** de [testes-homol.md](testes-homol.md) aplicam-se ao local — matriz idêntica (prefixos **L** vs **U**), critérios HTTP, preenchimento e escopo de telas.

> **Como executar (obrigatório):** `.claude/scripts/resumo_testes.sh local` — o stdout completo do Playwright **não entra no contexto**. Registrar apenas `N/N`, tempo e falhas. Ver [testes-resumido.md](testes-resumido.md).

---

## Ambiente alvo

**URL local (L0)** — ambiente de desenvolvimento informado no chat na etapa L0.

| Item | Valor |
|------|--------|
| URL base | URL local do perfil `arquitetura/ambiente-local-{projeto}.md` |
| `PLAYWRIGHT_BASE_URL` | mesma URL local do perfil |

A URL homol remota é alvo **somente** de I13 — ver [testes-homol.md](testes-homol.md) e o perfil `arquitetura/ambiente-local-{projeto}.md`.

---

## Quando executar

**Somente após:**

- **I7** — testes E2E com **100% pass**
- **I8** — `testes-e2e.md` registrado
- **I9** — `evidencias.html` com bloco **E2E completo** (print Playwright + tabela “Detalhamento dos cenários”)
- App local no ar (L0)

---

## Objetivo

Validar a implementação **na URL local (L0)** nas **telas/views alteradas pela demanda** (mapear no plano § Testes local/homol).

Figuras no HTML: **L01–LN** (prefixo local — **não** usar U01–UN, reservado à homol).

---

## Regras obrigatórias da matriz (local = homol)

### 1. Escopo — somente telas alteradas pela demanda

- A matriz L01–LN deve listar **apenas** rotas/views/campos/APIs **impactados pelo card**, conforme plano § Testes local/homol.
- **Proibido** incluir cenários genéricos sem relação com a demanda (ex.: login vazio, listagens não alteradas, hubs sem touchpoint do card).
- **Login** é feito em `auth.setup.ts` / helper — **não** gera cenário L com tela de login sem dados.

### 2. Preenchimento antes do screenshot

| Tipo | Regra |
|------|--------|
| **Cadastro / filtro** | Preencher o(s) campo(s) alterados pela demanda com o **valor de teste do plano/AC** **antes** do print |
| **Edição** | Navegar até o formulário de edição, preencher o campo alterado, **depois** screenshot |
| **Exibição** | Interagir ou exibir o estado que comprova o AC (texto, seleção, dado visível) — **não** tela vazia |
| **Asset / API** | GET **200** + trecho do corpo com marker definido no plano (sem screenshot de tela vazia) |
| **Rota não alterada** | **Não incluir** na matriz |

**Proibido:** screenshot de formulário ou tela **sem o estado de teste aplicado** como evidência de aceite funcional.

### 3. HTTP — somente 200 (indmissível 403/404/500)

- Todo cenário de página: **GET HTTP 200** na rota principal.
- Todo cenário asset/API: **GET HTTP 200**.
- Respostas **401, 403, 404, 500** (ou corpo com “404”, “Fatal error”, “PHP Error”) = **teste falha** — não usar `status < 500` como critério de pass.
- **100% pass** na suíte é **obrigatório** para concluir I10 — um único cenário falho bloqueia a etapa.

### 4. Evidência por tipo de cenário

| Tipo | Evidência |
|------|-----------|
| **Cadastro** | Print GET (formulário) + JSON GET **200** + print POST (campo preenchido) + JSON POST **200** |
| **Edição** | Print GET (tela inicial) + JSON GET **200** + print POST (após submit) + JSON POST **200** (redirect 302/303 aceito se tela final 200) |
| **Filtro** | Print com campo preenchido + JSON GET **200** — **sem** submit que gere alerta de erro |
| **Asset / API** | JSON GET **200** + trecho do corpo |

**Proibido em qualquer print:** toasts/alertas de erro (ex.: “Não foi possível localizar registros”, “Oops! Encontramos algo”, toast `.toast-error`).

Sufixos: `{L\|U}{xx}-get-tela.png`, `{L\|U}{xx}-get-api.json`, `{L\|U}{xx}-post-tela.png`, `{L\|U}{xx}-post-api.json`.

Screenshots: `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/Lxx/` (homol: prefixo **U**).

---

## Ordem obrigatória (I10)

### Passo 1 — Confirmar ambiente local

Acesse a URL local do perfil `arquitetura/ambiente-local-{projeto}.md`.

Credenciais: `testes/.credentials.local` — variáveis `PLAYWRIGHT_*_EMAIL` / `PLAYWRIGHT_*_PASSWORD` conforme o perfil `arquitetura/ambiente-local-{projeto}.md`.

### Passo 2 — Executar testes local (100% pass)

```bash
cd testes
# URL local: ver o perfil arquitetura/ambiente-local-{projeto}.md
PLAYWRIGHT_BASE_URL={url-local-do-perfil} npm run test:local
```

Se falhar: corrigir código ou ambiente → **revalidar I6** se mudança substancial → repetir até **100% pass**.

### Passo 3 — I11: documentar e HTML local

1. Produzir `testes-local.md` — [documento-testes.md](documento-testes.md).
2. Atualizar `evidencias.html` — bloco **local** L01–LN (figuras embutidas).
3. Subagente valida bloco local + E2E — [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i11).

---

## Estrutura dos specs

```
testes/local/
├── helpers/
│   ├── url-evidencia-rules.ts   # HTTP 200, preenchimento, anti-404 (reutilizável)
│   └── {card-id}-url-matrix.ts  # matriz L (espelho homol U) — por card
└── specs/{card-id}/
    └── *.spec.ts               # data-driven; zero skip
```

Matriz: **mesmos cenários** da § Testes homol do plano, executados na URL local.

---

## Registro no plano

Secção **`## Testes local (URL)`** no plano com:

- Rotas **alteradas pela demanda** (não rotas genéricas)
- Comando `npm run test:local`
- Critério: **100% pass** + evidência por tipo (§4 — cadastro/edição GET+POST; filtro; asset)
- Referência cruzada à matriz homol (mesmos cenários, prefixos L vs U)

---

## Critério de saída

### I10

- [ ] App local acessível (L0)
- [ ] `npm run test:local` — **100% pass** (zero falha; zero skip)
- [ ] Cada Lxx: evidência conforme **tipo** (§4): cadastro/edição GET+POST + 2 prints; filtro 1 print + GET; asset GET 200 — **sem alertas de erro** nos prints
- [ ] Evidências em `docs/evidencias/assets/`

### I11

- [ ] `testes-local.md` registrado
- [ ] `evidencias.html` com figuras L01–LN embutidas
- [ ] Subagente **Aprovado** em `## Validação do HTML local`
- [ ] Seguir **I12** — gate deploy homol
