# Estrutura da pasta `docs/`

Documentação de sustentação organizada por **tipo de problema** e **card**.

## Árvore de diretórios

```
docs/
├── analises/
│   ├── {tipo}/
│   │   └── {card-id}.md
│   └── collections/
├── fluxos/
│   └── {tipo}/
│       └── {card-id}.md
├── evidencias/
│   ├── html/
│   │   └── {tema-slug}/
│   │       └── {card-id}-{Titulo-Slug}/
│   │           ├── plano.html            ← I2-html — plano para o card
│   │           ├── evidencias.html       ← S3 · I9 · I11
│   │           └── evidenciashomol.html  ← I14
│   ├── assets/
│   │   ├── {tema-slug}/
│   │   │   └── {card-id}-{Titulo-Slug}/
│   │   │       ├── {card-id}-q1.png
│   │   │       └── {card-id}-qN.png
│   │   └── legado/
│   └── anexos/
│       └── {tema-slug}/
│           └── {card-id}-{Titulo-Slug}/
│               └── testes-e2e.md
└── implementacoes/
    ├── plano/
    │   └── impl-{nome}.md          ← I1/I2-val — plano (curto ou detalhado) + ## Validação do plano
    └── executada/
        └── impl-{nome}.md          ← I5–I11 — consolidação + validações I6/I11
```

## Convenções de nomenclatura

> **REGRA CRÍTICA — pasta de evidências NUNCA é só o número.**
> A pasta de evidências é sempre `{tema-slug}/{card-id}-{Titulo-Slug}` (ex.: `login-unificado-exemplo/152069-Login-Unificado-Parceiros-sistema-legado-exemplo`). Já os arquivos de `analises/` e `fluxos/` usam só `{card-id}.md` (ex.: `152069.md`). Monte o `{card-id}` (número) e o `{Titulo-Slug}` (título) **uma vez** e reutilize em todo o card.

| Elemento | Formato | Exemplo |
|----------|---------|---------|
| **`{tipo}`** | kebab-case; domínio do problema / pasta por demanda | `automacao-creditos`, `incidentes` |
| **`{card-id}`** | **número do card** (só dígitos) — usado no nome de `analises/`/`fluxos/` e como prefixo da pasta de evidências | `152069`, `146737` |
| **`{tema-slug}`** *(só evidências)* | kebab-case; tema/assunto da demanda — pasta agrupadora sob `docs/evidencias/{html\|assets\|anexos}/` | `login-unificado-exemplo` |
| **`{Titulo-Slug}`** *(só evidências)* | título do card em kebab-case capitalizado, **sem** o número — compõe a pasta como `{card-id}-{Titulo-Slug}` | `Login-Unificado-Parceiros-sistema-legado-exemplo` |
| **Análise** | `{card-id}.md` em `docs/analises/{tipo}/` | `docs/analises/{tipo}/{card-id}.md` |
| **Fluxo** | `{card-id}.md` em `docs/fluxos/{tipo}/` | mesmo nome da análise |
| **HTML do plano** *(I2-html)* | sempre `plano.html` na pasta do card | `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html` |
| **HTML de evidências** *(S3 · I9 · I11)* | sempre `evidencias.html` na pasta do card | `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html` |
| **HTML de homologação** *(I14)* | sempre `evidenciashomol.html` na pasta do card | `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidenciashomol.html` |
| **Print** | `{card-id}-qN.png` | `.../{tema-slug}/{card-id}-{Titulo-Slug}/{card-id}-q1.png` |
| **Registro de revisões (interno)** | `_processo-revisoes.md` na pasta do card — **não-entregável**, não vai ao ADO; recebe o registro do gatilho de artefato (S3-rev/I1-rev/I6-rev). O documento oficial não cita agente da frota (regras.md § 11) | `docs/analises/{tipo}/{card-id}-.../ _processo-revisoes.md` |
| **Implementação** | kebab-case, prefixo `impl-` | `impl-{nome}.md` |
| **Plano (I1/I2-val)** | `docs/implementacoes/plano/impl-*.md` | `docs/implementacoes/plano/impl-{nome}.md` |
| **Executada (I5–I11)** | `docs/implementacoes/executada/impl-*.md` (mesmo basename do plano) | `docs/implementacoes/executada/impl-{nome}.md` |
| **Testes E2E (I8)** | `testes-e2e.md` em `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/` | `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/testes-e2e.md` |

## O que vai em cada pasta

| Pasta | Conteúdo | Público |
|-------|----------|---------|
| `docs/analises/{tipo}/` | Diagnóstico, causa raiz, queries, decisão | Técnico |
| `docs/fluxos/{tipo}/` | Mapeamento do fluxo legado | Técnico |
| `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/` | **Três** HTML para Azure DevOps: `plano.html` (**I2-html** — plano antes do código) · `evidencias.html` (**S3** diagnóstico, **I9** impl + E2E, **I11** local) · `evidenciashomol.html` (**I14** homol) | Negócios |
| `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/` | Prints das queries | Referenciados no HTML |
| `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/` | JSON, logs, **`testes-e2e.md`** (I8) | Referenciados na análise / implementação |
| `docs/evidencias/.../legado/` | Materiais anteriores ao padrão | Consulta histórica |
| `docs/analises/collections/` | Postman e similares | Apoio técnico |
| `docs/implementacoes/plano/` | Plano de código (I1) — curto ou detalhado; validação I2-val | Técnico |
| `docs/implementacoes/executada/` | Consolidação pós-código (I5–I11); validações I6 e I11 | Técnico |

## Regras de organização

1. **Um card = um `{card-id}`** — análise, fluxo, HTML e imagens compartilham o mesmo identificador.
2. **`{tipo}`** — pasta por demanda/assunto (ex.: `automacao-creditos`).
3. **Não misturar cards** — subpasta própria em `html/`, `assets/` e `anexos/`.
4. **HTML** não cita caminhos internos `docs/` (é para negócios).
5. **Três HTML por card, na mesma pasta:** `plano.html` (I2-html — plano do código, gate I2-val); `evidencias.html` (S3 diagnóstico, I9 impl + E2E, I11 local L01–LN); `evidenciashomol.html` (I14 homol U01–UN) — [documento-plano-html.md](../implementacao/documento-plano-html.md), [documento-evidencias-html.md](../implementacao/documento-evidencias-html.md), [fluxo-completo.md](../fluxo-completo.md).
6. **Imagens no HTML:** `../../../assets/{tema-slug}/{card-id}-{Titulo-Slug}/{card-id}-qN.png`
7. **Legado** em `legado/` até migração; novos cards seguem o padrão acima.

## Exemplo (estrutura por card)

```
docs/
├── analises/{tipo}/{card-id}.md
├── fluxos/{tipo}/{card-id}.md
├── implementacoes/
│   ├── plano/impl-{nome}.md
│   └── executada/impl-{nome}.md
└── evidencias/
    ├── html/{tema-slug}/{card-id}-{Titulo-Slug}/
    │   ├── plano.html
    │   ├── evidencias.html
    │   └── evidenciashomol.html
    ├── assets/{tema-slug}/{card-id}-{Titulo-Slug}/
    │   └── {card-id}-q1.png
    └── anexos/{tema-slug}/{card-id}-{Titulo-Slug}/
        └── testes-e2e.md
```
