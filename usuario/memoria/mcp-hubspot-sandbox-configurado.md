---
name: mcp-hubspot-sandbox-configurado
description: MCP do HubSpot ligado no escopo de usuário contra o portal SANDBOX 23737834, com token de private app que também escreve — 21 tools, 7 delas de modificação
metadata:
  type: reference
---

Configurado em 27/08/2026 (`cursor mcp add hubspot -s user … npx -y @hubspot/mcp-server`,
versão 0.4.0). O registro vive em `~/.cursor/mcp.json` → `mcpServers.hubspot`, com o token em
`env.PRIVATE_APP_ACCESS_TOKEN`. **Não está no `.mcp.json` do repo** — que segue vazio e é
versionado; segredo do HubSpot ali já causou incidente em outro serviço
(ver [[segredo-versionado-payment-processing-service]]).

Portal conferido em `account-info/v3/details`: **portalId 23737834, `accountType: SANDBOX`**,
moeda BRL, hosting `na1`. **Não é o portal de produção do CIT**, que é `22604900`
(fixo em `application/config/constants/hubspot.php:45`). Dado de sandbox não responde pergunta
sobre cliente real.

**O token não é somente-leitura.** `oauth/v2/private-apps/get/access-token-info` devolve 25
escopos, entre eles `crm.objects.deals.write`, `crm.objects.companies.write`,
`crm.objects.contacts.write`, `crm.objects.custom.write`, `crm.objects.line_items.write`,
`crm.schemas.custom.write`, `settings.users.write`. Faltam `crm.pipelines.read` e
`crm.schemas.deals.read` nominalmente, mas `GET /crm/v3/pipelines/deals` e
`/crm/v3/properties/deals` respondem 200 — o escopo de deals cobre.

Das **21 tools** do servidor, **7 modificam dado**: `hubspot-batch-create-objects`,
`hubspot-batch-update-objects`, `hubspot-batch-create-associations`, `hubspot-create-property`,
`hubspot-update-property`, `hubspot-create-engagement`, `hubspot-update-engagement`.
Nenhuma está no `deny` **por decisão do usuário em 27/08/2026** — a trava é pedir permissão no
chat antes de qualquer escrita, ver [[pedir-permissao-antes-de-escrita-externa]].

**Why:** um MCP de CRM com escopo de escrita é a única integração da máquina que pode alterar
deal sozinha; e como o portal é sandbox, o inverso também engana — número lido ali não vale como
evidência de produção.

**How to apply:** antes de citar número do HubSpot em card, confirmar de qual portal veio.
Antes de rodar qualquer uma das 7 tools de escrita, pedir permissão no chat — nada as barra
sozinho. Ver [[pedir-permissao-antes-de-escrita-externa]], [[deny-conferir-contra-tool-real]] e
[[mcp-inventario-escopos-e-alcance]].
