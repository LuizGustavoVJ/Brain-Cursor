# Validação por subagente — implementação

Validação do **plano (I2-val — o antigo I2 foi fundido aqui)**, código (I6), HTML local (I11) e HTML homol (I15). Para **fluxo e análise** (sustentação) → [sustentacao/validacao-subagente.md](../sustentacao/validacao-subagente.md).

Mapa completo: [fluxo-completo.md](../fluxo-completo.md).

> **Fase 3 (25/09/2026) — prevalece [`fluxo-completo.md`](../fluxo-completo.md) § *Trilhas*:** o I2 foi fundido no
> **I2-val** (uma validação do plano), existe a **trilha curta** (sem `plano.html`, I6 e E2E separados)
> e toda validação tem **teto de 3 rodadas**. Onde este guia divergir, vale o `fluxo-completo.md`.

| Etapa | O quê | Quando | Subagente · modelo |
|-------|-------|--------|--------------------|
| **I2-val (curta)** | Plano curto em `docs/implementacoes/plano/` — estrutural + nenhum critério de completa | Antes do I4 | [`validador-leve`](../agents/validador-leve.md) · **Haiku** |
| **I2-val (completa)** | **`plano.html`** + plano `.md` + I1-rev + conformidade, numa rodada — **gate do I4** | Após I2-html; registro em `## Validação do plano.html` no plano `.md` | [`validador-tecnico`](../agents/validador-tecnico.md) · **Opus** |
| **I6** | Código vs plano aprovado (`plano/`), **incluindo I6-rev** | Depois do código (I5); registro em `executada/` | [`validador-tecnico`](../agents/validador-tecnico.md) · **Opus** |
| **I11** | Completa: bloco **local** L01–LN **+ bloco E2E (print+tabela)** vs I10/I7 + plano. Curta: **código vs plano curto + `evidencias.html`** | Após I10 (completa: pode consolidar com I15) | [`validador-tecnico`](../agents/validador-tecnico.md) · **Opus** |
| **I15** | `evidenciashomol.html` vs análise + plano + `executada/` | Após I14 | [`validador-tecnico`](../agents/validador-tecnico.md) · **Opus** |

**Não usar `general-purpose` para validar** — herda o modelo da sessão (Opus) mesmo em validação estrutural. Passar o **caminho do arquivo**, nunca o conteúdo colado. Política: [otimizacao-custos.md](../otimizacao-custos.md) § *Subagentes*.

O plano é validado **uma vez** (I2-val): na completa, `validador-tecnico` sobre plano `.md` + `plano.html`; na curta, `validador-leve` sobre o plano curto (se responder `Status: Escalonar`, o card tem critério de completa — promova). É essa aprovação que sustenta o OK do usuário em I4.

**Teto de 3 rodadas por etapa** (`cache_validacao.py rodada <ETAPA> <card>` antes, `recusa` depois): na 3ª recusa a etapa para e escala ao usuário com as divergências remanescentes.

## Cache de validação

Antes de cada rodada, checar se o documento idêntico já foi aprovado:

```bash
python3 .claude/scripts/cache_validacao.py check I2-val docs/implementacoes/plano/impl-x.md   # HIT → reaproveitar
python3 .claude/scripts/cache_validacao.py save  I2-val docs/implementacoes/plano/impl-x.md Aprovado --card <n>
python3 .claude/scripts/cache_validacao.py check I2-val docs/evidencias/html/{tema}/{card}/plano.html
```

Chave = `sha256(etapa + conteúdo)`, TTL 1h, só `Aprovado` é reaproveitado.

Ciclo geral: [fluxo-implementacao.md](fluxo-implementacao.md).

---

## Ciclo obrigatório (plano — I2-val)

```
Agente elabora ou atualiza docs/implementacoes/plano/impl-*.md (com I1-rev registrada)
        ↓
Subagente valida (rodada N)
        ↓
    ┌─── Status: Aprovado? ─── SIM ──→ (completa: I2-html → I2-val) → I3 → I4 → I5   · máx. 3 rodadas
    │
    NÃO
        ↓
Agente corrige o documento → revalidação obrigatória
```

### Regras do plano `.md`

1. Curta: `validador-leve` (Haiku); completa: o `.md` é conferido junto com o `plano.html` no I2-val (`validador-tecnico`).
2. Saída: `Status: Aprovado` ou `Status: Recusado` em `## Validação` — **sem meio-termo**. Se recusado: corrigir e revalidar até 100% aprovado.
3. **Escopo estrutural:** seções obrigatórias presentes (incluindo `## Conformidade e segurança`), escopo e fora de escopo, ordem de execução, ACs, matriz de testes. As revisões de especialistas ficam no **`_processo-revisoes.md` interno** (regras.md § 11), não no plano `.md`; confira o gatilho **lá** e recuse se o plano citar agente da frota.
4. O gate do I4 é a **I2-val** aprovada.

---

## Ciclo obrigatório (etapa I2-val — plano.html)

**Após I2-html.** Subagente [`validador-tecnico`](../agents/validador-tecnico.md) (**Opus**) valida o
`plano.html` contra o plano `.md`, as revisões de **I1-rev** e o checklist de conformidade.
Guia do artefato: [documento-plano-html.md](documento-plano-html.md).

```
I2-html concluída (plano.html gerado pelo escritor-evidencias)
        ↓
Subagente valida plano.html (rodada N)
        ↓
    ┌─── Status: Aprovado (100%)? ─── SIM ──→ Pós-I2-val (caminho + GUID; pergunta: posto eu ou entrego o comando?) → I3 → I4
    │
    NÃO
        ↓
Agente corrige plano.html (e o plano .md, se a falha vier dele) → revalidação obrigatória
```

### Regras I2-val

1. **Revisor:** `validador-tecnico` (**Opus**) — **aprovação pelo próprio agente não conta**.
2. **Arquivo:** `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html` — passar o **caminho**, nunca o conteúdo.
3. **Saída:** `Status: Aprovado` em **`## Validação do plano.html`** no plano `.md`.
4. **É este o gate do I4** — sem ele, proibido apresentar I3 e proibido pedir o OK do usuário.

### Critérios de RECUSA (qualquer um recusa)

- **Revisão de especialista disparada em I1-rev e não registrada** — gatilho bateu e não há linha com veredito e **onde foi acatado** (nem a linha de gatilhos não disparados).
- **Qualquer um dos 8 itens de conformidade em branco** — cada item fecha em `OK` / `N/A + por quê` / `Pendência`.
- **Seção do esqueleto apagada** em vez de marcada **`N/A + motivo`** (as 13 seções são fixas).
- **Antes/depois sem marcação** `novo` / `alterado` / `removido` / `inalterado` em toda linha, ou sem as **duas** partes (tabela lado a lado **e** fluxo numerado).
- **Decisão sem alternativa** ou **sem custo de reverter** na seção “Decisões e por quê”.

Também recusa: divergência entre `plano.html` e plano `.md`, PNG/print no `plano.html` (não há
teste em I2-html), mermaid no HTML, `<body>` com atributos, CSS fora do `<style>` canônico da skill.

### Formato `## Validação do plano.html`

```markdown
## Validação do plano.html

### Rodada 1 (YYYY-MM-DD)
- **Status:** Recusado | Aprovado
- **Revisor:** subagente `validador-tecnico`
- **Arquivo:** `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html`
- **Referências:** plano `.md` · `## Revisões de especialistas` no `_processo-revisoes.md` interno (I1-rev) · `## Conformidade e segurança`
- **Motivos de recusa / divergências:** ...
- **Ações corretivas:** ...
```

---

## Ciclo obrigatório (etapa I6 — código, inclui I6-rev)

**Após I5.** Subagente revisa se a implementação cumpre o **plano aprovado** e os **critérios de aceite**.

```
I5 concluída → I6-rev (especialistas por gatilho, sobre o diff) → validador-tecnico (rodada N) → Aprovado? → I7
                                    ↑_______________________________________________|
                                              (corrigir até 100%)
```

### I6-rev — revisões de especialistas sobre o diff

**Obrigatória quando houve revisão de segurança em I1-rev**: `especialista-seguranca` confere se o
**diff cumpre o que o plano decidiu**. Demais gatilhos (frontend, acessibilidade, design system,
`revisor-codigo`) em [fluxo-implementacao.md](fluxo-implementacao.md#ciclo-i6-rev--revisões-de-especialistas-sobre-o-diff).

Registro em **`## Revisões de especialistas (código)`** no **`_processo-revisoes.md` interno**
(regras.md § 11), nunca em documento entregável (Especialista · Veredito · Ponto · Onde foi
acatado) + a linha de gatilhos não disparados. O checklist de conformidade do plano é
**reconferido** aqui.

**O `validador-tecnico` recusa o I6** se houve segurança em I1-rev e não há revisão de segurança do
diff registrada, ou se uma revisão disparada em I6-rev ficou sem registro.

### Formato `## Validação do código`

No `.md` em `docs/implementacoes/executada/`:

```markdown
## Validação do código

### Rodada 1 (YYYY-MM-DD)
- **Status:** Recusado | Aprovado
- **Revisor:** subagente `validador-tecnico`
- **Commit base:** `{hash}` (pós-I5)
- **Plano referência:** `docs/implementacoes/plano/impl-*.md`
- **Motivos de recusa / ressalvas:** ...
- **Ações corretivas:** ...
```

---

## Ciclo obrigatório (etapa I11 — HTML local)

**Após I10.** Subagente revisa o bloco **local** em `evidencias.html` (L01–LN).

```
I10 concluída (test:local 100%)
        ↓
Subagente valida bloco local em evidencias.html (rodada N)
        ↓
    ┌─── Status: Aprovado (100%)? ─── SIM ──→ Pós-I11 (HTML; pergunta: posto eu ou entrego o comando?) → I12 (gate deploy homol)
    │
    NÃO
        ↓
Agente corrige HTML / testes / testes-local.md → revalidação
```

### Regras I11

1. **Quando:** somente após I10 concluída e bloco local preenchido em `evidencias.html`.
2. **Escopo:** bloco **local** L01–LN **e** bloco **E2E (I9)** no mesmo arquivo — subagente **recusa** se E2E estiver incompleto.
3. **Revisor:** subagente `validador-tecnico` — **aprovação pelo agente no mesmo turno não conta**.
4. **Saída:** `Status: Aprovado` em `## Validação do HTML local`.

### Pós-I11 — entrega ao usuário (não há conferência de postagem)

Aprovada a I11, o agente entrega no chat o caminho do `evidencias.html`, pergunta *posto eu ou entrego o comando?* (posta só com "sim") e segue para **I12**. **Não há etapa de conferência da postagem** — a validação I11 é o último gate sobre o HTML, então ele precisa sair 100% pronto daqui. Mesmo critério na sustentação (**S6a-val** → **Pós-S6a**).

### Critérios mínimos (HTML local)

- Resultados **local** (N/N, L01–LN) condizem com execução I10 e `testes-local.md`
- Matriz **somente telas/views/assets alterados pela demanda** (conforme plano § Testes local/homol) — **sem** cenários genéricos não relacionados ao card
- **Sem login vazio** como cenário L — autenticação via `auth.setup` / helper, não como evidência funcional
- **Cadastro / edição:** 2 prints (`{prefixo}{xx}-get-tela.png`, `-post-tela.png`) + JSON GET + POST **200** (redirect 302/303 aceito se tela final 200)
- **Filtro:** 1 print + JSON GET **200** — **sem** submit que dispare alerta de erro
- **Asset / API:** JSON GET **200** + trecho do corpo
- **Proibido** prints com toasts/alertas de erro (`.toast-error`, “Não foi possível localizar registros”, etc.)
- **Cadastro / filtro / edição / exibição:** dados de teste do plano/AC **preenchidos antes** do screenshot
- **Listagem / hub / rota não alterada:** **não incluir** na matriz salvo se o plano exigir e houver evidência útil (campo preenchido, ação ou dado demonstrável)
- **HTTP 200** na rota principal de cada cenário de página e em assets/API — **recusar** evidências com 401/403/404/500 ou corpo de erro (404, Fatal error, PHP Error)
- **Figura/evidência HTTP por cenário** da matriz local (não só “Pass” na tabela resumo)
- Prefixo **L** consistente; **sem** figuras U (homol) em `evidencias.html`
- Matriz local alinhada à § Testes local/homol do plano (mesmos cenários que homol, prefixos L vs U)

### Critérios mínimos (bloco E2E no mesmo arquivo — I9)

Conforme [documento-evidencias-html.md](documento-evidencias-html.md#padrão-e2e-obrigatório-todos-os-cards-todos-os-repositórios) — **obrigatório em todos os cards**:

- **`h3`** “1. Relatório Playwright — execução completa”
- **`figure.evidence`** com PNG `{card-id}-e2e-playwright.png` existente em `docs/evidencias/assets/`
- **`h3`** “2. Detalhamento dos cenários” com colunas # · Cenário · Documento / entrada · AC · Resultado
- **N/N** condizente com I7, `testes-e2e.md` e spec E2E
- **Proibido:** só tabela resumida, só `<pre>` com comando, ou texto “pass” sem print

### Formato `## Validação do HTML local`

```markdown
## Validação do HTML local

### Rodada 1 (YYYY-MM-DD)
- **Status:** Recusado | Aprovado
- **Revisor:** subagente `validador-tecnico`
- **Arquivo:** `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html` (bloco local)
- **Referências:** plano · testes-local.md · stdout I10
- **Motivos de recusa / divergências:** ...
- **Ações corretivas:** ...
```

---

## Ciclo obrigatório (etapa I15 — HTML homol)

**Após I14.** Subagente revisa `evidenciashomol.html` vs **análise**, **plano** e resultados reais I7/I10/I13.

```
I14 concluída (evidenciashomol.html: E2E + homol)
        ↓
Subagente valida evidenciashomol.html (rodada N)
        ↓
    ┌─── Status: Aprovado (100%)? ─── SIM ──→ Encerramento do card
    │
    NÃO
        ↓
Agente corrige evidenciashomol.html / testes / docs → revalidação
```

### Regras I15

1. **Quando:** somente após I13–I14 concluídas.
2. **Arquivo:** `evidenciashomol.html` — **não** `evidencias.html`.
3. **Saída:** `Status: Aprovado` em `## Validação do HTML homol` — **único encerramento** do card.

### Critérios mínimos (HTML homol vs análise + plano)

**Conformidade com a análise e plano**

- ACs no HTML homol sustentados por E2E/homol citados
- Resultados **homol** (N/N, U01–UN) condizem com plano e execução I13
- Decisões condicionais do plano refletidas corretamente

**Integridade do `evidenciashomol.html`**

- Bloco **E2E** completo (print Playwright + tabela “Detalhamento dos cenários”) — **mesmo padrão** de `evidencias.html` I9; **não** aceitar “resumo”
- Bloco homol completo: tabela + **figura/evidência HTTP por cenário U** — mesmas regras de escopo, preenchimento e HTTP 200 que local (ver critérios I11)
- **Sem** bloco implementação, **sem** bloco local L
- Prefixo **U** consistente; sem mistura com L
- Sem inconsistências internas (ex.: “10/10” vs tabela com falha)

### Formato `## Validação do HTML homol`

```markdown
## Validação do HTML homol

### Rodada 1 (YYYY-MM-DD)
- **Status:** Recusado | Aprovado
- **Revisor:** subagente `validador-tecnico`
- **Arquivo:** `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidenciashomol.html`
- **Referências cruzadas:** análise · plano · executada · testes-e2e.md · testes-local.md
- **Motivos de recusa / divergências:** ...
- **Ações corretivas:** ...
```

---

## Após cada resultado

| Etapa | Aprovado | Recusado |
|-------|----------|----------|
| **I2-val** (gate do I4) | **Pós-I2-val** (caminho + GUID; pergunta: posto eu ou entrego o comando?) → I3 — chat; aguardar OK (I4) | Corrigir `plano.html` (e o `.md`, se for a origem) → revalidar |
| **I6** (com I6-rev) | I7 — testes E2E | Corrigir código → revalidar |
| **I11** | I12 — gate deploy homol | Corrigir HTML local → revalidar |
| **I15** | Encerramento do card | Corrigir evidenciashomol.html → revalidar |

**Proibido:** **I3 sem `plano.html` aprovado (I2-val)** na completa; **4ª rodada sem decisão do usuário**; **I4 sobre o `.md`** sem `plano.html` aprovado; I7 sem I6; **fechar I6 sem I6-rev** quando houve revisão de segurança em I1-rev; I10 sem I9; I13 sem I12; **encerrar card** sem I15 aprovada; **aprovar I2-val/I11/I15 sem subagente `validador-tecnico`**; **apagar seção do `plano.html`** em vez de marcar `N/A + motivo`; **E2E no HTML sem print + tabela detalhada** (padrão de referência).
