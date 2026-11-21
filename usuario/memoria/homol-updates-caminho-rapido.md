---
name: homol-updates-caminho-rapido
description: "Sintaxe rápida do homol.sh para SELECT/UPDATE em homol sem reinvestigar: conexões crm/db, ordem SET/WHERE, o que NÃO dá (delete/insert/ddl)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1d174958-0e6f-4587-9207-ab6de3756d17
  modified: 2026-09-25T18:06:05.521Z
---

Quando o usuário pedir update/consulta em homol, **ir direto** — não reabrir script nem re-derivar
sintaxe (isso o irritou em 28/08/2026: "quando pedir tem que ser rápido"). Receitas específicas do
fluxo de cancelamento (fixture, reversão via webhook, simulação de efetivação) vivem em
`dominio-cancelamento-assinatura` § "Como testar em homol" — aqui só a sintaxe genérica da
ferramenta, reaproveitável em qualquer domínio.

**Comando único (SQL em homol):**
```bash
bash .cursor/scripts/homol.sh <select|update> <crm|db> <TABELA> "<SET ou campos>" [<WHERE col=val> ...]
```
- **1º positional depois da TABELA = SET** (no update) ou **lista de campos** (no select). **Todos
  os args seguintes = WHERE**, só igualdade, unidos por AND. Ex. real que funciona:
  `homol.sh update db forms_cancelamento status=concluido cnpj_cpf=26085605000116 status=aberto`
  → `SET status='concluido' WHERE cnpj_cpf='26085605000116' AND status='aberto'`.
- **Conexões:** `crm` = banco do CRM (`CCLIFOR`, `ASSINATURAS`, `ASSINATURAS_HIST_ALTERACOES`);
  `db` = banco do CIT (`forms_cancelamento`, `etapas_fluxos_servicos`).
- **Só faz SELECT e UPDATE.** Nada de DELETE/INSERT/DDL — isso é o usuário no DBeaver. Detalhe do
  endpoint em `ambiente-cit-infra`.
- **CNPJ no CRM (`CCLIFOR`) está só com dígitos** em homol → igualdade `CNPJ=<dígitos>` casa direto.
