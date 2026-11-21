---
name: postman-workspace-sempre-o-do-luiz
description: "No Postman, trabalhar SEMPRE no workspace 'Luiz Gustavo Finotello's Workspace'; NUNCA no Default — o Default não é usado"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1d174958-0e6f-4587-9207-ab6de3756d17
  modified: 2026-09-17T15:48:26.215Z
---

No Postman do Luiz, **todo trabalho (collection, environment, upload, dedup, leitura) acontece no workspace `Luiz Gustavo Finotello's Workspace`**. O **Default workspace NÃO é usado** — ignorar por completo.

**Como agir:**
- **Na IDE, Postman é TUDO via MCP (`mcp__postman__*`)** — decisão do Luiz (17/09/2026). API REST (`api.getpostman.com`) é **fallback explícito**, só quando o MCP não cobre (ex.: upload de segredos em massa mantendo os valores fora do meu contexto, via script). Preferir sempre a tool MCP; delegar ao agente **especialista-postman** e à skill de operação do Postman.
- Ao listar/criar/atualizar/apagar, **sempre escopar pelo workspace do Luiz** (o workspace correspondente no MCP; na API `?workspace=<id do Luiz>`). Uma listagem **sem** workspace mistura Default + dele e engana.
- **Nunca** mexer no Default (nem apagar duplicata que esteja lá) — não é nosso.

**IDs concretos (confirmados 17/09/2026 via MCP):** workspace do Luiz = `3a4b3f3e-329c-49a5-87d8-8ab2257880cb` (team). Default (NÃO usar) = `15570912-f747-416f-876b-eae4e3e54640`. User id 53116224, username lgfinotellosld, teamId 14194311. O MCP do Postman **não expõe tool de Globals** — só environments/collections/workspaces/specs/mocks.

**NÃO usar Globals — decisão do Luiz (17/09/2026):** o MCP não expõe tool de Globals, e o endpoint REST `PUT/GET /workspaces/{id}/global-variables` (campo é `values`, não `variables`) é **inconfiável**: o app do Postman chegou a mostrar as vars preenchidas, mas a API pública lia 0 de processos independentes — read/write dessincronizados. O Luiz mandou apagar os Globals e ficar só com o environment. Globals **limpos** via API (PUT `values:[]`). Casa oficial das constantes = **environment `env` (uid `53116224-f4945c8f-c863-4915-8636-0d745a005f8c`, 258 values)** no workspace do Luiz — persiste e confere de processo independente.

**Upload de segredos em massa (`.env` → Postman):** roda por **script** que lê o arquivo e envia direto (valores NUNCA entram no meu contexto; stdout só conta contagens, nunca chaves/valores). O classificador do harness barra ler `.env` para subir à nuvem como "Data Exfiltration" e **só libera após OK explícito do Luiz**. A chave PMAK fica no `~/.cursor/mcp.json` (`mcpServers.postman.env.POSTMAN_API_KEY`) — script lê de lá, não imprime. Antes de sobrescrever/limpar recurso externo: GET + backup em `~/backups-brain/`.

**Contexto (17/09/2026):** o environment `env` que eu apaguei estava no **Default**; por isso "sumiu" da conta mas o Luiz diz que o Workspace dele está vazio. Confundi as duas listagens. As 2 duplicatas `Homol — Cancelamento SENSE` que vi numa listagem crua provavelmente estão no Default → **não tocar**.

**Why:** operar no workspace errado apaga/duplica coisa fora do lugar e dá a falsa impressão de estado. O Luiz foi explícito: sempre o dele, nunca o Default.

**How to apply:** ver [[nunca-apagar-recurso-externo-sem-backup]] e [[postman-chave-privada-do-luiz]]. Antes de qualquer operação, resolver o id do workspace do Luiz e escopar tudo por ele.
