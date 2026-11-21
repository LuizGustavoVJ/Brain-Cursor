---
name: monitoramento-datadog-grafana
description: Luiz instalou datadog e grafana-cloud-mcp de proposito para monitorar os projetos; Grafana LIGADO em 18/09/2026 (Connected, stack tallcrab2315), Datadog ainda nao; dono e o especialista-observabilidade
metadata:
  type: project
---

Em 18/09/2026 o usuário instalou os plugins `datadog` e `grafana-cloud-mcp` **de propósito**: quer
monitoramento dos projetos, embora nenhum repositório tenha instrumentação hoje (o grep só acha
`vendor/aws-sdk`). O **Grafana ficou ligado em 18/09/2026** (`claude mcp get grafana-cloud` →
`Status: ✔ Connected`). O **Datadog continua desligado** — falta chave de API.

**Prefixo real das tools** (sai do nome do SERVIDOR, não do plugin): Datadog = `mcp__plugin_datadog_mcp__*`
(provado pelo matcher do `hooks/hooks.json` do próprio plugin); Grafana = `mcp__grafana-cloud__*`.
`mcp__datadog__*` e `mcp__grafana__*` estavam errados no mapa e foram corrigidos em 18/09.

As 5 skills do `datadog` são só setup do MCP `plugin:datadog:mcp` (`ddviz` é macOS, inútil aqui).
`grafana-cloud-mcp` é servidor hospedado com 60+ tools (Prometheus, Loki, Tempo, alerting, OnCall).

Dono: `especialista-aws` (absorveu observabilidade na Fase 3, 25/09); conexão e toolsets: `engenheiro-de-brain` (absorveu o especialista-mcp). O
gatilho `telemetria` já casa `datadog|grafana|prometheus` — não criar gatilho novo.

**Why:** deny contra tool inexistente não protege; e monitoramento é insumo de diagnóstico, não
fecha gate nenhum.

**How to apply:** nenhum agente declara tool de servidor desligado (hoje: Datadog). Para o Grafana,
declarar só as de leitura, conferidas contra a lista viva do servidor. Escrita no Grafana (dashboard, incidente, regra de alerta
e o `ask_assistant`, que é write-scoped) para no chat e espera OK.

**Como o Grafana foi ligado (18/09, medido — CONCLUÍDO):** o botão "Vincular" do plugin fica cinza porque o conector
`grafana-cloud` não existe na conta — `claude mcp list` não o traz. O caminho que funciona não passa
por esse botão: `claude mcp add --transport http grafana-cloud https://mcp.grafana.com/mcp --scope
user` e depois **`claude mcp login grafana-cloud`** no terminal (Claude Code faz Dynamic Client
Registration sozinho; sem client id/secret). O `login` é melhor que o `/mcp`: não depende de menu
nem de sessão interativa, e foi ele que destravou — o `/mcp` estava sombreado por comando do Brain
(ver [[comando-de-projeto-sombreia-embutido]]). Desfaz com `claude mcp remove grafana-cloud --scope user`. O classificador de
auto mode barra o `mcp add` para o agente (Unauthorized Persistence) — **quem roda é o usuário**.
Pré-condição do lado Grafana: stack Grafana Cloud existente, termos do Grafana Assistant aceitos
por um admin e papel Editor ou superior; sem isso o servidor fica em "Needs authentication".

**Stack Grafana Cloud (18/09):** conta criada pelo usuário, stack `https://tallcrab2315.grafana.net`
— é ESSA a URL a colar quando o `/mcp` pedir (sem o caminho `/a/...` do onboarding). Conta nova e
pessoal: o stack nasce VAZIO, nenhum projeto manda métrica/log para lá ainda. Descoberta OAuth e consentimento **concluídos em 18/09**
(tela "Authentication successful"; `Status: ✔ Connected`). Na tela de consentimento a ESCRITA é um checkbox separado — desmarcar
deixa o conector só-leitura e derruba o `ask_assistant`.

**Tool não chega em sessão viva.** Conectar o servidor NÃO injeta `mcp__grafana-cloud__*` nas abas já
abertas — é preciso reiniciar a sessão para o catálogo de tools ser relido. Mesma regra dos
conectores Google ([[google-workspace-conectores-nativos]]).
