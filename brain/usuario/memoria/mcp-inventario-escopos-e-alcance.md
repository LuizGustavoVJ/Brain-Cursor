---
name: mcp-inventario-escopos-e-alcance
description: Os MCPs vivem em dois escopos (.mcp.json do projeto e ~/.claude.json do usuário); servidor de pé não basta — a tool tem de estar declarada no frontmatter do agente
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6ec74188-34b7-436e-a7b4-4b76266ba1ee
  modified: 2026-08-21T00:00:00.000Z
---

Inventário conferido em 21/08/2026 (`.claude/scripts/mcp.sh checar`); revisto em 27/08/2026:
**4 servidores, todos no escopo de usuário** — o `.mcp.json` do repo `cit` está **vazio**.

| Servidor | Escopo | Estado |
|---|---|---|
| `azure-devops` | usuário (`~/.claude.json`) | ok — leitura de card em C0 |
| `playwright` | usuário | ok — captura em I7/I10/I13/I14 |
| `gitlab` | usuário | ok, `GITLAB_READ_ONLY_MODE=true`, `gitlab.solides.com.br` |
| `hubspot` | usuário | ok desde 27/08/2026 — sandbox, ver [[mcp-hubspot-sandbox-configurado]] |

**Zendesk: descontinuado em 21/08/2026** por decisão do usuário ("não vai subir, não vamos usar
mais"). Removido de `~/.claude.json` (backup em `~/.claude.json.bak-20260821-zendesk`) e as 19
entradas saíram do `settings.json`. Consequência a assumir: ticket de cliente entra no card por
copiar e colar. Sobrou a declaração em `partners/.mcp.json` — outro repo, precisa de permissão.

Três coisas que não são óbvias:

- **Escopo de usuário existe e é invisível no repo.** `gitlab` não está em nenhum `.mcp.json`;
  quem procurar só ali conclui que há 2 MCPs. Declarado nos dois escopos, o de projeto vence e o
  outro fica morto.
- **Tool não declarada no frontmatter não chega ao subagente.** O servidor pode estar de pé e o
  agente só ter `Bash`. Era o caso do MCP GitLab: `/cicd` prometia ler o log do job real e
  nenhum agente da frota declarava tool dele.
- **Nome de tool muda e a permissão morre calada.** `mcp__azure-devops__wit_get_work_item` não
  existe mais (hoje é `wit_work_item`); o `allow` apontava para o nome velho e o C0 pedia prompt
  a cada leitura de card. **Aconteceu de novo no `deny`, e pior:** em 21/08/2026 a revisão do
  Brain achou que a regra "o agente NUNCA posta no ADO" estava sustentada por
  `wit_work_item_comment_write` e `wit_work_item_attachment` — **nenhuma das duas existe** no
  servidor. Quem existe e escreve no card é `wit_work_item_write`, e ela não estava negada.
  Corrigido: `deny` foi de 4 para **17** regras, cobrindo as 13 tools de escrita reais
  (`wit_work_item_write`, `wit_work_item_link_write`, `wiki_upsert_page`, `testplan_*_write`,
  `pipelines_write`, `pipelines_run`, `repo_pull_request*_write`, `repo_create_branch`,
  `work_*_write`). Os dois nomes mortos ficaram, para cobrir versão antiga do servidor.

**Why:** MCP quebrado é pior que MCP ausente — ele injeta o nome das tools na sessão, o agente
confia que existe e descobre o contrário no meio da etapa.

**How to apply:** antes de contar com MCP numa etapa, rodar `.claude/scripts/mcp.sh` (inventário,
saúde e quem da frota alcança cada servidor). Ver [[fonte-unica-nunca-duplicar-tabela]] e
[[verificar-antes-de-deduzir]].

Quarto ponto, aprendido em 27/08/2026: **servidor recém-adicionado não vale na sessão em
curso** — as tools só entram no reinício do Claude Code. Para conferir o que ele expõe sem
reiniciar, subir o binário na mão por stdio e mandar `initialize` + `tools/list`.
