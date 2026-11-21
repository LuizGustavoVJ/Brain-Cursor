---
name: ado-postagem-script-guid-projeto
description: "Desde 25/09/2026 o agente PODE postar no ADO mas PERGUNTA antes a cada postagem (posto eu ou entrego o comando?); ado_update_comment.py EXIGE env ADO_PROJECT=GUID e tag <body> sem atributos"
metadata:
  node_type: memory
  type: reference
  originSessionId: 27edcec9-52e3-4d2c-b8d0-65624510d7a1
  modified: 2026-09-15T23:30:34.065Z
---

**25/09/2026 — política alterada pelo usuário:** o agente **pode** postar comentário/evidência no ADO (script abaixo ou tool MCP de comentário), mas **sempre pergunta antes, a cada postagem**: "Posto eu o <arquivo> no card <n>, ou te entrego o comando?". Só posta com sim explícito; a autorização vale para aquela postagem. Só o contexto principal posta — subagente nunca. `.cursor/settings.json` tem o script e `wit_work_item_comment_write` em `ask` (não mais em `deny`); alterar estado/campos/links do card, PR, pipeline e wiki continuam em `deny`.

**Why:** o usuário quer poder delegar a postagem, mas manter o controle de cada escrita externa (ver [[pedir-permissao-antes-de-escrita-externa]]).
**How to apply:** ao fechar Pós-S6a/Pós-I2-val/Pós-I11/Pós-I15, perguntar a opção; se ele preferir o comando, entregar caminho + GUID + comando pronto como abaixo.

~~05/08/2026 — agente não posta em nenhum projeto~~ (substituído em 25/09).

Comando (executado pelo agente após o sim, ou entregue ao usuário):

```
ADO_PROJECT=3acd1fd1-e624-4002-bdbd-532f45aeb902 \
  python3 .cursor/scripts/ado_update_comment.py <html_path> <work_item_id> [comment_id]
```

**Verificado em 16/07/2026 (card 156306, comentário 13549587) — o código atual do script diverge da versão "endurecida" antes anotada:**

1. **`ADO_PROJECT` é OBRIGATÓRIO — SEMPRE, sem exceção "só-texto".** O endpoint de comentários é `https://dev.azure.com/{org}/{PROJECT}/_apis/wit/workItems/{id}/comments` e **só existe com o projeto no path**; sem ele o ADO devolve **HTTP 404** ("controller ... not found"). Passar sempre o **GUID** na MESMA linha antes do `python3`: `ADO_PROJECT=<guid> python3 .cursor/scripts/ado_update_comment.py <html> <wid> [comment_id]`. GUIDs conhecidos: `3acd1fd1-e624-4002-bdbd-532f45aeb902` (TI CORP - Sustentação, org `solidestech`); `9ab3afca-3b1a-4a80-bc36-b0e3625d3a69` (projeto da feature 161899 cartão). Não usar o nome com espaços. **15/09/2026 — incidente recorrente**: comando rodado sem `ADO_PROJECT` exportado no shell → 404. Corrigido de vez: o script agora **exige** a env e sai com `exit(2)` e mensagem clara ("ADO_PROJECT é obrigatório") se faltar, em vez de montar URL org-level silenciosa. O caso "só-texto sem projeto" foi APAGADO do docstring — não existe. AGENTS.md:191 e a skill azure-devops-cards já estavam corretos; só o docstring do script estava errado (agora consertado).
2. **A tag `<body>` precisa ficar SEM atributos.** O regex é `<body>(.*?)</body>` **literal** — `<body style="...">` (padrão canônico) NÃO casa e o script quebra (AttributeError). Solução: gerar uma cópia p/ postagem trocando `<body[^>]*>` por `<body>` (o `style` do body é irrelevante — o script embrulha o conteúdo num `<div>` próprio). Preservar o arquivo canônico do repo com o body estilizado.
3. ~~`<img>` são REMOVIDOS do comentário~~ — **desatualizado.** Reconferido em 05/08/2026: o script tem `_processa_imagens` (linhas 147–182) que sobe cada PNG como anexo, vincula ao work item e **embute** a `<img>` com `src` contendo o GUID do projeto. Flags: `ADO_ATTACH=0` não anexa; `ADO_EMBED=0` anexa sem embutir.
4. Sem `comment_id` → POST (cria, imprime id). Com `comment_id` → PATCH (atualiza, incrementa version).
5. **Cosmético:** o sanitizador do ADO trunca `font-family` dos `pre.sql` (`font-family:Consolas,;`). SQL permanece íntegro/monoespaçado.

Fluxo que funcionou: montar cópia com body limpo no scratchpad → `ADO_PROJECT=GUID python3 ... <copia> <wid> [comment_id]`.

Card 156057: comentário id 13542596. Card 156306: comentário id 13549587. Relacionado: [[padrao-html-evidencias]], [[nomenclatura-docs-card-id]], [[ambiente-cit-porta-banco-divergentes]].
