---
name: mysql-solides
description: >-
  Monta e valida queries MySQL para QUALQUER projeto da stack Solides (partners,
  checkout, adapters Laravel, etc.) — é
  conhecimento de stack genérico (host/porta/banco variam por perfil). Use ao
  investigar schema, dados de produção, models Active Record, montar SELECT,
  EXPLAIN, JOIN ou validar colunas antes de alterar código, em qualquer
  repositório aberto na IDE.
---

# MySQL — Solides

> **Host, porta e nomes de BD** são específicos de cada projeto → ver o perfil `arquitetura/ambiente-local-{projeto}.md` do projeto atual.

## Documentação oficial

| Tema | URL |
|------|-----|
| MySQL 8.0 Reference | https://dev.mysql.com/doc/refman/8.0/en/ |
| SELECT / JOIN | https://dev.mysql.com/doc/refman/8.0/en/select.html |
| EXPLAIN | https://dev.mysql.com/doc/refman/8.0/en/explain.html |

## Ambientes

O MySQL central local fica em `127.0.0.1:3309` (comum a todos os projetos Solides). Os **nomes de BD** (schema do agente e BD do app local) variam por projeto → ver o perfil `arquitetura/ambiente-local-{projeto}.md`.

| Uso | Host | Porta | Banco |
|-----|------|-------|-------|
| Schema local (agente) | `127.0.0.1` | `3309` | BD do perfil |
| App local (I7 / I10) | `127.0.0.1` | `3309` | BD do perfil (cópia da massa **de homol**, não prod) |
| Homol remoto (I13) | servidor homol | — | BD do deploy (≠ local) |
| **Produção** | — | — | **Usuário executa** |

```bash
# nome do BD: ver o perfil arquitetura/ambiente-local-{projeto}.md
mysql -h 127.0.0.1 -P 3309 -u root {bd-do-perfil} -e "SHOW TABLES LIMIT 5;"
```

## Fluxo colaborativo (produção)

1. Agente monta query **read-only** (SELECT) com comentário de objetivo
2. Usuário executa e cola resultado
3. Agente interpreta — **nunca** assumir dados de produção sem evidência

Guia: [consultas-bd.md](../../sustentacao/consultas-bd.md)

## Convenções do projeto

- Models CI2: `$this->db->get('tabela')`, `$this->db->where()`
- Conexões adicionais do projeto (ex.: `DB_CRM_*`, `DB_CIT_*`, `DB_GESTAO_*`) — ver `database.php` do repositório atual
- Validar tipo/tamanho de coluna no schema local antes de alterar validação/populate

## Boas práticas

- Queries com `LIMIT` em exploração
- Documentar card-id e hipótese no comentário SQL
- Não incluir credenciais ou dumps completos no chat
