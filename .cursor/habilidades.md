# Habilidades fora do Brain — conta, CLI e plugin

> Fonte única do **encaixe**. O que cada habilidade faz está nela mesma; aqui está **quem da frota
> usa, em que momento, e o que ela não pode substituir**.
> Três origens diferentes, um encaixe só. Nenhuma delas é do Brain: o Brain propaga, estas não.
> Além das três origens, uma quarta leitura por **necessidade** (HTML/evidência, dado/SQL, teste,
> documento, apresentação, código, meta, infra, CI/CD, observabilidade, segurança, integração,
> Postman, frontend/UX — 14 grupos, mais o que nenhuma das três origens cobre) está em "Grupos por
> demanda", mais abaixo.

| Origem | Onde vive | Invocável com `Skill(...)`? | Propaga? |
|---|---|---|---|
| 1. Skills da conta (8) | `~/.cursor/skills/synced/<bucket>/` | sim | não — escopo de usuário |
| 2. Skills embutidas no CLI (16) | vêm com o CLI, sem arquivo até a 1ª invocação | sim | não — vêm na versão do CLI |
| 3. Plugins sincronizados (9) | `~/.cursor/plugins/synced/<bucket>/` | **não** enquanto `available` | não |

Tudo isso é **escopo de usuário**: vale em todos os repositórios sem `propagar.sh`. O Brain
(`.cursor/`) propaga; isto não — se sumir, o caminho é a conta em cursor.com, não o repositório.

O nome do bucket é um UUID que **muda a cada re-sync**. Nunca cravar esse caminho em agente, skill
ou script — resolver sempre por nome:

```bash
.cursor/scripts/skills_conta.sh listar                 # as três camadas
.cursor/scripts/skills_conta.sh caminho <nome>         # diretório da skill da conta
.cursor/scripts/skills_conta.sh tem <nome>             # 0/1, para usar em if
.cursor/scripts/skills_conta.sh plugins                # plugins e se estão habilitados
.cursor/scripts/skills_conta.sh ler-plugin <p>/<s>     # texto de uma skill de plugin
```

Quem tem a ferramenta `Skill` invoca pelo nome curto (`Skill(skill: "xlsx")`). Agente sem essa
ferramenta lê o `SKILL.md` pelo caminho do script acima — o conteúdo é o mesmo.

---

## Origem 1 — skills da conta (8)

| Skill | Quem usa | Entra quando | Não substitui |
|---|---|---|---|
| `skill-creator` | `engenheiro-de-brain` | criar ou reescrever skill/agente, e **sempre** que a queixa for "o agente não foi acionado" ou "foi acionado à toa" — a skill mede a `description` com eval, que é o que o Brain não tinha como medir | o gatilho por artefato nem a revisão humana do texto |
| `pdf` | `pesquisador-web` | documento de terceiro em PDF — manual de gateway, contrato, norma, transcrição | a citação obrigatória de página/seção |
| `docx` | `pesquisador-web`, `redator-tecnico` | documento recebido de área de negócio (.docx) ou entregável que o destinatário pediu em Word | documento do fluxo, que é `.md`/`.html` em `docs/` |
| `xlsx` | `especialista-sql`, `pesquisador-web` | planilha é a **entrada** (catálogo, massa, cronograma) ou a **saída** pedida pelo usuário | o gatilho `metrica`: a definição do número é conferida antes de virar planilha |
| `pptx` | `redator-tecnico` | apresentação de status pedida por nome (.pptx) | evidência de card — evidência é HTML no padrão canônico |
| `docs` (docs publicados) | contexto principal, `redator-tecnico` | documento vivo para **humano de fora do fluxo** ler e comentar | **nada do fluxo** — ver a regra de fronteira |
| `morning` | contexto principal, a pedido explícito | o usuário pede o brief do dia por nome | acompanhamento de card |
| `import-memory` | ninguém, por ora | só se o usuário quiser trazer memórias de ChatGPT/Gemini | a memória do projeto, escrita pelo `destilador-dominio` |

### Armadilha do `skill-creator`

Ele **escreve dentro do repositório**: fabrica arquivo em `.cursor/commands/` e cria
`<skill>-workspace/`. Na raiz do projeto isso dispara gatilho, entra no `frota.sh lint` e **viaja no
`propagar.sh` para os 13 repositórios**. Rode sempre com o diretório de trabalho no **scratchpad da
sessão**. No dia a dia use só `scripts/improve_description.py`; o eval completo (`run_loop.py`) fica
para erro de roteamento comprovado duas vezes.

---

## Origem 2 — skills embutidas no CLI (16)

Vêm com a versão do CLI, aparecem no catálogo (inclusive dentro de subagente) e **não têm arquivo em
disco antes da primeira invocação**. Três delas **executam de verdade** em vez de devolver texto —
essa é a diferença que manda no encaixe.

### As três que executam — trava antes do uso

| Skill | Quem usa | Entra quando | Trava inviolável |
|---|---|---|---|
| `code-review` | `revisor-codigo` (leitura do achado), **invocação só no contexto principal** | I6 e toda revisão de diff/MR | **nunca** com `--comment` — ela posta em PR/MR e o agente não publica. `--fix` altera o working tree: só com pedido explícito do usuário |
| `security-review` | `especialista-seguranca` | I6-rev, quando houve segurança no I1-rev | tratar como "pode publicar" até prova em contrário: achado vai para o doc da etapa, nunca para o MR |
| `simplify` | `arquiteto-plano` | depois do I6 aprovado, antes de commit | **aplica correção no working tree SEMPRE, sem flag para desligar** — por isso nunca dentro de subagente de etapa: furaria o I4 (código só depois do OK) |

**Regra que vale para as três:** elas rodam em execução forkada e mexem no working tree ou publicam.
São invocadas no **contexto principal**, com o working tree conhecido, nunca como passo automático de
uma etapa e nunca por um subagente.

**A trava é estrutural, não é instrução.** `revisor-codigo`, `especialista-seguranca` e
`arquiteto-plano` são somente leitura por desenho (`Read, Grep, Glob, Bash`) — e continuam
**sem a ferramenta `Skill`**. Dar `Skill` a eles abriria por dentro da tool exatamente a escrita que a
lista de ferramentas existe para impedir. Eles leem o achado; quem invoca é o contexto principal.

Cuidado geral: **`Skill` dá o catálogo inteiro**, inclusive `init` — que sobrescreveria o `AGENTS.md`.
Por isso a ferramenta só entra em agente que tem motivo nomeado aqui.

### As que só produzem texto ou configuração

| Skill | Quem usa | Entra quando | Não substitui |
|---|---|---|---|
| `update-config` | `engenheiro-de-brain` | mexer em hook, `permissions`, `env`, `settings.json`, MCP | o rito dela é o ganho: ler antes de escrever, **mesclar array em vez de sobrescrever**, provar que o hook disparou, limpar sentinela. Depois, `propagar.sh` |
| `dataviz` | `especialista-sql` (invoca — tem `Skill`; `escritor-evidencias` só embute a imagem já gerada, não invoca) | gráfico em análise ou relatório de dados | evidência de card, que segue o layout canônico — gráfico é insumo, não print |
| `run` | `ambiente-local` | L0 quando o repo não tem receita própria | a skill `ambientes-e-testes`, que continua sendo a fonte |
| `workflow-authoring` | contexto principal | varredura em escala (auditar todas as rotas, achar todos os pontos de um fluxo), **só com pedido explícito do usuário** | etapa nem gate — e a própria skill diz que não autoriza executar |
| `cursor-billing` | `engenheiro-de-brain` (custo de token, cache, janela) | só se formos codar contra a API da provedor de modelos, ou para medir custo do Brain | nada hoje: nenhum código nosso chama essa API. Subcomandos dela editam código e **gastam crédito real** |
| `loop`, `schedule` | ninguém por ora | acompanhar pipeline longo, se o usuário pedir | **nada é agendado sem pedido explícito** |
| `fewer-permission-prompts`, `keybindings-help` | `engenheiro-de-brain`, a pedido | conforto da IDE | — |
| `artifact-design`, `artifact-diagramming`, `artifact-capabilities` | ninguém | — | não publicamos Artifact: entregável de card é HTML em `docs/` |
| `init` | **ninguém — proibida neste repositório** | — | sobrescreveria o `AGENTS.md` do Brain |

---

## Origem 3 — plugins sincronizados (9)

Todos com `installationPreference: available`: **baixados pela conta, não instalados pelo CLI**
(`cursor plugin list` → "No plugins installed"). Nenhuma skill deles aparece no catálogo e nenhuma é
invocável. Servem como **texto de referência**, lido sob demanda — custo zero de contexto permanente:

```bash
.cursor/scripts/skills_conta.sh ler-plugin data/validate-data
```

`data`(10) · `datadog`(5) · `datarobot-agent-skills`(16) · `grafana-cloud-mcp`(1) · `monday-crm`(9)
`product-tracking-skills`(7) · `servicenow-sdk`(1) · `small-business`(44) · `zapier`(4)

### O que aproveitamos — citação, nunca cópia

O mapa **cita** `<plugin>/<skill>` e o motivo em uma linha. Copiar o conteúdo para cá criaria a
tabela duplicada que o Brain proíbe: quem precisa do detalhe roda `ler-plugin` e lê a fonte.

| Texto de referência | Quem lê | Para quê |
|---|---|---|
| `data/validate-data` | `especialista-sql` | QA do número antes de ele sair |
| `data/statistical-analysis` | `especialista-sql` | "desde quando piorou", outlier, sazonalidade |
| `data/explore-data` | `especialista-sql` | perfilar tabela nova — perfil não decide schema |
| `data/sql-queries` | `especialista-sql` | seção BigQuery. **Não cobre MySQL**, que é do `especialista-sql` |
| `data/data-context-extractor` | `engenheiro-de-brain` | criar mapa `dominio-*` de dados — a âncora `arquivo:linha` continua valendo |
| `data/build-dashboard` | `testador` (board ao vivo em I7/I10/I13), `especialista-sql` (board pontual fora de card) | HTML interativo autocontido (KPI card, filtro, tabela, gráfico Chart.js via CDN), abre no browser sem servidor — desenho concreto do board de testes na subseção abaixo |
| `data/create-viz` | `especialista-sql` | gráfico Python (matplotlib/seaborn/plotly) publication-quality fora do board — é insumo de análise, não print de evidência |
| `data/data-visualization` | idem `create-viz` | guia de escolha de tipo de gráfico; não executa nada sozinho |
| `small-business/report-builder` | `especialista-sql` | armadilhas de relatório recorrente |
| `small-business/build-agent` | `engenheiro-de-brain` | extrair a especificação da conversa em vez de reinterrogar |
| `small-business/build-connector` | `engenheiro-de-brain` | mapa conector → quem consome → fallback quando ele cai |
| `small-business/smb-router` | contexto principal | desempate entre dois especialistas: perguntar uma vez, manter a escolha |

**Dependência Python de `create-viz`/`data-visualization` — instalada em 25/09/2026:**
`python3 -c "import pandas, matplotlib"` responde `pandas 2.1.4 | matplotlib 3.6.3` neste host
(instaladas com `sudo apt-get install python3-pandas python3-matplotlib`). As duas skills estão
**disponíveis**. Divisão de trabalho: `create-viz`/`data-visualization` geram gráfico Python
estático (PNG/SVG) para **insumo de análise** em `docs/`; o board ao vivo e qualquer HTML de
evidência continuam no `data/build-dashboard` (Chart.js via CDN, interativo, sem Python).
Gráfico Python **nunca** substitui o print de tela real da evidência de card.

### Board de testes ao vivo — `build-dashboard` durante I7/I10/I13

Desenho concreto, não é proposta em aberto:

- **Quem gera:** o `testador`, no mesmo momento em que roda `.cursor/scripts/resumo_testes.sh`
  — é quem já tem a query de fixture na mão e o log crescendo em disco em tempo real. O
  `escritor-evidencias` fica de fora do board: ele só entra depois, para o entregável oficial.
- **A partir de quê:**
  - o log que `resumo_testes.sh` grava em `.cursor/cache/logs-testes/` cresce durante a execução
    porque a redireção `> "$LOG" 2>&1` é do processo inteiro, não um buffer pós-término
    (`.cursor/scripts/resumo_testes.sh:27-32`) — dá para `tail -f` nele enquanto o Playwright roda;
  - a tabela de cenário por cenário é o mesmo grep que o script já faz
    (`.cursor/scripts/resumo_testes.sh:38-41`) e o placar agregado é a mesma linha de sumário
    (`resumo_testes.sh:45`);
  - as queries são o mesmo texto exato que a regra "query acima do print" já obriga registrar em
    evidência (`.cursor/agents/escritor-evidencias.md:47`) — o board reaproveita essa disciplina em
    vez de criar uma segunda forma de anotar query. **Gap hoje:** o `testador` não persiste essas
    queries em arquivo à parte durante a execução; até isso existir, o board nasce só com
    cenário+placar, e a aba de queries entra quando o `testador` gravar
    `.cursor/cache/queries-teste/<alvo>-<timestamp>.jsonl` (uma linha por query rodada em fixture).
- **Onde salva:** `.cursor/cache/boards-teste/<alvo>-<timestamp>.html` — mesmo padrão de
  `.cursor/cache/logs-testes/`, fora de `docs/`, gitignored (`.cursor/` inteiro está fora do git),
  nunca versionado.

**Fronteira dura, sem exceção:**

- O entregável de card continua sendo o **HTML canônico em `docs/`** (`evidencias.html` /
  `evidenciashomol.html`), validado pelo `validador-tecnico` em I9/I11/I14 — o board **não** entra
  em gate, **não** é anexado, **não** é citado como prova de teste.
- Board de erros é **ferramenta de acompanhamento interno**: ajuda a diagnosticar rápido enquanto
  a suíte roda, não é o que prova que I10/I13 passou — quem prova é o `resumo_testes.sh` (código
  de saída + tabela) mais o print Playwright que o `escritor-evidencias` embute depois.
- HTML gerado por `build-dashboard` é **arquivo local**, nunca Artifact publicado nem docs publicados
  — a regra de fronteira da seção abaixo vale igual para o board.

**Duas condições de uso.** Se o `ler-plugin` falhar — re-sync mudou o bucket, plugin saiu da conta —
o agente diz **"não disponível"** e segue sem isso; **nunca cita de memória**. E conteúdo que for
usado duas vezes e se provar estável **vira destilação dentro do Brain** (skill ou mapa de domínio),
não referência eterna a arquivo fora do repositório.

**Fora**: `zapier`, `monday-crm`, `servicenow-sdk`, `datarobot-agent-skills`, `product-tracking-skills`
e as outras 40 do `small-business` — ferramentas que o time não opera e domínio de pequena empresa dos
EUA (contabilidade, folha, imposto, Canva). **Plugin `data` fica HABILITADO** (decisão do usuário, 25/09/2026 — suas skills são usadas pela frota,
ver tabela abaixo). Custo aceito: o `.mcp.json` dele declara servidores MCP (amplitude, bigquery, hex…)
que aparecem como "needs auth" e o `definite` falha ao conectar — ruído, não erro.

### Monitoramento — `datadog` e `grafana-cloud-mcp`

Instalados de propósito pelo usuário: o alvo é **monitoramento novo**, não instrumentação existente
(nenhum repositório tem `dd-trace`, Datadog ou Grafana hoje). **Autenticam de formas diferentes** —
não trate os dois como o mesmo problema:

- **Grafana — OAuth. LIGADO em 18/09/2026** (`cursor mcp get grafana-cloud` → `Status: ✔ Connected`,
  escopo de usuário, stack `https://tallcrab2315.grafana.net`). O botão *Vincular* da aba Conectores
  do plugin fica cinza porque o conector não existe na conta; o caminho que funciona não passa por
  ele: `cursor mcp add --transport http grafana-cloud https://mcp.grafana.com/mcp --scope user` e
  depois **`cursor mcp oauth grafana-cloud`** no terminal (o CLI faz Dynamic Client Registration
  sozinho, sem client id/secret). O `login` vale mais que o menu: não depende de sessão interativa
  nem de comando de projeto sombreando o `/mcp` embutido. Desfaz com `cursor mcp remove
  grafana-cloud --scope user`. Exige stack Grafana Cloud existente, termos do Grafana Assistant
  aceitos por um admin e papel Editor ou superior. **As tools só chegam à sessão aberta DEPOIS de
  reiniciar** — conectar não injeta tool em sessão viva.
- **Datadog — chave de API, não OAuth.** `.dd_cursor-mcp.json` manda `DD_API_KEY`,
  `DD_APPLICATION_KEY` e `X-Datadog-MCP-Toolsets` como header, com o domínio em `DD_MCP_DOMAIN`.
  Sem as duas chaves a URL vira `not-setup` e o servidor fica mudo. **Ainda não ligado.**

As cinco skills do `datadog` não entregam observabilidade nenhuma — são setup do servidor MCP
`plugin:datadog:mcp`: `ddsetup` (1ª configuração: escolhe o domínio, depois `/reload-plugins` e `/mcp`),
`ddconfig` (troca domínio ou organização, diagnostica servidor mudo), `ddtoolsets` (liga grupos de
tools: logs, metrics, traces, alerting), `ddviz` (**macOS only — inútil aqui**) e `datadog-app`
(scaffolding de app, fora do escopo). O valor vem das tools depois de autenticado.

`grafana-cloud-mcp` é um servidor HTTP hospedado com 60+ tools: Prometheus, Loki, Tempo, Pyroscope,
ClickHouse, CloudWatch, Elasticsearch, alerting, incidentes, OnCall e dashboards.

| Quando ligarem | Dono | Entra quando | Trava |
|---|---|---|---|
| tools MCP do Datadog e do Grafana | `especialista-aws` | incidente em produção, latência, erro em lote, "desde quando piorou" | leitura corre solta; **escrita para no chat e espera OK** |
| `ddsetup` / `ddconfig` / `ddtoolsets` | `engenheiro-de-brain` | conectar, trocar organização, servidor que não responde | conta, chave de API e consentimento são do usuário — o agente não autentica |
| log e trace na investigação | `analista-causa-raiz` | S3 e depuração, quando o rastro não está no repositório | não substitui reprodução local |

São **escrita** no Grafana, conferido contra a lista viva de 18/09 (117 tools): `update_dashboard`,
`create_folder`, `create_datasource`, `update_datasource`, `install_plugin`, `create_annotation`,
`update_annotation`, `delete_annotation`, `create_snapshot`, `delete_snapshot`, `create_incident`,
`update_incident`, `add_activity_to_incident`, `create_investigation`, `alerting_manage_rules`,
`alerting_manage_silences`, `alerting_manage_routing`, `update_alert_group`, **`grafana_api_request`**
(genérica — aceita qualquer verbo, trate como escrita) e **`ask_assistant`** (write-scoped: autorizar
só leitura no OAuth desliga a pergunta em linguagem natural). `find_error_pattern_logs` e
`find_slow_requests` **não existem** no servidor — estavam errados aqui e saíram.

**Quem tem as tools:** nenhum agente desde a Fase 3 (25/09/2026) — o antigo especialista de
observabilidade foi aposentado até o OAuth existir (o stack estava vazio). Quando ligarem, o
`especialista-aws` recebe **só as de leitura** (datasources, dashboards, Prometheus, Loki, Tempo,
incidentes, docs). Escrita não entra na lista de agente nenhum — passa pelo chat do orquestrador e
espera OK do usuário.

**Contexto:** usar `get_dashboard_summary` no lugar de `get_dashboard_by_uid` e
`get_dashboard_property` com JSONPath. Dashboard JSON inteiro estoura a janela.

**Prefixo real das tools — confira antes de declarar.** O prefixo sai do nome do *servidor*, não do
plugin: Datadog declara o servidor `mcp` dentro do plugin `datadog`, logo
**`mcp__plugin_datadog_mcp__*`** (provado pelo matcher do próprio `hooks/hooks.json` do plugin); o
Grafana foi adicionado direto como `grafana-cloud`, logo **`mcp__grafana-cloud__*`**. Escrever
`mcp__datadog__*` ou `mcp__grafana__*` é errar o alvo — a regra não pega em nada.

**Grafana já está ligado; o Datadog não.** Nenhum agente declara tool de servidor desligado — deny
contra tool que não existe não protege ninguém. Para o Grafana, declarar **só as de leitura**,
conferidas contra a lista viva do servidor (`cursor mcp get grafana-cloud` em sessão reiniciada). Gatilho: o `telemetria` já casa `datadog|grafana|prometheus`,
não há gatilho novo a criar.

**Nada disso fecha etapa.** Monitoramento é insumo de diagnóstico; quem sustenta gate continua sendo
teste + `validador-tecnico`.

### Diagramação — conector `Figma` (conta, escopo cursor.com)

Ligado por decisão do usuário em 25/09/2026: "comece a usar o Figma... para desenho de fluxos e
regras de negócio". É **conector de conta**, não skill do Brain — tools `mcp__legacy_figma__*`;
não propaga por arquivo (só o TEXTO que o referencia, aqui e no fluxo, propaga).
`whoami` confirmado: Luiz Gustavo Finotello, plano **Starter**, assento View, role admin.

**Cota — o limite real é o teto, não a conveniência.** Doc oficial do servidor
(`file://figma/docs/rate-limits-access.md`): plano Starter = **20 chamadas de tool por mês**
(tools de leitura contam; `create_new_file`, `add_code_connect_map` e `whoami` são isentas). O
plano Starter também limita arquivos FigJam por time — **a confirmar** na doc oficial, ainda não
lida linha a linha. Regra de uso: nunca em loop, **nunca ler de volta** um board que o próprio
agente acabou de desenhar — cada leitura consome cota do mês inteiro.

**Quem chama a tool — só o contexto principal.** Nenhum agente da frota declara
`mcp__legacy_figma__*` no frontmatter. Não foi possível testar se um subagente (`Task`)
alcançaria a tool — este ambiente não tinha ferramenta de spawn disponível para o teste — por isso
foi adotado direto o caminho seguro já conhecido ("tool não declarada não chega ao subagente",
`mcp-inventario-escopos-e-alcance`): o subagente (`mapeador-fluxo`, `levantador-requisitos`,
`arquiteto-plano`, `analista-causa-raiz`) escreve o Mermaid **dentro do próprio documento**; o
contexto principal, só quando valer a cota, lê esse bloco e chama `generate_diagram`.

**Economia — no máximo 1 board por card.** `generate_diagram` aceita `fileKey` de um board
**existente** para ADICIONAR diagrama (testado, funciona — não cria arquivo novo); todo diagrama
do mesmo card usa o mesmo `fileKey`, guardado pelo contexto principal na primeira chamada do card.
Tipos suportados: `flowchart`/`graph`, `sequenceDiagram`, `stateDiagram`, `gantt`, `erDiagram`.

**Onde entra:** S1 (fluxo ponta a ponta), pré-I1 (regra de negócio como árvore de decisão), S3/I1
(integração entre sistemas, schema novo) e fora de card só a pedido — **nunca por padrão na
trilha curta**. Detalhe por etapa: [`.cursor/fluxo-completo.md`](fluxo-completo.md) § *Diagrama
Figma/FigJam*.

**Pergunta antes de usar — sempre, inclusive board novo.** Antes de chamar `generate_diagram`
(criar board novo do card ou adicionar num existente), o contexto principal pergunta "Vale
desenhar isto no Figma?" mostrando o porquê, e só chama depois do OK (correção de 25/09/2026 —
substitui a autorização permanente anterior). **Exceção:** quando o agente julgar extremamente
necessário, usa sem perguntar e comunica logo em seguida no chat (o que desenhou, o link, por que
foi necessário). **Alterar ou apagar** board que o agente não criou no card sempre exige perguntar
antes — mesma cautela de `nunca-apagar-recurso-externo-sem-backup`.

**Exemplo já criado (25/09/2026, teste fora de card):** board "Brain — fluxo por card (trilha
curta x completa)", `fileKey XUTaRVVYy549785lXKCZdn` — prova que `generate_diagram` com `fileKey`
adiciona ao board existente em vez de criar um novo.

**Fonte única:** o Mermaid no `.md` do card é o entregável e o que sustenta gate; o link do FigJam
é visualização/colaboração, anotado no mesmo documento — nunca substitui o Mermaid, nunca é citado
como prova de etapa, e o documento oficial continua sem citar agente (`frota/regras.md` § 11).

---

## Grupos por demanda — da necessidade às skills certas

Segunda camada de leitura, por cima das três origens acima. Origem organiza *onde a skill mora*;
aqui organiza *o que fazer com ela* — diante de uma necessidade concreta do fluxo, qual conjunto
pequeno (2–6) cobre o Brain inteiro para aquele tipo de demanda. **Não duplica** as tabelas de
origem: cada linha aponta de volta para a seção onde o encaixe completo já está descrito.

**14 grupos**, derivados do fluxo (`.cursor/fluxo-completo.md`) e da tabela de gatilhos por
artefato (`.cursor/frota/gatilhos.tsv`) — não são exemplo, são a demanda real dos 13 projetos. Uma
mesma skill pode aparecer em mais de um grupo (ex.: `dataviz` em três) porque o corte é por
*demanda*, não por skill; a descrição continua vivendo uma vez só, na origem. Demanda sem
habilidade externa que a sirva **não** ganha tabela vazia — vai para "Lacunas", ao final da seção.

### 1. HTML / evidências / board de acompanhamento

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `evidencias-html-ado` | skill Brain (propaga) | `escritor-evidencias` | I2-html, S3, I9, I11, I14 | o layout canônico é obrigatório — não inventar CSS inline |
| `dataviz` | CLI embutida | `especialista-sql` (invoca — tem `Skill`; `escritor-evidencias` só embute a imagem já gerada, não invoca) | gráfico dentro de análise/relatório | print de evidência, que segue o layout canônico |
| `data/build-dashboard` | plugin | `testador` (board ao vivo), `especialista-sql` (board pontual) | I7/I10/I13 monitorando execução, ou ad-hoc fora de card | `evidencias.html` canônico — ver "Board de testes" acima |

### 2. Dados / queries / SQL / migrations

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `mysql-solides` | skill Brain (propaga) | `especialista-sql` | qualquer SELECT/DDL/DML MySQL, inclusive migration — gatilho `sql` (`.cursor/frota/gatilhos.tsv`) é obrigatório | o gatilho, que continua exigindo o especialista mesmo com a skill lida |
| `data/validate-data` | plugin | `especialista-sql` | QA do número antes de ele sair | o gatilho `sql`/`metrica` |
| `data/sql-queries` | plugin | `especialista-sql` | seção BigQuery da consulta | **não cobre MySQL** — isso é do `especialista-sql` |
| `data/explore-data` | plugin | `especialista-sql` | perfilar tabela nova antes de criar coluna/índice, gatilho `schema` (`gatilhos.tsv`) | perfil não decide schema — a decisão em si é lacuna, ver seção "Lacunas" |
| `data/statistical-analysis` | plugin | `especialista-sql` | "desde quando piorou", outlier, sazonalidade | causa raiz (S3), que é do `analista-causa-raiz` |

**Migrations não ganham grupo próprio:** o gatilho `schema` (`especialista-sql`) e a escrita da
migration em si já são cobertos pela mesma `mysql-solides` (ela cita explicitamente EXPLAIN,
índice, JOIN que duplica **e** migration — ver descrição da skill); o que falta é a **decisão** de
índice/particionamento, e essa decisão não é skill-shaped — é julgamento do `especialista-sql`
sobre o schema concreto do card, por isso vai para "Lacunas".

### 3. Testes (E2E / local / homol)

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `ambientes-e-testes` | skill Brain (propaga) | `ambiente-local`, `testador` | L0, I7/I8/I10/I13 | fonte única de URL/porta/BD é o perfil `arquitetura/ambiente-local-*` |
| `run` | CLI embutida | `ambiente-local` | L0 quando o repo não tem receita própria | a própria `ambientes-e-testes`, que continua sendo a fonte |
| `data/build-dashboard` | plugin | `testador` | board ao vivo durante a execução — desenho completo na seção "Board de testes ao vivo" acima | HTML E2E/local/homol oficial, que sai do `escritor-evidencias` |

### 4. Documento (fluxo, análise, requisitos, plano)

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `pdf` | skill da conta | `pesquisador-web` | manual, contrato, norma, transcrição de terceiro em PDF | a citação obrigatória de página/seção |
| `docx` | skill da conta | `pesquisador-web`, `redator-tecnico` | documento recebido de negócio, ou entregável pedido em Word | documento do fluxo, que é `.md`/`.html` em `docs/` |
| `xlsx` | skill da conta | `especialista-sql`, `pesquisador-web` | planilha como entrada (massa, catálogo) ou saída pedida | o gatilho `metrica` — a definição do número é conferida antes |
| `docs` (docs publicados) | skill da conta | contexto principal, a pedido | documento vivo para leitor de fora do fluxo | **nada do fluxo de card** — ver "Regra de fronteira" abaixo |
| `Figma` (`generate_diagram`) | conector de conta | contexto principal (subagente só escreve o Mermaid) | S1/pré-I1/S3/I1 — fluxo, árvore de decisão, integração, schema — ver "Diagramação — conector `Figma`" acima | o Mermaid no `.md`, que é o entregável e sustenta gate — o board é só visualização |

### 5. Apresentação

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `pptx` | skill da conta | `redator-tecnico` | apresentação de status pedida por nome (.pptx) | evidência de card |
| `dataviz` | CLI embutida | `redator-tecnico` | gráfico dentro da apresentação | print de evidência |

### 6. Código

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `code-review` | CLI embutida (executa) | invocação só no contexto principal | I6, revisão de diff/MR | **nunca** com `--comment` — posta em PR/MR |
| `security-review` | CLI embutida (executa) | `especialista-seguranca` | I6-rev, quando houve segurança em I1-rev | não publica — achado vai para o doc da etapa |
| `simplify` | CLI embutida (executa) | `arquiteto-plano` | depois de I6 aprovado, antes do commit | nunca dentro de subagente de etapa — furaria o I4 |
| `codeigniter2-php-legacy`, `laravel-php-service`, `legacy-frontend-jquery`, `integracao-apis`, `financeiro-modulo` | skills Brain (propagam) | `desenvolvedor` | I5 | leitura da `regras-de-trabalho` antes, sempre |

### 7. Meta — criar/calibrar agente, skill, conector, MCP ou contexto

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `skill-creator` | skill da conta | `engenheiro-de-brain` | criar/reescrever skill ou agente, ou medir por que um não dispara — gatilho `skill` (`.cursor/frota/gatilhos.tsv`)/`agente`/`prompt` | o gatilho por artefato nem a revisão humana do texto — roda sempre no scratchpad |
| `small-business/build-agent` | plugin | `engenheiro-de-brain` | extrair a especificação da conversa em vez de reinterrogar | texto de referência só — não substitui a interview do `skill-creator` |
| `small-business/build-connector` | plugin | `engenheiro-de-brain` | mapear conector → quem consome → fallback quando cai | — |
| `update-config` | CLI embutida | `engenheiro-de-brain` | hook, `permissions`, `env`, `settings.json`, MCP | o rito de ler antes de escrever e provar que o hook disparou — depois, `propagar.sh` |
| `cursor-billing` | CLI embutida | `engenheiro-de-brain` | medir custo de token, cache, janela de contexto — gatilho `contexto` não tem detecção mecânica, é `decl` (`gatilhos.tsv`) | código de produto que chama LLM — não existe hoje em nenhum repo (especialista aposentado na Fase 3) |

### 8. Infra / Docker / ambiente local

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `ambientes-e-testes` | skill Brain (propaga) | `ambiente-local`, `especialista-docker` | L0, container que não sobe — gatilho `container` (`gatilhos.tsv`) | o perfil `arquitetura/ambiente-local-*`, fonte única de URL/porta/BD |
| `run` | CLI embutida | `ambiente-local` | L0 quando o repo não tem receita própria (`docker compose up`, `make up` — ver `estado-projeto-hubspot-adapter.md`) | a própria `ambientes-e-testes` |

Os repositórios Solides não são uniformes: vários sobem por `docker compose`,
`hubspot-adapter` por `make up`, `debt-processing-service` por `./docker/dev-up.sh` — cada um com
receita própria no seu `estado-projeto-*.md`, nenhuma delas skill externa.

### 9. CI/CD e deploy/reversão

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `gitlab-deploy-cicd` | skill Brain (propaga) | `especialista-git` | `.gitlab-ci.yml`, job vermelho, cache, artifact — gatilho `pipeline-ci` (`gatilhos.tsv`) | a decisão de reversão em si, que é do `gestor-de-risco` — ver "Lacunas" |
| `code-review` | CLI embutida (executa) | contexto principal | diff da branch de release antes de abrir o MR | publicar achado — nunca com `--comment`, ver Grupo 6 |

### 10. Observabilidade / telemetria

Detalhe completo de autenticação, escopo e tools já está na seção **"Monitoramento — `datadog` e
`grafana-cloud-mcp`"**, acima; aqui só o encaixe por demanda.

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `datadog:ddsetup` / `ddconfig` / `ddtoolsets` | plugin (referência) | `engenheiro-de-brain` | conectar/trocar organização, servidor mudo — gatilho `telemetria-custo` (`gatilhos.tsv`) | achado de causa, que é do `especialista-aws` |
| `grafana-cloud-mcp-tools` | plugin (referência) | `especialista-aws` | incidente, latência, "desde quando piorou" | reprodução local — não substitui isolar no ambiente |
| `dataviz` / `data/build-dashboard` | CLI/plugin | `especialista-sql` | visualizar série temporal de uma métrica já coletada | a tool viva do Grafana/Datadog quando a organização está ligada |

### 11. Segurança / credencial / exposição

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `security-review` | CLI embutida (executa) | `especialista-seguranca` | I6-rev, quando houve segurança em I1-rev — gatilhos `dado-sensivel`/`exposicao` (`gatilhos.tsv`) | rotação de segredo e enquadramento LGPD — nenhuma skill cobre, ver "Lacunas" |
| `code-review` | CLI embutida (executa) | contexto principal | achado de segurança dentro do diff geral | publicar em PR — nunca `--comment`, ver Grupo 6 |

### 12. Integração / webhook / contrato de terceiro

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `integracao-apis` | skill Brain (propaga) | `especialista-integracao`, `desenvolvedor` | alterar libraries/helpers de chamada HTTP a terceiro — gatilho `terceiro` (`gatilhos.tsv`) | a idempotência do retry em si, que é do `especialista-financeiro-cobranca` |
| `small-business/build-connector` | plugin (referência) | `engenheiro-de-brain` | mapear conector → quem consome → fallback quando cai (mesma linha do Grupo 7) | a implementação do webhook, que é do `especialista-integracao` |

### 13. Postman / collection de cenários (etapa PC)

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `postman-operacao` | skill Brain (propaga) | `especialista-postman` | S6a-pc/I13-pc (`.cursor/fluxo-completo.md:169-180`) e gatilho `postman` (`gatilhos.tsv`) — qualquer collection/environment/segredo subido ao Postman | o workspace certo — **sempre** o do Luiz, nunca Default nem Globals (regra fixa da própria skill) |
| `data/build-dashboard` | plugin | `testador` | board ao vivo referenciando os mesmos cenários que a collection cobre, durante I7/I10/I13 | a collection oficial da etapa PC, que é o que fecha o gate |

### 14. Frontend / UX / acessibilidade

| Skill | Origem | Quem usa | Entra quando | Não substitui |
|---|---|---|---|---|
| `legacy-frontend-jquery` | skill Brain (propaga) | `especialista-php-legado`, `desenvolvedor` | editar view PHP/JS/jQuery legado — gatilho `frontend` (`gatilhos.tsv`) | a fricção de UX da tela, que é do `especialista-ux` — ver "Lacunas" |
| `dataviz` | CLI embutida | `especialista-sql` (invoca — tem `Skill`; `especialista-php-legado`, sem `Skill`, no máximo consome o resultado) | gráfico dentro de uma tela do produto | print de evidência, que segue o layout canônico |

---

## Lacunas — demanda sem habilidade externa que a sirva

Nenhuma das três origens cobre estas oito demandas do fluxo. Registradas aqui em vez de
tabela vazia — território puro de agente/especialista do Brain, sem skill/plugin por trás:

| Demanda | Gatilho (classe · linha) | Quem cobre no Brain |
|---|---|---|
| Concorrência / idempotência / dinheiro | `concorrencia`/`dinheiro` (`gatilhos.tsv`) | `especialista-financeiro-cobranca` |
| Git / branch / release | `git-arvore` (`gatilhos.tsv`) | `especialista-git` + regras de branch do `AGENTS.md` |
| Causa-raiz / depuração | `bug-nao-isolado` (`gatilhos.tsv`) | `analista-causa-raiz` (S3) |
| Dependência / CVE / bump de versão | `dependencia` (`gatilhos.tsv`) | `especialista-seguranca`, apoiado por `pesquisador-web` para a fonte oficial do CVE |
| Migrations — decisão de schema/índice | `schema` (`gatilhos.tsv`) | `especialista-sql` — `data/explore-data` (Grupo 2) só perfila, não decide |
| UX / acessibilidade dedicada (auditoria WCAG, heurística de usabilidade) | `tela` (`gatilhos.tsv`) | `especialista-ux` |
| Reversão de deploy / estratégia de rollback | `irreversivel` (`gatilhos.tsv`) | `gestor-de-risco` |
| Docker/compose profundo (multi-stage, rede entre containers, cache de build) | `container` (`gatilhos.tsv`) | `especialista-docker` |

Nenhuma delas é candidata a skill nova: todas dependem de julgamento sobre o card concreto
(qual índice, qual branch, qual causa), não de um procedimento genérico que caiba num `SKILL.md`
— é exatamente a fronteira do § *Sua única função* deste engenheiro. `skill-creator` não foi
acionado nesta tarefa por isso.

---

## Regra de fronteira — docs publicados não entra no fluxo de card

**Todo artefato do fluxo vive em `docs/` do repositório**, versionado, com o `{card-id}` no nome:
fluxo, análise, requisitos, plano, `plano.html`, `evidencias.html`, `evidenciashomol.html`,
migrations e documentos de implementação. Isso não é preferência de formato — é o que o
`validador-tecnico` lê, o que sustenta o I4 e o I12, e o que sobra quando a sessão morre.

Um documento do docs publicados **não é rastreável pelo repositório, não passa por gate e não some com o
card**. Por isso:

- **Proibido** usar `docs` para plano, análise, fluxo, evidência ou qualquer entregável de card —
  inclusive "só uma versão para o Gustavo ver". A versão que o Gustavo vê é o HTML validado.
- **Permitido** para documento que nasce fora do fluxo e é do usuário com outras pessoas: status
  consolidado, ata, levantamento aberto, material comentado a várias mãos.
- Em dúvida: se o documento tem `{card-id}`, ele é do repositório. Sem exceção.

## Uso dentro da etapa

Habilidade é **insumo**, igual a especialista: não dispensa etapa, não dispensa gate e não decide
escopo. Invocar `xlsx` não substitui o `especialista-sql` na consulta que gerou a planilha, e
invocar `skill-creator` não substitui o registro de 1 linha do gatilho de classe `skill`.
