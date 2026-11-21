# Política de economia de custos — Claude Code

Aplicável a **todo card**, em qualquer fluxo (S1–S6 ou I1–I15). Não altera nenhum gate: os
critérios de aprovação continuam os mesmos — muda **quem valida**, **quantas vezes** e **quanto
texto entra no contexto**.

Mapa do fluxo: [fluxo-completo.md](fluxo-completo.md) · Relatório mensal:
[`scripts/relatorio_custos.py`](scripts/relatorio_custos.py).

---

## Gargalos medidos e alvos

| Gargalo | Antes | Alvo | Alavanca |
|---------|------:|-----:|----------|
| Subagentes (validações) | 44% | ≤ 30% | Modelo por etapa + validação consolidada + cache |
| MCP Playwright / testes | 24% | ≤ 15% | Saída resumida + `/compact` pós-teste + MCP só nas etapas de captura |
| Contexto acumulado na aba do card | — | < 300k | Orquestrar: só caminho de arquivo + veredito no principal |
| Prompt do hook `UserPromptSubmit` | ~4k tokens **por mensagem** | < 800 | Hook enxuto apontando para o CLAUDE.md |

---

## 1. Subagentes — modelo por etapa

Duas definições de subagente, escolhidas pela natureza da validação:

| Subagente | Modelo | Etapas | Por quê |
|-----------|--------|--------|---------|
| [`validador-leve`](agents/validador-leve.md) | **Haiku** | **S2** (fluxo, quando separado) · **I2-val da trilha curta** (plano curto) | Verificação estrutural: completude, coerência, referências existem. Não exige julgamento arquitetural. Custa ~80% menos por token que Opus. |
| [`validador-tecnico`](agents/validador-tecnico.md) | **Opus** | **S4** · **S6a-val** · **I6** · **I11** · **I15** | Causa raiz, review de código vs plano e conferência visual de HTML — exige julgamento técnico. |

**Como invocar:** `Agent` com `subagent_type: "validador-leve"` ou `"validador-tecnico"`.
Não usar `general-purpose` para validação — ele herda o modelo da sessão (Opus) e recebe o
contexto inteiro da conversa.

**Escalonamento:** se o `validador-leve` responder `Status: Escalonar`, reexecutar a mesma
validação com `validador-tecnico`. Isso é raro; se virar rotina em S2 ou no plano curto, o documento está
mal estruturado — corrigir o documento, não o subagente.

**Enviar o mínimo:** o prompt do subagente deve conter **o caminho do arquivo** e a etapa, não o
conteúdo colado. O subagente lê o arquivo com `Read`. Colar o documento no prompt paga o
documento duas vezes.

---

## 2. Subagentes — validação consolidada S2-S4 e cache

### 2.1 Validação consolidada (padrão em sustentação)

**Padrão:** produzir **S1 (fluxo)** e **S3 (análise)** na mesma passada e submeter **uma única
validação consolidada S2-S4** ao [`validador-tecnico`](agents/validador-tecnico.md), cobrindo
os dois documentos.

```
S1 (fluxo) + S3 (análise + HTML diagnóstico)
        ↓
S2-S4 consolidada — validador-tecnico, uma rodada
        ↓
    ┌── Aprovado (ambos)? ── SIM ──→ S5 (decisão)
    │
    NÃO → corrigir o(s) documento(s) recusado(s) → revalidar (só o recusado)
```

Na revalidação, submeter **apenas o documento recusado** — não repagar o que já passou.

**Manter S2 e S4 separadas quando** (registrar o motivo no chat):

- incidente crítico ou card com impacto em produção;
- o fluxo (S1) tem ambiguidade que muda a análise — validar o fluxo primeiro evita escrever
  uma análise inteira em cima de premissa errada;
- o usuário pedir explicitamente as duas rodadas.

Fora desses casos, consolidar. O ganho é um roundtrip de subagente por card.

> **I2 foi fundido no I2-val (Fase 3).** Uma validação do plano; e o `escritor-evidencias` desceu para Sonnet.
> **O plano não consolida com outra etapa.** O plano é validado sozinho, antes do gate I4 — é o que sustenta
> o OK explícito do usuário para codar.

### 2.2 Cache de validação

Antes de disparar qualquer subagente de validação, checar se o documento já foi aprovado
sem alteração:

```bash
python3 .claude/scripts/cache_validacao.py check I2-val docs/implementacoes/plano/impl-x.md
# HIT Aprovado ... (exit 0) → reaproveitar, registrar no .md e seguir
# MISS              (exit 1) → disparar o subagente
```

Depois da resposta do subagente:

```bash
python3 .claude/scripts/cache_validacao.py save I2-val docs/implementacoes/plano/impl-x.md Aprovado
```

Chave: `sha256(etapa + conteúdo do arquivo)`. TTL 1h. Só `Aprovado` é reaproveitado — qualquer
byte alterado no documento é MISS, então **não existe risco de aprovar versão diferente da
validada**. Cache em `.claude/cache/validacoes.json` (gitignorado).

Usar quando: refazer a mesma validação na mesma sessão, retomar após interrupção, ou quando o
usuário reexecuta uma etapa por engano.

---

## 3. Playwright e testes — nunca despejar o stdout

Guia operacional: [implementacao/testes-resumido.md](implementacao/testes-resumido.md).

**Regra:** em **I7**, **I10** e **I13**, rodar via wrapper e registrar só o resumo:

```bash
.claude/scripts/resumo_testes.sh e2e     # I7
.claude/scripts/resumo_testes.sh local   # I10
.claude/scripts/resumo_testes.sh homol   # I13
```

O log completo vai para `.claude/cache/logs-testes/` (gitignorado); só a tabela de cenários, o
sumário N/N e — se houver falha — as primeiras 40 linhas do erro voltam ao contexto.

**Entra no contexto:** resultado final N/N, tempo, tabela de cenários, print do relatório
Playwright, prints dos cenários **da matriz do plano**, e o erro dos cenários que falharam.
**Não entra:** stdout completo, output por assertion, print de cenário que passou e não está na
matriz.

Um hook `PostToolUse` ([`hook_pos_testes.py`](scripts/hook_pos_testes.py)) lembra disso
automaticamente após cada `test:*` e sugere `/compact` quando a aba estiver carregada.

### MCP Playwright — só onde é necessário

O MCP é para **captura de evidência**, não para navegar por curiosidade.

| Etapa | MCP Playwright |
|-------|----------------|
| **I7, I10, I13, I14** — capturar prints das evidências | **Sim** |
| C0, L0, S1–S6, I1–I4 | **Não** — análise e plano não precisam de browser |
| I5, I6, I8, I9, I11, I12, I15 | **Não** — usar os prints já capturados |

Não existe chave em `settings.json` para ligar/desligar MCP por fase — o cumprimento é do
agente. Se precisar validar uma URL fora das etapas de captura, use `curl -sI` (já permitido),
que custa uma fração de um `browser_snapshot`.

---

## 4. Aba única por card — abrir aba é exceção, não rotina

**ABA ÚNICA POR CARD é obrigatória** — outro card citado nesta aba dispara o alerta do
`hook_card.py` (o agente avisa e aguarda). O card inteiro cabe numa aba porque o contexto principal só
**orquestra**: despacha cada etapa ao subagente dela e guarda **caminho de arquivo + veredito de
15 linhas**. Conteúdo de documento **nunca** volta para o principal — é essa delegação que torna a
aba única viável, e é o que substituiu o modelo antigo de dividir o card em 5 abas por rotina.
Orçamento: **300k** (modelo opus[1m]; corte de exceção ≥130% = 390k), medido por `fase.sh` + `hook_contexto.py`, **por sessão**.

`/compact` e `/clear` passam a ser **exceção cobrada pelo medidor** e, quando cobrados, só no
**corte de exceção do bloco** — o ponto em que o contexto já entregou o artefato e o que sobra é
descartável.

Tabela de blocos e rótulo do medidor: fonte única em
[fluxo-completo.md](fluxo-completo.md) § *Aba única por card e orçamento de contexto*.

O `/compact` **imediatamente após cada suíte** é a alavanca principal: é o momento em que o
contexto está mais inflado e o conteúdo descartável (logs) é mais fácil de identificar. O que
tem de sobreviver ao compact: resultado N/N, caminhos dos prints, tabela de cenários.

### Medidor automático de contexto

Este é o gargalo real medido: a **média histórica é de ~293k tokens de contexto por resposta**.
O orçamento de 150k (15% da janela de 1M) forçou 463 compactações manuais e 5.063 avisos, 99%
amarelos — em 25/09/2026 passou a **300k**, e o medidor passou a falar só quando a faixa sobe. Cada turno relê esse contexto inteiro (cache read), e cache read responde por
**~47% do custo total**. Nenhuma outra otimização deste documento chega perto desse impacto.

Como depender de memória não funcionou, a checagem é automática:

| Peça | Papel |
|------|-------|
| [`scripts/fase.sh`](scripts/fase.sh) | O agente **declara** etapa e card ao entrar na etapa: `.claude/scripts/fase.sh I7 167697`. Estado **por sessão** (`CLAUDE_CODE_SESSION_ID`); card diferente do ativo imprime o alerta de aba única. |
| [`scripts/hook_contexto.py`](scripts/hook_contexto.py) | Hook em `UserPromptSubmit` + `PostToolUse`. Lê o transcript da sessão, calcula o contexto **real** e compara com o orçamento da fase declarada. |

Três níveis, com ação diferente em cada um:

| Situação | Nível | O que o agente faz |
|----------|-------|--------------------|
| ≥ 85% do orçamento | 🟡 próximo do limite | Avisa ao concluir a etapa; **não** interrompe a tarefa |
| ≥ 130% | 🟠 acima | **Para**, pede `/compact` na **primeira linha** da resposta e **aguarda** a execução |
| ≥ 200% | 🔴 crítico | **Para**, entrega um resumo de 3–5 linhas do estado e pede `/clear` **no corte de exceção do bloco** |

**Silencioso dentro do orçamento e dentro da mesma faixa** — só injeta quando a faixa **sobe**
(85% → 130% → 200%, gravada por sessão); faixa que desce após `/compact` é gravada em silêncio.
Em 🔴 cobra a destilação do card antes do `/clear`. Roda em ~45ms lendo só a cauda do transcript.

**Sem fase declarada** ele assume o padrão de 300k e diz que a fase não foi declarada
— nunca adivinha a etapa pelo texto da conversa (um palpite errado produziria orçamento errado).

> **O agente não executa `/compact` nem `/clear`** — são comandos do cliente, e hooks não os
> disparam. O que a automação garante é que o pedido apareça **no momento certo, com o número
> medido**, em vez de depender de o agente lembrar. A execução continua sendo sua.

**Pedir compactação encerra o turno.** A partir de 130% o agente **para** na mesma resposta em que
pede: não inicia, não continua e não retoma nada até o usuário rodar o comando. O motivo é
prático — `/compact` leva tempo do lado do usuário, e um agente que segue trabalhando nesse
intervalo consome exatamente o contexto que a compactação vai tentar recuperar. Antes de parar,
o agente registra em 1–2 linhas onde a tarefa ficou, para retomar sem redescobrir o estado.

---

## 5. Hábitos que valem mais que qualquer ajuste de configuração

- **Ler trecho, não arquivo inteiro** — `Read` com `offset`/`limit`, ou `Grep` com contexto.
- **Não reler arquivo que acabou de editar** — o `Edit` teria falhado se não tivesse aplicado.
- **Não colar conteúdo de arquivo no chat** para "mostrar" — referenciar `caminho:linha`.
- **Uma pergunta ao usuário por vez, agrupada** — cada roundtrip repaga o contexto inteiro.
- **Nunca trazer conteúdo de artefato do subagente para o principal** — só caminho e veredito; é
  o que sustenta a aba única. `/clear` só quando o medidor cobrar, no corte de exceção do bloco.

Ver também a skill [antialucinacao-eficiencia](skills/antialucinacao-eficiencia/SKILL.md)
§ *Não desperdiçar tokens*.

---

## 6. Revisão mensal — automatizada

Toda **sexta-feira às 12:00** o agente roda:

```bash
python3 .claude/scripts/relatorio_custos.py --dias 30
```

e apresenta no chat: custo estimado por modelo, fatia de subagentes vs agente principal, fatia
de Playwright, uso de `/compact` e `/clear`, e taxa de revalidação — cada um comparado ao alvo
da tabela no topo deste documento, com o próximo ajuste recomendado.

Rodar sob demanda a qualquer momento com `--dias 7` para uma leitura semanal.

> O relatório é **estimativa** calculada dos `usage` nos transcripts locais
> (`~/.claude/projects/-{projeto}/*.jsonl`), com a tabela de preços no topo do script. Não
> substitui a fatura do Console — serve para comparar períodos e localizar o gargalo.

**Quando a distribuição mudar:** se subagentes caírem abaixo de 30% e Playwright abaixo de 15%,
o próximo gargalo costuma ser o contexto acumulado na aba do card — a resposta é delegar mais
etapas a subagentes (caminho + veredito no principal), não cortar validação nem picar o card em
abas.
