---
name: pat-do-ado-repetido-em-nove-repos
description: "PAT do Azure DevOps vive só em ~/.claude.json desde 21/08/2026; ado_update_comment.py foi corrigido em 24/08/2026 para ler de lá em vez do .mcp.json morto"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6ec74188-34b7-436e-a7b4-4b76266ba1ee
  modified: 2026-08-24T00:00:00.000Z
---

**Resolvido em 21/08/2026.** Havia **9** `.mcp.json` em `/var/www/html/*/`, cada um com o mesmo
`AZURE_DEVOPS_EXT_PAT` + `ADO_MCP_AUTH_TOKEN` em texto plano. Hoje `find /var/www/html -maxdepth 2
-name .mcp.json` devolve **zero**: os arquivos foram para `~/backups-brain/mcpjson/<repo>.mcp.json`
e os servidores vivem **só no escopo de usuário** (`~/.claude.json`, raiz `mcpServers`:
`gitlab`, `azure-devops`, `playwright`). Backup do `~/.claude.json` anterior:
`~/.claude.json.bak-20260821-pat`.

**Why:** rotacionar o PAT passou de "editar 9 arquivos e rezar para não esquecer nenhum" para
editar **um**. Esquecer um quebrava o C0 só naquele repo, com erro que parecia problema do MCP.
Também deixou de existir declaração de servidor em repositório de produto.

**How to apply:** ao rotacionar o PAT, mexer apenas em `~/.claude.json`. **Não recriar `.mcp.json`
em repo nenhum** — escopo de projeto vence o de usuário e a duplicação volta calada. Se um MCP
"desaparecer" num repo, conferir primeiro se alguém recriou um `.mcp.json` lá. A remoção em lote
foi bloqueada duas vezes pelo classificador do auto mode e quem executou foi o usuário — se
precisar repetir, entregar o comando pronto em vez de tentar. Ver
[[mcp-inventario-escopos-e-alcance]] e [[fonte-unica-nunca-duplicar-tabela]].

**Sequela corrigida em 24/08/2026:** `.claude/scripts/ado_update_comment.py` ainda lia o PAT de
`<repo>/.mcp.json` por caminho fixo. Como esses arquivos não existem mais, **toda postagem de
evidência no ADO morria** com `FileNotFoundError: .../.mcp.json` — erro que parece falta de
configuração, não consequência da consolidação. O `get_pat()` agora tenta, nesta ordem: variável
de ambiente (`AZURE_DEVOPS_EXT_PAT` ou `ADO_PAT`) → `~/.claude.json` → `<repo>/.claude/.mcp.json`
→ `<repo>/.mcp.json`; e varre o JSON **pela chave**, não pelo caminho
`mcpServers.azure-devops.env`, para não quebrar de novo se o servidor for renomeado. Sem PAT em
lugar nenhum, sai mensagem dizendo o que definir e onde procurou — não mais um traceback.
Corrigido e propagado aos 13 repositórios (backup em `~/backups-brain/20260824-191554`).

**Lição que vale além deste script:** ao consolidar um segredo, **procurar quem o lê por caminho
fixo** antes de mover o arquivo. `grep -rl '\.mcp\.json' .claude/scripts/` teria pego isso em
21/08. O consumidor quebrado só aparece na primeira vez que alguém usa — aqui, três dias depois.
