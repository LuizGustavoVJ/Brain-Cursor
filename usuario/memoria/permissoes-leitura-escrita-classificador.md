---
name: permissoes-leitura-escrita-classificador
description: Leitura é livre em todo o projeto (inclusive .env/credencial); escrita/execução com efeito externo sempre pede OK no chat antes; deny não protege por si — conferir a tool viva; bloqueio do classificador em ação já autorizada resolve-se pedindo para liberar por settings.local.json
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:03:37.684Z
---

Consolida `leitura-liberada-tudo-no-projeto`, `pedir-permissao-antes-de-escrita-externa`,
`deny-conferir-contra-tool-real` e `pedir-liberacao-quando-classificador-bloqueia` (destilação de
25/09/2026).

**Leitura: sem pedir, sempre.** Autorização permanente do usuário (21/09/2026): qualquer arquivo do
projeto e do ambiente, inclusive `.env` e credencial. Imprimir o segredo lido continua proibido
(nunca vai para chat, doc, commit ou prompt de subagente).

**Escrita/execução com efeito em sistema de terceiro (MCP, API externa, painel de fornecedor, git,
ADO, UPDATE em homol): sempre para no chat e pede OK explícito antes**, dizendo o que muda, onde e
como reverter — mesmo em sandbox. Decidido ao configurar o MCP do HubSpot (27/08/2026): **não
bloquear tool de escrita por `deny`** — o usuário prefere decidir caso a caso a perder capacidade
por uma trava cega.

**`deny` só protege se o nome da tool for o real e vivo na sessão** — nome morto no `deny` não dá
erro, simplesmente não bloqueia nada (achado real: a proibição de postar no ADO tinha 2 nomes
mortos no `deny` e a tool que de fato escreve estava livre). Ao revisar `allow`/`deny` de tool MCP,
comparar com a lista viva da sessão, nunca com o que está escrito no arquivo — confirmação empírica
é a tool desaparecer da lista disponível depois de negada.

**Quando o classificador bloqueia uma ação que o usuário JÁ autorizou** (ex.: criar card no ADO
barrado por "Credential Exploration"/"Auto-Mode Bypass"), não parar em "não consigo": perguntar se
pode liberar por regra em `.cursor/settings.local.json` e, com o OK, escrever a regra específica do
comando (regra genérica de diretório não vence o classificador) e executar — não terceirizar o
comando de volta ao usuário.

**Atualização 25/09/2026:** escrita no HubSpot (tools do MCP de projeto e do conector claude.ai) e no Grafana está em `ask` no `.cursor/settings.json` (propagado aos 14 repos), então a confirmação é da própria ferramenta. Postman fica sem `ask` de propósito, porque é etapa de todo card, no workspace do Luiz.
