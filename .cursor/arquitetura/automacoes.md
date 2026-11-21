# Automações do Cursor — Solides

Referência das automações ativas e MCPs recomendados para o fluxo S1–I15.

> **Scripts de ambiente, URLs e portas** são específicos de cada projeto → ver o perfil `arquitetura/ambiente-local-{projeto}.md` do projeto atual. O nome do script de sync (`dev-sync.sh`) e do script de subida do ambiente varia por repositório.
>
> Patches locais de produto ficam **fora do Brain-Cursor** — ver `alteracoes-ambiente-local-{repo}.md` no repositório de aplicação.

---

## O que já está ativo (`.cursor/settings.json`)

> Esta seção espelha o `settings.json` **real**. Ao alterar o arquivo, atualizar aqui.

### Permissões sem prompt (`permissions.allow`)

| Comando | Etapa beneficiada |
|---------|------------------|
| `git log`, `git diff`, `git status`, `git rev-parse`, `git show` | S1/S3 — histórico e diff (leitura) |
| `find`, `ls`, `cat`, `grep` | S1/S3 — navegar e ler código |
| `curl -sI*`, `curl -s http://127.0.0.1*` | L0 — validar HTTP local |
| `mysql -h127.0.0.1 -P3309*` | S3 — **schema** local (dump congelado; dado ao vivo de homol **não** vem daqui) |
| `git ls-remote*`, `git fetch*` | S1 — o que já existe em qual branch, sem alterar a árvore |
| `cd testes && npm run test:{e2e\|local\|homol}*`, `npm install*`, `npx playwright*` | I7 / I10 / I13 |
| `docker ps*`, `docker logs*`, `docker compose*` | L0 — gerenciar/diagnosticar container |
| `ss -tlnp*` | L0 — conferir portas em escuta |
| **scripts do Brain** — `resumo_testes.sh`, `fase.sh`, `kb.sh`, `frota.sh`, `brain_status.sh`, `ancoras.py`, `cache_validacao.py`, `relatorio_*` | rodam sem prompt em qualquer etapa |

A lista literal e completa é o próprio arquivo — enumerar as ~36 entradas aqui desatualiza na
primeira permissão nova. Para ver a lista viva:

```bash
python3 -c "import json;[print(' ',x) for x in json.load(open('.cursor/settings.json'))['permissions']['allow']]"
```

### Bloqueios (`permissions.deny`)

Materializam o que continua proibido no ADO mesmo com a postagem liberada por pergunta (ver AGENTS.md § *Postagem no ADO*):

| Regra negada | Por quê |
|--------------|---------|
| `mcp__azure-devops__wit_work_item_attachment` | Agente não sobe anexo em card |

### Confirmação (`permissions.ask`) — postagem no ADO

A postagem de comentário/evidência passa por **pergunta a cada vez** ("posto eu ou te entrego o comando?"); o `ask` é a trava estrutural por trás dessa instrução:

| Regra em `ask` | Por quê |
|----------------|---------|
| `Bash(python3 .cursor/scripts/ado_update_comment.py:*)` | Script canônico de postagem (sobe as imagens) — roda só após "sim" explícito |
| `Bash(ADO_PROJECT=* python3 .cursor/scripts/ado_update_comment.py:*)` | Mesma regra, na forma com o prefixo de env que o comando canônico usa |
| `Bash(python3 /var/www/html/{projeto}/.cursor/scripts/ado_update_comment.py:*)` | Mesma regra, com caminho absoluto — **o `{projeto}` é o do repositório atual** |
| `mcp__azure-devops__wit_work_item_comment_write` | Comentário pela tool MCP — mesma pergunta antes |
| Escrita no HubSpot: `mcp__hubspot__hubspot-{batch-create-*,batch-update-objects,create-*,update-*}` (7) e `mcp__legacy_hubspot__{manage_*,import-design-from-url}` (14) | Escrita em serviço externo pede OK (decisão do usuário, 25/09/2026). A leitura continua livre |
| Escrita no Grafana: `mcp__grafana-cloud__{create_*,update_*,delete_*,alerting_manage_*,agento11y_manage_*,add_activity_to_incident,install_plugin,grafana_api_request}` (27) | Mesma regra. As `*_manage_*` também listam, então uma leitura por elas também pede confirmação: custo aceito |
| Postman: **sem** `ask` | A collection no workspace do Luiz faz parte de todo card (etapa PC). A trava é o texto "só no workspace do Luiz" |

### Hooks

**Padrão em todos os projetos:**

| Hook | Gatilho | Ação |
|------|---------|------|
| **`UserPromptSubmit`** | Toda mensagem enviada pelo usuário | Injeta no contexto: lembrete de **idioma pt-BR** + mapa condensado do fluxo (**C0 → L0 → B0 → Fluxo A (S1–S6) / Fluxo B (I1–I15)**), gates de OK explícito e as **regras de economia** (subagente por etapa, testes resumidos, abas) |
| **`PostToolUse`** (matcher `Bash`) | `Bash` contendo `test:e2e`, `test:local` ou `test:homol` | Roda [`hook_pos_testes.py`](../scripts/hook_pos_testes.py): lembra de **não** reproduzir o stdout do Playwright. Em qualquer outro comando não emite nada |
| **`UserPromptSubmit`** + **`PostToolUse`** | Toda mensagem e todo `Bash` | Roda [`hook_contexto.py`](../scripts/hook_contexto.py) — o **medidor de contexto**: lê o transcript da sessão, calcula o contexto real e obriga o agente a pedir `/compact` (≥130% do orçamento) ou `/clear` (≥200%). Por sessão; fala só quando a faixa sobe |
| **`PostToolUse`** (matcher `Edit\|Write\|MultiEdit\|NotebookEdit`) + **`SessionStart`** + **`Stop`** | Editar/escrever arquivo, abrir sessão, encerrar turno | Roda [`hook_dominio.py`](../scripts/hook_dominio.py) — o **ciclo de aprendizado**: editou arquivo citado por um mapa `dominio-*`, o mapa entra em `.cursor/cache/dominios-sujos`; `SessionStart` avisa antes da primeira palavra; o `Stop` desta peça **não chega ao modelo** (Stop só entrega `decision:block`; `additionalContext` é descartado) — a cobrança efetiva de destilação é do `hook_card.py` |
| **`UserPromptSubmit`** + **`Stop`** | Toda mensagem, fim de turno | Roda [`hook_card.py`](../scripts/hook_card.py) — **card da sessão**: mensagem que cita outro card manda o agente alertar (aba única por card, obrigatória) e cobra a destilação do card anterior; no `Stop`, card em etapa de encerramento sem `docs/destilacoes/<card>.md` recebe `decision:block` uma vez |

| **`PostToolUse`** (matchers `Bash`, `Edit\|Write\|MultiEdit\|NotebookEdit`, `Agent`) + **`Stop`** | Artefato produzido ou subagente chamado | Roda [`hook_gatilhos.py`](../scripts/hook_gatilhos.py) — o **gatilho por artefato**: casa caminho, conteúdo escrito ou comando contra [`frota/gatilhos.tsv`](../frota/gatilhos.tsv) e cobra o especialista da classe **antes** de o artefato sair. Só artefato dispara (conteúdo de documento só pela forma inequívoca de SQL/DDL; comando casado no início). Observa as chamadas `Agent` e fica em silêncio se aquele especialista já foi consultado; fala uma vez por especialista por sessão, no máximo 3 por mensagem |

### Medidor de contexto — como funciona

O gargalo medido não é duplicação em arquivo: é a **conversa acumulada** — cada turno relê o
contexto inteiro como cache read. Depender de o agente lembrar de pedir `/compact` não funcionou,
então a checagem virou automática:

1. O agente **declara** etapa e card ao entrar na etapa — `.cursor/scripts/fase.sh I7 167697` —
   gravados **por sessão** (`.cursor/cache/sessao/<session_id>.json`). O **orçamento é o mesmo
   em todas as etapas** (valor em `hook_card.ORCAMENTO`).
2. A cada mensagem e a cada `Bash`, o hook lê a **cauda** do `transcript_path`, soma
   `input + cache_read + cache_creation` da última resposta e compara com o orçamento.
3. Só fala quando a **faixa sobe** (gravada por sessão). Acima de 85% avisa; acima de 130% exige `/compact` na primeira linha da resposta; acima de
   200% manda parar, resumir o estado em 3–5 linhas e pedir `/clear` **no corte de exceção do
   bloco** — a aba do card é única, e o corte é exceção cobrada pelo medidor, não rotina.

Sem fase declarada usa o mesmo padrão e diz que a fase não foi declarada — **não adivinha
a etapa pelo texto da conversa**, porque um palpite errado gera rótulo errado (a primeira versão
tentava isso e classificou uma sessão de manutenção de docs como “Aba 5 · I12–I15”).

> **Os números vivem no código, não aqui.** Quem manda são `ORCAMENTO` e `BLOCOS` em
> [`hook_card.py`](../scripts/hook_card.py) — lidos por `fase.sh` e `hook_contexto.py`. Os blocos e seus cortes de exceção estão em
> [fluxo-completo.md](../fluxo-completo.md) § *Aba única por card e orçamento de contexto* —
> **fonte única**. Valor repetido em prosa desatualiza e passa a contradizer o medidor.

> **Nem o hook nem o agente executam `/compact` ou `/clear`** — são comandos do cliente. A
> automação garante o *pedido* no momento certo, com o número medido; a execução é do usuário.

O conteúdo injetado é a fonte da verdade do processo: os documentos em `.cursor/` refletem o que esse hook declara — ver [fluxo-completo.md](../fluxo-completo.md) (§ *B0 — Bifurcação* e § *Aba única por card e orçamento de contexto*).

> **Orçamento do hook `UserPromptSubmit`:** ele é reinjetado **a cada mensagem** do usuário, então cada token nele é pago dezenas de vezes por sessão. Manter **abaixo de ~800 tokens** e apontar para os documentos em vez de duplicá-los. Medir depois de editar:
>
> ```bash
> bash -c "$(python3 -c "import json;print(json.load(open('.cursor/settings.json'))['hooks']['UserPromptSubmit'][0]['hooks'][0]['command'])")" \
>   | python3 -c "import json,sys; t=json.load(sys.stdin)['hookSpecificOutput']['additionalContext']; print(len(t)//4, 'tokens aprox')"
> ```

**Opcionais, por projeto** — existem apenas onde o repositório tem patches locais e/ou script de sync (comandos e caminhos no perfil `arquitetura/ambiente-local-{projeto}.md`):

| Hook | Gatilho | Ação | Onde faz sentido |
|------|---------|------|------------------|
| **`PreToolUse`** (matcher `Bash`) | `Bash` contendo `git commit` | Bloqueia o commit se os **patches locais** do projeto estiverem ativos; instrui a rodar o comando de restauração antes | Projetos com patches locais para rodar em dev |
| **`PostToolUse`** (matcher `Edit\|Write`) | Qualquer `Edit`/`Write` com o container no ar | Roda o script de sync do projeto (ex.: `./docker/dev-sync.sh`) — sem precisar lembrar | Projetos cujo código **não** é bind mount |

> Onde esses dois hooks **não** estão configurados, os passos são **manuais**: sincronizar após editar (script/`docker cp`) e reverter os patches locais antes de commit/PR — ver o perfil do projeto.

> **Manutenção do hook:** o comando é uma **única linha JSON** com todas as aspas internas escapadas (`\"`). Uma aspa crua invalida o arquivo e o Cursor **descarta todo o settings.json em silêncio** — permissões e hook param de valer. Depois de editar, validar com:
>
> ```bash
> python3 -c "import json; json.load(open('.cursor/settings.json')); print('ok')"
> ```

### Overrides pessoais (`.cursor/settings.local.json`)

**Não é padronizado entre projetos** — cada repositório tem o seu, com caminhos próprios:

| Item | Conteúdo típico |
|------|-----------------|
| `permissions.allow` | complemento local do `settings.json` — `Write`/`Edit` em `.cursor/scripts/**`, `python3` no diretório de scratchpad. **Nome de tool MCP aqui envelhece:** o `allow` versionado é a fonte |
| `permissions.additionalDirectories` | `/var/www/html/{projeto}` |
| `enabledMcpjsonServers` | `playwright`, `azure-devops` |

---

## MCPs

> **Como funciona:** Como o Cursor é usado como extensão do VSCode (sem CLI), os MCPs são configurados via arquivo `.mcp.json` na raiz do projeto. O Cursor carrega este arquivo automaticamente ao abrir o workspace. **Não use `cursor mcp add`** — esse comando exige o CLI instalado.

**Dois escopos, e o inventário não é copiado aqui.** Além do `.mcp.json` do projeto (gitignored,
vale só neste repo), o Cursor lê `mcpServers` de `~/.cursor/mcp.json` — **escopo de usuário**, vale
em todos os repos. Servidor declarado nos dois escopos: o de projeto vence e o outro fica morto.

```bash
.cursor/scripts/mcp.sh          # inventário + saúde + quem da frota alcança cada servidor
```

Três regras que valem mais que a lista:

1. **MCP quebrado é pior que MCP ausente.** O servidor injeta o nome das tools na sessão, o agente
   confia que existe e descobre o contrário no meio da etapa. `mcp.sh checar` mede isso de fora,
   sem gastar contexto chamando tool.
2. **Tool não declarada no frontmatter não chega ao subagente.** Servidor de pé não basta: se o
   agente não lista `mcp__<servidor>__<tool>`, ele só tem `Bash`. Foi o que aconteceu com o MCP
   GitLab — `/cicd` prometia ler o log do job real e o agente não alcançava a tool.
3. **Escrita fora do agente.** ADO e GitLab são **leitura**; o `deny` do `settings.json` e o
   `GITLAB_READ_ONLY_MODE=true` materializam isso. Quem comenta em card ou em MR é o usuário.

**Sequential Thinking:** recomendação **revogada**. O raciocínio estruturado é nativo do modelo
hoje; o servidor só acrescentaria schema de tool ao contexto sem entregar nada novo.

### 1. Playwright MCP — prioridade alta ✓ configurado

**O que resolve:** Captura de screenshot do relatório E2E (I9) e prints das telas locais (I10/I11) e homol (I13/I14) — hoje feito manualmente.

**Pacote:** `@playwright/mcp@latest` (v0.0.77+)

**Como vai ajudar:**
- I9: captura automática do `playwright-report/index.html` como PNG para `docs/evidencias/assets/`
- I10/I13: navega URL local/homol, preenche campos de teste e tira prints diretamente como evidência L01–LN / U01–UN
- Elimina o passo manual de "tire um screenshot e salve como `{card-id}-qN.png`"

> **Restrição de custo — usar só onde é necessário.** Cada `browser_snapshot` / `browser_evaluate` devolve payloads grandes ao contexto; o MCP Playwright responde por parcela relevante do gasto. Permitido em **I7, I10, I13 e I14** (captura de evidência). **Proibido** em C0, L0, S1–S6, I1–I4 e nas demais etapas I — para conferir se uma URL responde, usar `curl -sI` (já permitido), que custa uma fração. **Não existe chave em `settings.json` para ligar/desligar MCP por fase** (`enabledMcpServers` / `disableMcpFor` não existem) — o cumprimento é do agente, declarado em [otimizacao-custos.md](../otimizacao-custos.md) § *Playwright* e na lista de proibições do [fluxo-completo.md](../fluxo-completo.md).

---

### 2. MCP Azure DevOps — prioridade média ✓ configurado

**O que resolve:** O agente **lê** o card pelo MCP (número, título, ACs, comentários, `System.TeamProject`) sem abrir o browser. A **postagem** do HTML de evidências usa o script `.cursor/scripts/ado_update_comment.py` — o contexto principal pergunta antes (posto eu ou entrego o comando?) e só posta com "sim" (ver AGENTS.md § *Postagem no ADO*).

**Pacote:** `@azure-devops/mcp@latest` (v2.7.0+)

**Configurar antes de usar** — editar `.mcp.json` na raiz com os valores reais:
```json
"azure-devops": {
  "command": "npx",
  "args": ["-y", "@azure-devops/mcp@latest", "solidestech", "--authentication", "envvar"],
  "env": {
    "AZURE_DEVOPS_EXT_PAT": "SEU_PAT_AQUI",   ← gerar no ADO
    "ADO_MCP_AUTH_TOKEN": "SEU_PAT_AQUI"       ← mesmo PAT
  }
}
```

**Gerar PAT:** `dev.azure.com → User Settings → Personal Access Tokens` · Escopo mínimo: Work Items (Read & Write)

**Como vai ajudar:**
- Buscar detalhes do card (número, título, ACs) sem copiar manualmente
- Consultar histórico e comentários do work item durante S1
- Obter o GUID do projeto (`System.TeamProject`) para montar o comando de postagem

> **Escrita no ADO:** só comentário, e só após perguntar e receber "sim" (`ask`). Anexo avulso, estado, campos e links continuam no `deny`.
>
> **Nota:** Imagens embutidas são resolvidas pelo script `ado_update_comment.py` quando executado — pelo agente após o "sim" ou pelo usuário (upload do PNG como anexo + `src` com o GUID do projeto). LibreOffice/Word não é necessário.

---

### 3. MCP GitLab — escopo de **usuário** (`~/.cursor/mcp.json`), não do projeto

**O que resolve:** pipeline e MR **reais** — qual job falhou e com que mensagem, o diff que o
revisor humano vê, o que já está em qual branch. Roda com `GITLAB_READ_ONLY_MODE=true`: o agente
lê, não retenta job nem escreve em MR.

**Quem alcança:** `especialista-git` (branch, MR, pipeline e job),
`revisor-codigo` (diff de MR). As tools são diferidas — o agente carrega com `ToolSearch` antes de
chamar. Para uma pergunta só sobre branch, `git ls-remote`/`git fetch` custam menos.

### 4. MCP Zendesk — **descontinuado** (21/08/2026)

Estava declarado no escopo de usuário e nunca foi configurado (toda tool respondia
`Zendesk not configured`). **Decisão do usuário: não vai subir e não será usado.** A declaração foi
removida de `~/.cursor/mcp.json` e as 19 entradas de `allow`/`deny` saíram do `settings.json`.

Consequência a assumir, não a esquecer: **ticket de cliente entra no card por copiar e colar**. O
número do ticket continua no `{card-id}` das evidências — isso é do padrão de nomenclatura, não do MCP.

Sobra uma declaração fora deste repositório: `partners/.mcp.json` ainda lista `zendesk`. Remover
depende de permissão para alterar outro repositório (AGENTS.md § *Regras de escopo*).

---

## Resumo — impacto por etapa

| Etapa | Antes | Depois |
|-------|-------|--------|
| Toda mensagem | Depender da memória do fluxo | Hook `UserPromptSubmit` reinjeta idioma + C0/L0/B0 + gates + abas |
| B0 — bifurcação | Presumir se é sustentação ou implementação | Pergunta explícita, com confirmação (Y/n) para pular S1–S6 |
| I7/I10/I13 — prints | Screenshot manual → salvar PNG | Playwright MCP captura direto |
| C0 — ler card ADO | Abrir browser, copiar ACs | MCP ADO consulta direto (`mcp__azure-devops__wit_work_item`) |
| Pós-S6a/I11/I15 | Risco de o agente postar no card sem perguntar | `ask` no script e no comentário via MCP; `deny` no resto da escrita |
| Permissões | Popup a cada comando de leitura/teste | Pré-aprovados em `allow`, sem interrupção |
| I5 — editar código *(onde há `PostToolUse`)* | Editar → lembrar de rodar o sync | Editar → sync automático pelo hook |
| Pré-commit *(onde há `PreToolUse`)* | Lembrar do comando de restauração | Hook bloqueia commit com patches locais ativos |

---

## O que pode não estar automatizado (conferir no projeto atual)

Os hooks `PostToolUse` (sync) e `PreToolUse` (guarda de commit) são **opcionais** e não existem em todos os repositórios. Conferir no `settings.json` do projeto atual — onde faltarem, os passos são **manuais**:

- **Sync após editar:** se o código não for bind mount, rodar o script de sync / `docker cp` conforme o perfil `arquitetura/ambiente-local-{projeto}.md`.
- **Antes de commit/PR:** reverter os patches locais. Neste repositório o comando é
  reverter patches locais conforme [alteracoes-ambiente-local-projeto.md](alteracoes-ambiente-local-projeto.md)
  § *Patches PHP locais*. É **gate do AGENTS.md**, não sugestão.

Para saber o que está ativo agora:

```bash
python3 -c "import json; d=json.load(open('.cursor/settings.json')); print(list(d.get('hooks',{}).keys()))"
```

---

## Subagentes declarados (`.cursor/agents/`)

Cada arquivo em `agents/` declara um subagente com **modelo fixo** — o `Agent` o invoca por
`subagent_type`. O catálogo **não é listado aqui**: `.cursor/scripts/frota.sh listar` o lê do
disco, `frota.sh modelos` mostra a calibragem e `frota.sh lint` confere a integridade. A tabela
etapa → agente → comando → modelo é a do **AGENTS.md** § *Frota* (sempre carregado); política de
custo em [otimizacao-custos.md](../otimizacao-custos.md), regras de uso em
[frota/README.md](../frota/README.md).

O que importa nesta página é a **consequência de automação**: a validação de etapa tem agente
próprio e modelo próprio — `validador-leve` (Haiku) em S2/plano curto, `validador-tecnico` (Opus) em
S4/S6a-val/I6/I11/I15. `general-purpose` **não** serve para validar etapa: ele herda o modelo da
sessão (Opus) mesmo quando a validação é estrutural, e recebe todo o contexto da conversa.

---

## Scripts de apoio (`.cursor/scripts/`)

| Script | Para que serve | Quando roda |
|--------|----------------|-------------|
| [`resumo_testes.sh`](../scripts/resumo_testes.sh) | Roda `test:{e2e\|local\|homol}` e devolve só a tabela de cenários + N/N; log completo em `.cursor/cache/logs-testes/` | I7, I10, I13 |
| [`cache_validacao.py`](../scripts/cache_validacao.py) | Cache de validações por `sha256(etapa+conteúdo)`, TTL 1h; evita repagar subagente em documento inalterado | Antes/depois de cada validação |
| [`relatorio_custos.py`](../scripts/relatorio_custos.py) | Custo estimado por modelo, subagente, Playwright e higiene de contexto, a partir dos transcripts locais | Revisão de sexta-feira 12:00 · sob demanda |
| [`relatorio_semanal.sh`](../scripts/relatorio_semanal.sh) | Wrapper do anterior: grava em `.cursor/cache/relatorios/` e imprime o resumo — é o que vai no cron do SO | Agendado (crontab / systemd timer) |
| [`hook_pos_testes.py`](../scripts/hook_pos_testes.py) | Corpo do hook `PostToolUse` de testes | Automático |
| [`hook_contexto.py`](../scripts/hook_contexto.py) | Medidor de contexto — exige `/compact` ou `/clear` quando estoura o orçamento da fase | Automático (toda mensagem e todo `Bash`) |
| [`fase.sh`](../scripts/fase.sh) | Declara a etapa atual (`fase.sh I7`), calibrando o orçamento do medidor | Ao entrar em cada etapa |
| [`hook_dominio.py`](../scripts/hook_dominio.py) | Marca mapa de domínio como sujo, avisa no `SessionStart` e cobra `/destilar` no `Stop` | Automático (`Edit`/`Write`, abertura de sessão, fim de turno) |
| [`ado_update_comment.py`](../scripts/ado_update_comment.py) | Postagem de evidências no card — pelo agente após "sim" ou pelo usuário; em `ask` | Pós-S6a / Pós-I11 / Pós-I15 |

Os scripts de **conhecimento e frota** (`kb.sh`, `ancoras.py`, `frota.sh`, `brain_status.sh`,
`gerar_plugin.py`) estão na tabela do [`.cursor/README.md`](../README.md) §
*Scripts do Brain* — as duas listas são complementares, não cópias.

`.cursor/cache/` (cache de validação e logs de teste) é transitório e não versionado.

---

## Revisão de custos — sexta-feira 12:00

Job recorrente registrado na sessão do Cursor (`CronCreate`) que executa:

```bash
python3 .cursor/scripts/relatorio_custos.py --dias 30
```

e apresenta o resultado no chat, comparado aos alvos de
[otimizacao-custos.md](../otimizacao-custos.md) § *Gargalos medidos e alvos*.

> **Limitação:** jobs de `CronCreate` vivem **apenas na sessão em que foram criados** — não são
> persistidos em disco, somem quando a sessão do Cursor é encerrada, e jobs recorrentes
> expiram após **7 dias**. Serve para a sessão corrente; não serve como agenda permanente.

### Agenda permanente — `relatorio_semanal.sh` + cron do SO

[`relatorio_semanal.sh`](../scripts/relatorio_semanal.sh) roda o relatório, grava em
`.cursor/cache/relatorios/custos-AAAA-MM-DD.md` (mantendo os 12 mais recentes) e imprime o
resumo. É o que deve ser agendado fora do Cursor.

**Opção A — crontab do usuário** (mais simples):

```bash
crontab -e
# sexta 12:00
0 12 * * 5 <repo-de-produto>/.cursor/scripts/relatorio_semanal.sh >> /tmp/relatorio-custos-cron.log 2>&1
```

**Opção B — systemd user timer** (sobrevive a reboot, tem histórico de execução):

```ini
# ~/.config/systemd/user/custos-cursor.service
[Service]
Type=oneshot
ExecStart=<repo-de-produto>/.cursor/scripts/relatorio_semanal.sh

# ~/.config/systemd/user/custos-cursor.timer
[Timer]
OnCalendar=Fri *-*-* 12:00:00
Persistent=true
[Install]
WantedBy=timers.target
```

```bash
systemctl --user enable --now custos-cursor.timer
loginctl enable-linger "$USER"   # roda sem sessão gráfica aberta
systemctl --user list-timers custos-cursor.timer
```

`Persistent=true` recupera a execução se a máquina estiver desligada no horário — o `crontab`
simples não faz isso.

> **Agente agendado na nuvem não serve para este caso.** O relatório lê os transcripts **locais**
> em `~/.cursor/projects/`; um agente rodando fora desta máquina não enxerga esses arquivos.
> Agendamento em nuvem só faria sentido se as métricas viessem da API de billing.

Rodar sob demanda continua valendo: `.cursor/scripts/relatorio_semanal.sh 7`.

---

## Manutenção

- Ao adicionar novo MCP: registrar aqui com comando de instalação e etapa beneficiada.
- Ao alterar `settings.json` (permissões ou hooks): atualizar as tabelas de § *O que já está ativo* e **validar o JSON** (`python3 -c "import json; json.load(open('.cursor/settings.json'))"`).
- Ao alterar o texto do hook `UserPromptSubmit`: refletir a mudança em [fluxo-completo.md](../fluxo-completo.md), AGENTS.md, na skill `skills/regras-de-trabalho/` e nos guias de `sustentacao/` e `implementacao/` — os documentos devem espelhar o hook. **Medir o tamanho** depois de editar: alvo < 800 tokens.
- Ao mudar preços de modelo: atualizar `PRECOS` em [`relatorio_custos.py`](../scripts/relatorio_custos.py).
- MCPs ficam em `.mcp.json` na raiz do projeto (gitignored) — padrão do Cursor via VSCode; documentar para onboarding de novo dev.
