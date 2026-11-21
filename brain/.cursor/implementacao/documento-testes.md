# Documento de evidências — testes (E2E + local + homol)

**Pasta:** `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/`

| Arquivo | Etapa | Conteúdo |
|---------|-------|----------|
| `testes-e2e.md` | I8 | Bloco E2E (após I7 100% pass) |
| `testes-local.md` | I11 | Bloco local URL (após I10 100% pass) |

Resumo homol fica referenciado em `testes-e2e.md` ou anexo dedicado conforme o card; evidências visuais homol estão em `evidenciashomol.html` (I14).

Guias: [testes-e2e.md](testes-e2e.md) (I7), [testes-local.md](testes-local.md) (I10–I11), [testes-homol.md](testes-homol.md) (I13–I14).

---

## Conteúdo mínimo (I8 — bloco E2E)

```markdown
# Testes — {card-id}

## Resumo E2E (I7/I8)

- **Data:** YYYY-MM-DD
- **Ferramenta:** Playwright (project `e2e`)
- **Commit:** `{hash}`
- **Resultado:** N/N testes passaram (100%)

## Critérios de aceite — E2E

| AC | Spec | Resultado |
|----|------|-----------|
| AC1 | `testes/E2E/specs/{card-id}/....spec.ts` | Pass |

## Comando E2E

\`\`\`bash
cd testes && npm run test:e2e
\`\`\`

## Saída resumida

(colar trecho final do runner)
```

---

## Conteúdo mínimo (I11 — `testes-local.md`)

Arquivo separado ou secção no mesmo diretório:

```markdown
# Testes local — {card-id}

## Resumo local URL (I10/I11)

- **Data:** YYYY-MM-DD
- **Base URL:** {URL local do perfil arquitetura/ambiente-local-{projeto}.md}
- **Resultado:** N/N cenários pass (100%)

## Comando local

\`\`\`bash
cd testes && npm run test:local
\`\`\`

## Matriz (resumo)

| Cenário | Rota | Resultado |
|---------|------|-----------|
| L01 | … | Pass |
```

---

## Regras

1. **I8:** só registrar E2E após **100% pass** na I7.
2. **I11:** só registrar local após **100% pass** na I10.
3. Prefixo **L** para cenários local; **U** para homol (documentado em I14).
4. Não incluir credenciais reais.
5. Referenciar plano em `docs/implementacoes/plano/` e executada em `docs/implementacoes/executada/`.
