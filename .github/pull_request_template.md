## Card ADO

- **Card ADO URL:** https://dev.azure.com/ORG/PROJECT/_workitems/edit/000000
- **Título do card:** (título curto do work item)

## PR

- **Branch:** deve seguir `<card>_<descricao>` (ex.: `167697_corrigir-hook`) ou `feat/bcge-12-...` para demandas do Brain-Cursor.
- **Base:** `staging` (não abrir PR para `main` diretamente).
- **Após o merge:** a branch deste PR será **removida** automaticamente (política do repo; permanecem só `main` e `staging`).

## Checklist

- [ ] Lint + testes locais: `bash scripts/ci-lint.sh && bash scripts/ci-test.sh`
- [ ] Sem secrets ou credenciais no diff
- [ ] Regra Brain: **nunca** merge de `staging` na branch de trabalho do card

## Notas para o revisor

(Opcional) contexto extra para aprovação.