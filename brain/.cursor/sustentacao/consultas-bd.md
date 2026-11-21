# Consultas ao banco (análise colaborativa)

O agente **nunca executa** consultas em **produção** — **monta**, o **usuário executa**.

Em **local** e **homologação** é o contrário: **o agente executa** — `SELECT`, DDL de migration e DML — sem pedir ao usuário.

| Papel | Responsabilidade |
|-------|------------------|
| **Agente** | Monta **todas** as queries que a solução exigir — `SELECT` de diagnóstico **e** DML de correção (`UPDATE`/`INSERT`/`DELETE`) — valida sintaxe/schema localmente, interpreta resultados, atualiza análise/HTML |
| **Usuário** | Executa em **produção** (inclusive a correção) a partir do **documento de evidência** e devolve resultados (texto, print ou imagem) |

## Queries de correção (DML) — sempre no documento de evidência

Quando a solução exigir alteração de dados (`UPDATE`, `INSERT`, `DELETE`), o agente **monta a query no documento de evidência** (`evidencias.html`) e na análise:

- Envolver em **`START TRANSACTION`** + **conferência** (`SELECT`) + **`COMMIT`/`ROLLBACK`** ao final.
- Filtros específicos (chave/PK) para afetar **apenas** as linhas alvo.
- **Validar a sintaxe no ambiente local** (BD homol espelhado) com `ROLLBACK`, sem persistir.
- Deixar explícito que **execução e `COMMIT` em produção são decisão do usuário** (DBA/negócio).
- O agente **não executa** a correção em produção em nenhuma hipótese.

## Gate: nenhuma query sai sem o `especialista-sql`

**Toda** consulta que vá ser entregue ao usuário ou executada — `SELECT` de diagnóstico, DML de
correção, DDL — passa pelo [`especialista-sql`](../agents/especialista-sql.md) **antes** de entrar
no documento ou no chat. É gatilho por artefato, não sugestão: `.claude/frota/gatilhos.tsv`.

Ele confere o que a pressa do fluxo não confere:

- a consulta responde **exatamente** a pergunta feita (`COUNT(*)` × `COUNT(DISTINCT)`);
- `JOIN` que multiplica linha, `LEFT JOIN` que virou `INNER` pelo `WHERE`, `NULL` em `NOT IN`;
- **compatibilidade com o cliente do usuário**: `SET @var :=` como primeiro statement quebra com
  **erro 1064** em cliente sem `CLIENT_MULTI_STATEMENTS` (DBeaver, por exemplo). Variável de
  sessão em consulta para o usuário rodar → reescrever com subquery/CTE;
- `UPDATE`/`DELETE` validados antes como `SELECT` com o **mesmo** `WHERE`.

Registro, uma linha na análise: `especialista-sql · OK|Ajustar|Bloqueante · ponto · onde foi
acatado`. Sem essa linha, o `validador-tecnico` recusa a etapa.

## Regras para montagem das queries

- **Proibido inventar** banco, tabela, coluna ou tipo de campo
- Validar no **BD local** antes de cada query — ver o perfil `arquitetura/ambiente-local-{projeto}.md`
- Schema via `SHOW TABLES`, `DESCRIBE`, `INFORMATION_SCHEMA` ou explorador da IDE
- Cruzar com **código** (models, migrations, queries existentes)
- Entregar queries numeradas, uma a uma ou em lotes pequenos, com objetivo claro
- `SELECT` de diagnóstico **e** DML de correção (`UPDATE`/`INSERT`/`DELETE`) quando a solução exigir — sempre montadas no documento de evidência e **nunca executadas em produção** pelo agente (ver [Queries de correção (DML)](#queries-de-correção-dml--sempre-no-documento-de-evidência)); em local e homol o agente executa normalmente

## Formato de entrega (no chat)

```markdown
### Query N — [objetivo]
**Banco:** {BD do projeto — ver perfil `arquitetura/ambiente-local-{projeto}.md`}
**Tabelas:** tabela_a, tabela_b
```sql
SELECT ...
```
```

## Ciclo de evidências

1. Agente envia query(s) validadas no schema local
2. Usuário executa em produção e devolve resultado
3. Agente registra no `.md` e atualiza `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html`
4. Prints em `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/{card-id}-qN.png`
5. Repetir até **100%** da análise; só então submeter à validação

## HTML incremental

- Pode iniciar cedo e expandir a cada resultado
- Cada evidência de BD: número da query, objetivo, SQL, resultado (imagem ou tabela), conclusão parcial
- Ao final, consolidar conclusão geral
