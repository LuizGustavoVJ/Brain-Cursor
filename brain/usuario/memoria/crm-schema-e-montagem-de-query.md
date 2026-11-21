---
name: crm-schema-e-montagem-de-query
description: "como montar query no banco do CRM: conexão sem schema padrão (DATABASE()=NULL) → sempre USE ou schema.TABELA; nomes aless608_sg (prod) e aless608_sg_homol (local/homol)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1d174958-0e6f-4587-9207-ab6de3756d17
  modified: 2026-09-28T14:02:50.609Z
---

O banco do **CRM** (onde vivem `ASSINATURAS`, `CCLIFOR`, `ASSINATURAS_HIST_ALTERACOES`, `CMOVIMENTOS`, `BPRODUTOS`) é acessado por uma conexão que **não tem schema padrão selecionado** — `SELECT DATABASE()` retorna `[NULL]`. Consequência prática, comprovada em 28/09/2026 no card 166398:

- Query sem qualificar a tabela ou filtro `TABLE_SCHEMA = DATABASE()` **volta vazia / falha silenciosamente** (zero linhas), não porque o dado não existe, mas porque `DATABASE()` é NULL.
- **Sempre** fazer uma das duas coisas ao montar query pro CRM:
  1. `USE \`aless608_sg\`;` no topo do script, ou
  2. qualificar a tabela: `schema.TABELA` (ex.: `SHOW COLUMNS FROM aless608_sg.ASSINATURAS_HIST_ALTERACOES;`).
- Em `INFORMATION_SCHEMA`, filtrar por **`TABLE_SCHEMA = 'aless608_sg'` literal**, nunca `= DATABASE()`.

**Nomes dos schemas do CRM (base SG):**
- Produção: `aless608_sg`
- Local / homol: `aless608_sg_homol`
- (Confirmar sempre com `SHOW DATABASES LIKE 'aless608%';` — nome pode variar por ambiente.)

Esse banco do CRM é **distinto** do banco do CIT (onde fica `forms_cancelamento`). Toda migration/consulta do histórico de cancelamento (`ASSINATURAS_HIST_ALTERACOES`) roda no CRM, não no CIT. Ver [[ambiente-cit-infra]] e [[homol-updates-caminho-rapido]].
