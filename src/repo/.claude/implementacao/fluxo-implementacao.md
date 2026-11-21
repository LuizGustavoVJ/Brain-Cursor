# Implementação — fluxo de código

Ciclo **obrigatório** sempre que houver alteração de código. Roda na **mesma aba do card**: **ABA ÚNICA POR CARD é o padrão** — o contexto principal só orquestra (guarda caminho do artefato + veredito de 15 linhas). Abrir aba é **exceção cobrada pelo medidor**, não rotina.

**Visão geral em uma página:** [fluxo-completo.md](../fluxo-completo.md).

> **Fase 3 (25/09/2026) — prevalece [`fluxo-completo.md`](../fluxo-completo.md) § *Trilhas*:** o I2 foi fundido no
> **I2-val** (uma validação do plano), existe a **trilha curta** (sem `plano.html`, I6 e E2E separados)
> e toda validação tem **teto de 3 rodadas**. Onde este guia divergir, vale o `fluxo-completo.md`.

## Como este ciclo é acionado (duas entradas)

| Entrada | Condição | Pré-requisito |
|---------|----------|---------------|
| **S6b** — handoff da sustentação | **S5 = implementação necessária** | Fluxo e análise **aprovados** conforme [`.claude/sustentacao/fluxo-por-card.md`](../sustentacao/fluxo-por-card.md) (**S1–S6**) |
| **B0 direto** — usuário declara implementação | Usuário responde **“é implementação”** na bifurcação **e** confirma *“Confirma que pula S1–S6 e vai direto para I1–I15? (Y/n)”* | **L0 ok** (app + BD + URL no chat) + **(Y/n)** registrado no chat |

Em ambas as entradas, I1–I15 seguem na **mesma aba do card** (ABA ÚNICA POR CARD é o padrão): cada etapa vai para o agente dela e o principal guarda apenas caminho + veredito de 15 linhas. Sem o **(Y/n)** explícito, é **proibido** entrar aqui pulando S1–S6.

Detalhes: [fluxo-completo.md](../fluxo-completo.md) § *B0 — Bifurcação*.

---

## Relação sustentação × implementação

| Fase | Escopo | Pasta de guias |
|------|--------|----------------|
| **Sustentação** | Entender, mapear, diagnosticar, decidir | `.claude/sustentacao/` |
| **Implementação** | Plano, código, validação, E2E, local URL, homol remoto, evidências | `.claude/implementacao/` |

---

## Ordem de entrega

| Etapa | Entrega | Pasta / artefato | Modo |
|-------|---------|------------------|------|
| I1 | Documento de **implementação** (plano) | `docs/implementacoes/plano/` | Plan |
| I1-rev | **Revisões de especialistas** — todo gatilho disparado, fan-out na mesma mensagem | `## Revisões de especialistas` no **`_processo-revisoes.md` interno** (não no plano — regras.md § 11) | Plan |
| I2-html | **`plano.html`** (`escritor-evidencias`, **sonnet**) — só trilha completa | `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html` | Plan |
| I2-val | **Validação única do plano** — completa: `validador-tecnico` sobre plano `.md` + `plano.html`; curta: `validador-leve` sobre o plano curto — **gate do I4**, teto de 3 rodadas | `## Validação do plano` em `plano/impl-*.md` | Plan |
| Pós-I2-val | **Entrega do `plano.html`** — caminho + GUID + **comando pronto**; **pergunta antes: posto eu ou entrego o comando?** | — | Plan |
| I3 | Apresentação no chat + caminho do plano `.md` e do `plano.html` | — | Plan |
| I4 | **OK explícito** do usuário para executar código | — | Plan |
| I5 | **Execução do código** + doc **executada** | Repositório + `docs/implementacoes/executada/impl-*.md` | **Agent** |
| I6 | **Validação da implementação** (subagente) | `## Validação do código` em `executada/` | **Agent** |
| I6-rev | **Revisões de especialistas sobre o diff** — obrigatória se houve segurança em I1-rev | `## Revisões de especialistas (código)` no **`_processo-revisoes.md` interno** (regras.md § 11) | **Agent** |
| I7 | **Testes E2E** (`testes/E2E/`) — 100% pass | `testes/E2E/specs/{card-id}/` | **Agent** |
| I8 | **Documento testes E2E** | `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/testes-e2e.md` | **Agent** |
| I9 | **HTML de evidências** — implementação + bloco **E2E** (print + tabela) | `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html` | **Agent** |
| I10 | **Testes local URL** — 100% pass | `testes/local/specs/{card-id}/`, `npm run test:local` | **Agent** |
| I11 | **Doc local + HTML local** (subagente) | `testes-local.md` + bloco **local** L01–LN + validação **E2E** em `evidencias.html` | **Agent** |
| I12 | **Gate deploy homol** | Sinal no chat; **OK explícito** do usuário | Plan/Agent |
| I13 | **Testes homol remoto** — 100% pass | `testes/homol/specs/{card-id}/`, `npm run test:homol` | **Agent** |
| I14 | **HTML homol** | `evidenciashomol.html` (E2E print+tabela + homol U01–UN) | **Agent** |
| I15 | **Validação HTML homol** (subagente) | `## Validação do HTML homol` em `executada/` | **Agent** |
| Pós-I15 | **Entrega das evidências homol** *(só se houve dev)* | Caminho do `evidenciashomol.html` + **comando pronto** do script `.claude/scripts/ado_update_comment.py`, destinado ao **card de DESENVOLVIMENTO** — **pergunta antes: posto eu ou entrego o comando?** | **Agent** |

**Antes de I5:** ler por completo a skill [`regras-de-trabalho`](../skills/regras-de-trabalho/SKILL.md) (SKILL.md **e** `escopo-e-permissoes.md`) — limites de escopo são obrigatórios; não iniciar código sem isso.

**Checklist integral (S1–S5 + I1–I15):** [fluxo-completo.md](../fluxo-completo.md#checklist-rápido--antes-de-avançar).

---

## Contexto e abas (I1–I15) — aba única por card

**ABA ÚNICA POR CARD é o padrão.** I1–I15 rodam na mesma aba porque **o contexto principal só orquestra**: chama o agente da etapa, recebe **caminho do artefato + veredito de 15 linhas** e passa adiante. Conteúdo de documento **nunca** volta para o principal — é isso que mantém a aba única viável.

**Abrir aba é exceção cobrada pelo medidor**, não rotina: só quando o medidor apontar estouro e o usuário decidir. `/compact` e `/clear` são comandos **do usuário** — o agente pede com o número medido e para.

Orçamento de contexto: **fonte única** em [fluxo-completo.md](../fluxo-completo.md) § *Aba única por card e orçamento de contexto* — quem mede e cobra são `.claude/scripts/fase.sh` e o hook `hook_contexto.py`. Número repetido aqui desatualiza e contradiz o medidor.

---

## Ciclo I1-rev — revisões de especialistas no plano

**Após I1, antes de I2-val.** O gatilho é por **artefato**, não por etapa: cada trecho do plano que criou uma migration, uma rota, um cálculo de dinheiro, um segredo ou uma tela já chamou o especialista da classe quando foi escrito. O I1-rev **confere** que todos foram respondidos e registrados. Fan-out **na mesma mensagem** (paralelo), **um especialista = uma pergunta**, **sem teto**.

**Tabela de gatilhos: uma fonte só** — [`frota/gatilhos.tsv`](../frota/gatilhos.tsv), via `.claude/scripts/frota.sh gatilhos`. Aqui não há cópia; mecanismo e limites em [`frota/gatilhos.md`](../frota/gatilhos.md).

Retorno fixo de cada especialista: `Veredito: Bloqueante|Ajustar|OK` + até 3 pontos com `arquivo:linha` + o que muda. Registro obrigatório em **`## Revisões de especialistas`** no **`_processo-revisoes.md` interno** — nunca no plano `.md` nem no `plano.html`, que não citam agente da frota (regras.md § 11) — (Especialista · Veredito · Ponto · Onde foi acatado). Gatilho que **não** disparou entra em **uma** linha: *“Gatilhos avaliados e não disparados: …”*.

O plano também fecha os **8 itens** de **`## Conformidade e segurança`** — nenhum em branco. Conteúdo: [documento-implementacao.md](documento-implementacao.md#conteúdo-mínimo-plano--detalhado).

---

## Trilha curta — plano curto

Card sem critério de completa (`fluxo-completo.md` § *Trilhas*): I1 produz **plano curto** (problema,
arquivos, cenários de teste local, rollback, fora de escopo) → **I2-val** com `validador-leve` →
**I4** → I5 → I10 → I11 (`validador-tecnico` confere código vs plano + `evidencias.html` numa rodada)
→ I12 → I13 → PC → I14 → I15 → DEST. Sem `plano.html`, sem I6/I6-rev/I7–I9 separados.

O antigo **I2** (pré-conferência estrutural do plano `.md`) foi **fundido no I2-val**.

---

## Ciclo I2-html — `plano.html`

**Somente na trilha completa, após I1-rev registrada.** Subagente `escritor-evidencias` (**sonnet**) produz:

`docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html`

**13 seções em ordem fixa**; seção não aplicável recebe **“N/A + motivo”** e **nunca** é apagada. Antes/depois é **tabela lado a lado + fluxo numerado** (ADO-safe) — mermaid só no `.md`. **Sem PNG e sem Playwright em I2-html.** Guia canônico: [documento-plano-html.md](documento-plano-html.md).

---

## Ciclo I2-val — validação do `plano.html` (gate do I4)

**Somente após I2-html.** Subagente `validador-tecnico` (**Opus**) valida o `plano.html` contra o plano `.md`, as revisões de I1-rev e o checklist de conformidade.

```
plano.html → validador-tecnico (rodada N) → Status: Aprovado? → Pós-I2-val → I3 → I4 → I5
                       ↑_________________________________|
                          (corrigir plano.html / plano .md e revalidar)
```

**Critério de saída:** `Status: Aprovado` em **`## Validação do plano.html`** no plano `.md`. Critérios de recusa: [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i2-val--planohtml).

---

## Pós-I2-val — entrega do `plano.html` (pergunta antes de postar no ADO)

**Executado após I2-val aprovada**, antes de I3/I4. O agente pergunta *"Posto eu o `<arquivo>` no card `<n>`, ou te entrego o comando?"* e posta só com "sim" explícito (por postagem); senão entrega o comando. Entrega no chat:

1. **Caminho** do `plano.html` aprovado.
2. **GUID do projeto** do card (campo `System.TeamProject`, obtido no C0).
3. **Comando pronto:**

```bash
ADO_PROJECT=<GUID-do-projeto> python3 .claude/scripts/ado_update_comment.py <plano.html> <work_item_id> [comment_id]
```

Mesmas regras da Pós-I11 (`<body>` sem atributos, `comment_id` para atualizar). Detalhe: [documento-plano-html.md](documento-plano-html.md#entrega-em-pós-i2-val-o-usuário-posta).

---

## Ciclo I6 — validação da implementação (código)

**Após I5 concluída**, subagente `validador-tecnico` compara **diff/código** com o plano aprovado e critérios de aceite.

Detalhes: [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i6).

```
I5 código entregue
        ↓
Subagente valida implementação (rodada N)
        ↓
    ┌─── Aprovado (100%)? ─── SIM ──→ I7 (testes E2E)
    │
    NÃO (Recusado / ressalvas bloqueantes)
        ↓
Agente corrige o código
        ↓
Atualiza ## Validação do código em executada/
        ↓
Subagente valida NOVAMENTE (rodada N+1)
        ↓
(repete até Status: Aprovado pleno)
```

**Critério de saída:** `Status: Aprovado` em `## Validação do código` — **sem** encerrar com ressalvas pendentes.

---

## Ciclo I6-rev — revisões de especialistas sobre o diff

**Dentro do I6**, antes de fechá-lo. Os gatilhos do **diff** dispararam durante o I5, arquivo a arquivo — aqui você confere que foram respondidos. Tabela: [`frota/gatilhos.tsv`](../frota/gatilhos.tsv) (`frota.sh gatilhos`), sem cópia neste arquivo.

Dois gatilhos do I6-rev **não** são detectáveis por arquivo e você declara na mão:

| Gatilho declarado | Especialista |
|-----------------|--------------|
| houve revisão de segurança em I1-rev | `especialista-seguranca` — **obrigatório** (o diff cumpre o que o plano decidiu?) |
| diff > 200 linhas ou 5+ arquivos no mesmo passo (`git diff --stat`) | `revisor-codigo` |

Fan-out **na mesma mensagem**; retorno fixo `Veredito: Bloqueante|Ajustar|OK` + até 3 pontos com `arquivo:linha`. Registro em **`## Revisões de especialistas (código)`** no **`_processo-revisoes.md` interno** (não em `executada/` nem em documento entregável — regras.md § 11), com **onde foi acatado**. Gatilhos não disparados em uma linha. O checklist de conformidade do plano é **reconferido aqui**.

**Proibido fechar o I6 sem I6-rev quando houve revisão de segurança em I1-rev.**

---

## Ciclo I7–I9 — testes E2E e HTML (primeira parte)

**Somente após I6 aprovada.**

1. **I7:** executar **`npm run test:e2e`** — [testes-e2e.md](testes-e2e.md); **100% pass** obrigatório.
2. Se falhar: corrigir código → **revalidar I6** se mudança substancial → reexecutar I7.
3. **I8:** produzir [documento-testes.md](documento-testes.md) (bloco E2E).
4. **I9:** atualizar `evidencias.html` — implementação + critérios de aceite + **testes E2E** (print Playwright + tabela “Detalhamento dos cenários” — [documento-evidencias-html.md](documento-evidencias-html.md)). **Não encerrar o card** — falta I10.

```
I6 → I7 (E2E 100%) → I8 (testes-e2e.md) → I9 (evidencias.html E2E) → I10 (local)
```

---

## Ciclo I10 — testes local URL (obrigatório)

**Somente após I9** (E2E **completo** no HTML: print + tabela detalhada).

Ordem fixa — detalhes em [testes-local.md](testes-local.md):

```
I9 concluída
        ↓
1. Confirmar app local no ar (URL L0)
        ↓
2. npm run test:local — **100% pass** (tela com dados de teste preenchidos + HTTP **200** por cenário)
        ↓
3. Gerar evidências L01–LN em docs/evidencias/assets/
        ↓
I11 — testes-local.md + bloco local no evidencias.html + subagente
```

| Passo | Comando / artefato |
|-------|-------------------|
| URL alvo | URL local (L0) — ver o perfil `arquitetura/ambiente-local-{projeto}.md` |
| Testes | `cd testes && npm run test:local` |
| Specs | `testes/local/specs/{card-id}/` |
| Evidências visuais | `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/*-local-*.png` |

**Critério de saída I10:** 100% pass local na URL L0. **Não encerrar o card** — falta I11.

---

## Ciclo I11 — documentação local + validação HTML local (subagente)

**Somente após I10 concluída.**

1. Produzir `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/testes-local.md` — [documento-testes.md](documento-testes.md).
2. Atualizar `evidencias.html` — bloco **local** L01–LN (figuras, HTTP 200, matriz local).
3. Subagente valida bloco local **e bloco E2E (I9)** vs testes I10/I7 e plano.

Detalhes: [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i11).

```
I10 concluída
        ↓
Subagente valida bloco local em evidencias.html (rodada N)
        ↓
    ┌─── Status: Aprovado (100%)? ─── SIM ──→ Pós-I11: entregar HTML + comando de postagem ──→ I12 (gate deploy homol)
    │
    NÃO
        ↓
Agente corrige HTML / testes / testes-local.md
        ↓
Subagente revalida (rodada N+1)
```

**Critério de saída I11:** `Status: Aprovado` em `## Validação do HTML local` em **`executada/`**.

**Não incluir** bloco homol em `evidencias.html`.

---

## Pós-I11 — Entrega das evidências (pergunta antes de postar no ADO)

**Executado após I11 aprovada**, antes de apresentar o gate I12.

O agente pergunta *"Posto eu o `<arquivo>` no card `<n>`, ou te entrego o comando?"* e posta só com "sim" explícito (por postagem); senão entrega o comando pronto de postagem.

### O que o agente entrega no chat (e usa ao postar, após o "sim")

1. **Caminho** do `evidencias.html` validado em I11.
2. **GUID do projeto** do card (campo `System.TeamProject`, já obtido no C0).
3. **Comando pronto** para copiar e rodar:

```bash
ADO_PROJECT=<GUID-do-projeto> python3 .claude/scripts/ado_update_comment.py <html_path> <work_item_id> [comment_id]
```

O script resolve tudo numa única chamada:

1. Inlina o CSS do `evidencias.html` (o comentário do ADO ignora `<style>`/`<head>`).
2. Para cada `<img>` referenciada, sobe o PNG como anexo, vincula ao work item e reescreve o `src` para a URL **com o GUID do projeto** — assim as imagens ficam **embutidas no comentário**.
3. Sem `comment_id` → **cria** (imprime o `id`; **guardar** para futuras atualizações). Com `comment_id` → **atualiza** (PATCH). Se retornar **404 "Comment does not exist"**, rodar **sem** `comment_id` para criar novo.

**Regras:**

- **`ADO_PROJECT` obrigatório** = GUID do projeto do card (o agente confirma com `mcp__azure-devops__wit_work_item`, campo `System.TeamProject`, e já entrega o valor preenchido no comando). Sem ele, o upload fica org-level e o embed das imagens falha (HTTP 400).
- **PAT:** o script usa a variável já configurada em `.mcp.json` (`AZURE_DEVOPS_EXT_PAT`).
- Flags: `ADO_ATTACH=0` não (re)anexa (útil ao repostar só texto); `ADO_EMBED=0` anexa mas não embute.
- **`<body>` sem atributos:** o script casa `<body>(.*?)</body>` literal (`ado_update_comment.py:30`) — `<body style="…">` quebra a execução. O arquivo entregue deve estar compatível, para o comando rodar de primeira na mão do usuário.
- **Como o HTML sai pronto daqui e o agente não confere a postagem, o `evidencias.html` precisa estar completo e validado (I11) antes da entrega** — sem pendências nem placeholders.

Detalhes e GUIDs conhecidos: skill [azure-devops-cards](../skills/azure-devops-cards/SKILL.md).

---

### Fluxo completo

```
I11 aprovada pelo subagente
        ↓
1. Agente informa no chat: caminho do evidencias.html + GUID do projeto
        ↓
2. Agente exibe o comando pronto:
   ADO_PROJECT=<GUID> python3 .claude/scripts/ado_update_comment.py <evidencias.html> <work_item_id> [comment_id]
        ↓
3. Agente (após "sim" à pergunta) ou usuário roda o comando e posta no card (o script inlina CSS, sobe/vincula os PNGs e embute as <img>)
        ↓
I12 (gate deploy homol)
```

---

## Ciclo I12 — gate deploy homol

**Somente após I11 aprovada.**

1. Agente sinaliza no chat que local está validado e solicita deploy em homol.
2. **Aguardar OK explícito** do usuário confirmando deploy concluído.
3. **Não** executar `test:homol` antes do OK.

Modo: **Plan** (aguardar) ou **Agent** (sinalizar) — **sem alterar código** nesta etapa.

---

## Ciclo I13 — testes homol URL remoto (obrigatório)

**Somente após I12** (OK explícito de deploy).

Ordem fixa — detalhes em [testes-homol.md](testes-homol.md):

```
I12 OK recebido
        ↓
1. Confirmar homol remota acessível
        ↓
2. npm run test:homol — 100% pass (tela + HTTP 200 por cenário)
        ↓
3. Gerar evidências U01–UN em docs/evidencias/assets/
        ↓
4. restaurar patches locais (comando de restauração do perfil)
        ↓
I14 — evidenciashomol.html
```

| Passo | Comando / artefato |
|-------|-------------------|
| URL alvo | URL homol remota — ver o perfil `arquitetura/ambiente-local-{projeto}.md` |
| Testes | `cd testes && npm run test:homol` |
| Limpar local | comando de restauração de patches do perfil `arquitetura/ambiente-local-{projeto}.md` |

**Critério de saída I13:** 100% pass homol remota, ambiente local revertido. **Não encerrar o card** — falta I14 e I15.

---

## Ciclo I14 — HTML homol

**Somente após I13 concluída.**

Criar `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidenciashomol.html` contendo:

- Bloco **E2E** (print Playwright + tabela “Detalhamento dos cenários” — mesmo padrão I9)
- Bloco **homol URL** U01–UN (figuras embutidas)

**Não incluir** bloco de implementação nem bloco local — esses ficam em `evidencias.html`.

Detalhes: [documento-evidencias-html.md](documento-evidencias-html.md).

---

## Ciclo I15 — validação final do HTML homol (subagente)

**Somente após I14 concluída.**

Subagente `validador-tecnico` compara `evidenciashomol.html` com:

- Documento de **análise** aprovado
- Documento de **plano** aprovado
- Documento **executada** com resultados I7–I13
- Anexos `testes-e2e.md`, `testes-local.md`

Detalhes: [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i15).

```
I14 concluída
        ↓
Subagente valida evidenciashomol.html (rodada N)
        ↓
    ┌─── Status: Aprovado (100%)? ─── SIM ──→ Pós-I15: entregar evidenciashomol.html + comando (card de DESENVOLVIMENTO) ──→ Encerramento do card
    │
    NÃO
        ↓
Agente corrige evidenciashomol.html / testes / docs
        ↓
Subagente revalida (rodada N+1)
```

**Critério de saída I15:** `Status: Aprovado` em `## Validação do HTML homol` — **único gate de encerramento** do card com implementação.

---

## Pós-I15 — Entrega das evidências homol (só se houve desenvolvimento)

**Executado após I15 aprovada, sempre que houve desenvolvimento/implementação.** Se o card foi encerrado como análise suficiente (sem código), esta etapa **não** se aplica.

O agente pergunta *"Posto eu o `<arquivo>` no card `<n>`, ou te entrego o comando?"* e posta só com "sim" explícito (por postagem); senão entrega o comando de postagem.

O destino é o **card de DESENVOLVIMENTO**, que **pode ser diferente** do card do incidente/sustentação (ex.: no card 152069 o incidente e o desenvolvimento/teste estavam em cards distintos). O agente **sinaliza isso no chat** e deixa o número como placeholder `<card-de-dev>` no comando — **não** assume que é o mesmo card do incidente.

### Método padrão — mesmo comando da Pós-I11

```bash
ADO_PROJECT=<GUID-do-projeto-do-card-de-dev> python3 .claude/scripts/ado_update_comment.py <evidenciashomol.html> <card-de-dev> [comment_id]
```

- **`ADO_PROJECT`** = GUID do projeto do **card de desenvolvimento**. Se o card de dev estiver em outro projeto que não o do incidente, o GUID muda — o agente avisa no chat.
- Sem `comment_id` → **cria** (guardar o `id`); com `comment_id` → **atualiza**.
- Demais regras (inline de CSS, upload/embed de PNGs, PAT) idênticas à Pós-I11.

### Fluxo completo

```
I15 aprovada pelo subagente  (houve desenvolvimento)
        ↓
1. Agente informa no chat: caminho do evidenciashomol.html + que o destino é o card de DESENVOLVIMENTO
        ↓
2. Agente exibe o comando pronto (número do card de dev como placeholder):
   ADO_PROJECT=<GUID> python3 .claude/scripts/ado_update_comment.py <evidenciashomol.html> <card-de-dev> [comment_id]
        ↓
3. Agente (após "sim" à pergunta) ou usuário roda o comando e posta no card de desenvolvimento
        ↓
Encerramento do card
```

Detalhes e GUIDs conhecidos: skill [azure-devops-cards](../skills/azure-devops-cards/SKILL.md).

---

## Modo de operação (plan × agent)

| Modo | Etapas | O que inclui |
|------|--------|--------------|
| **Plan** | I1 a I4 (inclui **I1-rev**, **I2-html**, **I2-val**, **Pós-I2-val**), **I12** (aguardar OK) | Plano, revisões, `plano.html`, validações, entrega do `plano.html`, chat, OK do usuário, gate deploy |
| **Agent** | I5 a I11, I13 a I15 | Código, validação, E2E, local, homol, HTMLs, validações |

**Proibido:**

- alterar código da aplicação antes de **I4** (OK explícito);
- **I3 sem `plano.html` aprovado** (I2-val), na trilha completa;
- **I4 sobre o `.md`** quando não há `plano.html` aprovado;
- **fechar I6 sem I6-rev** quando houve revisão de segurança em I1-rev;
- **apagar seção do `plano.html`** em vez de marcar **N/A + motivo**.

---

## Handoff desde a sustentação (S6b)

1. Sinalizar no chat: *“Análise completa → implementação necessária (S6b)”*.
2. Seguir na **mesma aba do card** (aba única é o padrão), delegando cada etapa ao agente dela. Se o medidor cobrar o orçamento, **pedir** `/compact` ao usuário (com o número medido) e parar — abrir aba é exceção, não rotina.
3. Ordem da trilha confirmada no B0 — completa: I1 → I1-rev → I2-html → I2-val → Pós-I2-val → I3 → … → I15; curta: § *Trilha curta*.

Referências no plano: fluxo e análise aprovados em `docs/fluxos/` e `docs/analises/`.

## Entrada direta por B0 (sem sustentação)

Quando o usuário declara **“é implementação”** na bifurcação e confirma o **(Y/n)**, não há fluxo/análise aprovados para referenciar. Nesse caso, o **I1** documenta o entendimento da demanda a partir do card (C0) e do que o usuário descreveu — e os gates da trilha continuam obrigatórios — completa: **I2-val, I4, I6, I7, I10, I11, I12, I13, I15**; curta: **I2-val, I4, I10, I11, I12, I13, I15** (gatilhos valem nas duas).

---

## Guias desta pasta

| Documento | Etapa |
|-----------|-------|
| [documento-implementacao.md](documento-implementacao.md) | I1, I1-rev — plano |
| [documento-plano-html.md](documento-plano-html.md) | I2-html, I2-val, Pós-I2-val — `plano.html` |
| [documento-implementacao-executada.md](documento-implementacao-executada.md) | I5–I15 — executada |
| [validacao-subagente.md](validacao-subagente.md) | I2-val, I6, I11, I15 |
| [testes-e2e.md](testes-e2e.md) | I7 |
| [testes-local.md](testes-local.md) | I10, I11 |
| [testes-homol.md](testes-homol.md) | I13, I14 |
| [documento-testes.md](documento-testes.md) | I8, I11 (anexos) |
| [documento-evidencias-html.md](documento-evidencias-html.md) | I2-html, I9, I11, I14 |
| [resposta-chat.md](resposta-chat.md) | Todas |

Regras: skill [`regras-de-trabalho`](../skills/regras-de-trabalho/SKILL.md); gates em [`fluxo-completo.md`](../fluxo-completo.md) § *Tabela mestra*.

---

## Exceções

- **S5 = análise suficiente** — ciclo I1–I15 **não** se aplica.
- **B0 = implementação** com **(Y/n)** confirmado — S1–S6 pulados; entra-se direto em **I1** (nenhuma etapa da trilha pode ser pulada).
- Usuário pede explicitamente pular etapa *(registrar no chat)*.
- Quando houve **implementação**, em qualquer trilha, **I2-val**, **I10**, **I11**, **I13** e **I15** **não** podem ser puladas.
