---
name: postman-operacao
description: >-
  Como operar o Postman do Luiz (workspace, chave, collections, environments)
  a partir da IDE. Use sempre que a tarefa envolver criar/alterar coleção,
  environment, variável ou subir segredos ao Postman — antes de chamar
  qualquer tool `mcp__postman__*` ou a API REST do Postman.
---

# Operação do Postman — Solides

> Conhecimento testado em campo (17/09/2026) na conta do Luiz. Onde a doc oficial diverge do
> teste real, **o teste manda** (ex.: Globals). Detalhe completo de cada seção fica nas
> referências oficiais linkadas abaixo — este arquivo é o roteiro operacional.

## Regra-mãe

- **Na IDE, Postman é TUDO via MCP (`mcp__postman__*`).** As tools do MCP Postman são
  **deferidas** — carregue-as com `ToolSearch` antes de chamar (ex.:
  `select:mcp__postman__getCollections,mcp__postman__createEnvironment,...`). Chamar uma tool
  MCP sem antes selecioná-la falha silenciosamente.
- **API REST (`api.getpostman.com`, header `X-Api-Key`) é fallback explícito** — só quando o
  MCP não tem a tool (ex.: upload de segredos em massa, ver seção própria abaixo).
- **Sempre** o workspace do Luiz: **`Luiz Gustavo Finotello's Workspace`**
  (`3a4b3f3e-329c-49a5-87d8-8ab2257880cb`). **NUNCA** o Default
  (`15570912-f747-416f-876b-eae4e3e54640`) — listagem sem filtro de workspace mistura os dois
  e engana. Identidade da conta: user id `53116224`, username `lgfinotellosld`.

## Chave / autenticação

- A PMAK vive em `~/.cursor/mcp.json` → `mcpServers.postman.env.POSTMAN_API_KEY` (64 chars, prefixo
  `PMAK-`). O MCP já usa essa chave sozinho — não peça nem cole a chave em prompt.
- Em **script** de fallback (API REST), ler a chave desse arquivo e **nunca imprimir** seu
  valor (nem em stdout, nem em log). Header da API: `X-Api-Key: <PMAK>`.
- A chave é **privada do Luiz** — não compartilhar, não nagar para rotacionar, não colar em
  artefato que saia da máquina (memória: `postman-chave-privada-do-luiz`).

## Collections

- Criar com `createCollection`; request novo ou alterado com **`createCollectionRequest`** /
  **`updateCollectionRequest`** (um por cenário). `putCollection` substitui a collection inteira e é
  barrado pelo classificador em collection compartilhada — não está na lista do `especialista-postman`
  (equivalente REST: `POST /collections?workspace=`, `PUT /collections/{uid}`). Body no schema **v2.1.0**, sempre
  dentro do wrapper `{"collection": {...}}`.
- **Quirk do schema MCP** (`additionalProperties:false`): as `variable` de **topo** da coleção
  aceitam só `key`, `value`, `description`, `disabled` — **NÃO aceitam `type`**. Remova o campo
  `type` de cada variável antes de enviar, ou a chamada é rejeitada.
- Ao reaproveitar um export (Postman app → Export), remova `_postman_id`/`id`/`uid` herdados
  antes de subir — o endpoint recria com IDs novos de qualquer forma.
- Já existe no workspace do Luiz: **"Fluxo Cancelamento Cliente — Homol (SENSE)"**
  (uid `53116224-91acfca0-2ab5-45da-8ce5-208a638f212d`).

## Environments — casa das constantes

- Criar com `createEnvironment`, atualizar com `putEnvironment` (REST equivalente:
  `POST /environments?workspace=`, `PUT /environments/{id}`, ou `PATCH` para 1 operação por
  chamada). Wrapper `{"environment": {...}}`, array `values` com `key`, `value`, `type`
  (`secret`|`default`), `enabled`, `description`.
- É aqui que constantes e segredos de ambiente devem viver — não em Globals (ver abaixo).
- Já existem no workspace do Luiz:
  - **"Homol — Cancelamento SENSE"** (uid `53116224-d86dd942-781d-491b-abba-a5476a83e26c`, 13 vars).
  - **"env"** (uid `53116224-f4945c8f-c863-4915-8636-0d745a005f8c`, 258 values — todo o `.env`
    do cit).

## Globals — PROIBIDO usar

- **Não existe tool de Globals no MCP.** O endpoint REST
  (`GET`/`PUT /workspaces/{id}/global-variables`, campo `values`) é **inconfiável**: em teste
  de campo o app mostrou valores preenchidos enquanto a API pública lia `values: []` de um
  processo independente — leitura e escrita dessincronizadas.
- Decisão tomada com o Luiz: **nunca usar Globals**. Toda constante vai para um Environment.
  Os Globals da conta já foram limpos (`values: []`).

## Upload de segredos em massa (`.env` → Postman)

- Rota **obrigatória: script**, não MCP nem prompt. O script lê o arquivo local e envia direto
  à API — os **valores nunca entram no contexto do modelo**. stdout do script imprime só
  **contagens** (quantas chaves, quantas alteradas), nunca a chave nem o valor.
- Por quê não MCP: `createEnvironment`/`putEnvironment` via MCP exigem os `values` como
  argumento da chamada — isso traria cada segredo para o contexto do modelo. Por isso o upload
  em massa é a **exceção** que passa por script/API, nunca por tool MCP.
- Duas barreiras do harness que isso atravessa, nessa ordem:
  1. Ler o `.env` para subir à nuvem é tratado como potencial exfiltração de dado — só prossiga
     **com OK explícito do Luiz antes** (gate de escrita externa em recurso de terceiro).
  2. Nunca imprimir segredo em stdout/log — isso é barrado como exfiltração de dado
     independente do OK acima.

## Higiene sempre

- **Antes** de sobrescrever ou apagar qualquer recurso (collection, environment) no Postman:
  `GET` do estado atual + backup em `~/backups-brain/` com data + pergunta de permissão ao Luiz(humano). Apagar sem esse backup é
  irreversível — já houve incidente perdendo um `environment` desse jeito.
- Depois de subir ou alterar algo por API/MCP, peça ao Luiz para dar **Refresh/Sync** no app
  Postman — o app não reflete a mudança sozinho na hora.
- Nunca chamar de "lixo" um recurso do workspace sem antes confirmar (GET) que ele está de
  fato obsoleto.

## Referências oficiais

Pesquisadas em 17/09/2026, fonte primária = collection oficial "Postman API" v1.45.1.

- **Autenticação** (header `X-Api-Key`, base `https://api.getpostman.com`, EU
  `https://api.eu.postman.com`):
  https://learning.postman.com/docs/reference/postman-api/authentication
- **Referência da API** (fonte primária):
  https://www.postman.com/postman/postman-public-workspace e
  https://documenter.getpostman.com/view/12959542/UV5XjJV8
- **Collections:** `POST /collections?workspace=`, `PUT /collections/{uid}` (replace total),
  wrapper `collection`, schema `v2.1.0`, limite de corpo **100 MB**.
- **Environments:** `POST /environments?workspace=`, `PUT /environments/{id}` (replace),
  `PATCH /environments/{id}` (1 operação por chamada), wrapper `environment`, array `values`,
  limite **30 MB**. Só variáveis "shared"/sincronizadas são editáveis via API.
- **Global variables:** `GET`/`PUT /workspaces/{workspaceId}/global-variables`, campo do array
  é **`values`**. PUT é replace total. Relato de comunidade (não oficial) de que globals de
  workspace via API não são confiáveis — casa com o teste de campo:
  https://community.postman.com/t/how-to-update-my-public-workspace-global-variables-with-the-api/65214
- **Rate limits:** geral 300 req/min; **Write (POST/PUT/PATCH) 180/min**, **Read (GET)
  300/min**; `GET /collections`, `GET /workspaces{,/id}` e Monitors: 10 chamadas/10s; workspace
  updates 20/min.
  https://learning.postman.com/docs/developer/postman-api/postman-api-rate-limits/
- **MCP server oficial:** https://github.com/postmanlabs/postman-mcp-server · npm
  `@postman/postman-mcp-server` · config via env `POSTMAN_API_KEY`
  (`POSTMAN_API_BASE_URL` para EU). Modos: **minimal** (padrão), **code**, **full** (100+
  tools, inclui Enterprise), **learn** (busca na doc). O README não cita tool específica de
  "global variables" — não confirmado se `full` cobre; validar em runtime se precisar. A
  instância em uso roda **@2.12.3**.

## Memórias relacionadas

`postman-workspace-sempre-o-do-luiz`, `postman-chave-privada-do-luiz`,
`nunca-apagar-recurso-externo-sem-backup`, `pedir-permissao-antes-de-escrita-externa`,
`mcp-inventario-escopos-e-alcance`.
