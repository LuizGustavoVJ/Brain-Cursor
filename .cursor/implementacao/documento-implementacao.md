# Documento de implementação — plano

**Pasta:** `docs/implementacoes/plano/`  
**Nome:** kebab-case descritivo com prefixo `impl-` quando útil (ex.: `impl-cnpj-alfanumerico.md`)

Guia operacional: [fluxo-implementacao.md](fluxo-implementacao.md).  
HTML do plano (I2-html): [documento-plano-html.md](documento-plano-html.md).  

> **Fase 3 (25/09/2026) — prevalece [`fluxo-completo.md`](../fluxo-completo.md) § *Trilhas*:** o I2 foi fundido no
> **I2-val** (uma validação do plano), existe a **trilha curta** (sem `plano.html`, I6 e E2E separados)
> e toda validação tem **teto de 3 rodadas**. Onde este guia divergir, vale o `fluxo-completo.md`.
Consolidação pós-código: [documento-implementacao-executada.md](documento-implementacao-executada.md).

## Quando produzir

Na **etapa I1**, após sustentação concluir com **implementação necessária** (**S5**).

**Pré-requisitos:**

- Fluxo aprovado em `docs/fluxos/{tipo}/`
- Análise aprovada em `docs/analises/{tipo}/`

## Conteúdo mínimo (plano — detalhado)

- Referência ao fluxo e à análise aprovados (links)
- Premissas e decisões herdadas da análise
- Escopo e **fora de escopo**
- Estratégia técnica e alterações **propostas** (arquivos, métodos, trechos)
- Ordem de execução (passos numerados)
- Critérios de aceite (AC1, AC2, …)
- Secção **`## Testes E2E`** — specs em `testes/E2E/`, AC cobertos, `npm run test:e2e`
- Secção **`## Testes homol (URL)`** — matriz de rotas/views, `npm run test:homol`, evidência dupla (tela + HTTP 200)
- Verificação pós-implementação (queries manuais, se houver)
- Riscos e rollback
- Registro de I1-rev **no `_processo-revisoes.md` interno**, não neste `.md` (regras.md § 11)
- Secção **`## Conformidade e segurança`** (8 itens — obrigatória, nenhum em branco)
- Secção **`## Validação do plano`** (I2-val — completa: `validador-tecnico` sobre `.md` + `plano.html`; curta: `validador-leve` — **gate do I4**)

**Não incluir** no plano: diff real, validação de código (I6), validação de HTML (I11) — isso vai em `executada/`.

### Revisões de especialistas (I1-rev) — no `_processo-revisoes.md` interno

O documento oficial **não cita agente da frota** (regras.md § 11). Toda revisão **disparada por
gatilho** (fonte única: [`frota/gatilhos.tsv`](../frota/gatilhos.tsv), via `frota.sh gatilhos`)
entra na tabela `Especialista · Veredito · Ponto · Onde foi acatado` **no `_processo-revisoes.md`
da pasta do card** — arquivo interno não-entregável, nunca neste `.md` nem no `plano.html`.

Fechar com **uma** linha: *“Gatilhos avaliados e não disparados: …”*. Gatilho disparado **sem**
linha no `_processo-revisoes.md` = **recusa** em I2-val.

### `## Conformidade e segurança` (8 itens)

Os oito itens são **obrigatórios** e cada um fecha em **`OK`** / **`N/A + por quê`** / **`Pendência`** — **nenhum em branco** (branco = recusa em I2-val). São reconferidos em **I6-rev** sobre o diff.

| # | Item |
|---|------|
| 1 | Dado de cartão (PAN, CVV, validade, titular) trafega ou persiste? |
| 2 | Token/credencial: onde nasce, onde vive, quando expira, quem rotaciona |
| 3 | Token aparece em URL, log, HTML, `localStorage` ou histórico? |
| 4 | Rota nova é pública? Autenticação e autorização |
| 5 | Segredo no `.env` (**nunca** versionado) e no `.env.example` **sem valor** |
| 6 | LGPD: campo, finalidade, retenção, quem acessa |
| 7 | Efeito financeiro **idempotente** (duplo clique, duas abas, reenvio de webhook) |
| 8 | Limite de abuso: rate limit, tentativa, enumeração de token |

### `## Validação do plano.html` (I2-val)

Registro das rodadas do `validador-tecnico` sobre o `plano.html` — é **esta** seção que sustenta o I3/I4:

```markdown
## Validação do plano.html

### Rodada 1 (YYYY-MM-DD)
- **Status:** Recusado | Aprovado
- **Revisor:** subagente `validador-tecnico`
- **Arquivo:** `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html`
- **Motivos de recusa / divergências:** ...
- **Ações corretivas:** ...
```

## Validação do plano (I2-val) — única, é o gate do I4

O antigo I2 (pré-conferência estrutural) foi **fundido no I2-val** (Fase 3). **Completa:** o `.md`
concluído (com I1-rev e conformidade) vira `plano.html` (I2-html) e o `validador-tecnico` valida os
dois numa rodada. **Curta:** plano curto, sem `plano.html`, validado pelo `validador-leve`. Recusado →
corrigir → nova rodada, **no máximo 3**; na 3ª recusa, escalar ao usuário. Sem I2-val aprovada:
**proibido** apresentar I3 e pedir o OK do I4 (na completa, nunca sobre o `.md` sem `plano.html`).

Detalhes: [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i2) e [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i2-val--planohtml).

## Após aprovação (Pós-I2-val, I3 e I4)

1. **Pós-I2-val:** entregar no chat o caminho do `plano.html`, o **GUID do projeto** e perguntar **posto eu ou entrego o comando?** — posta só com "sim"; senão entrega o **comando pronto** de `ado_update_comment.py`.
2. Resumir no chat e informar os caminhos: `docs/implementacoes/plano/impl-*.md` **e** `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html`.
3. Informar o resultado da **I2-val** (rodada final, N de 3).
4. **Aguardar OK explícito** do usuário (I4) — sobre o plano aprovado (`plano.html` na completa).
5. **Só então** I5 (código) e criação/atualização do documento em **`executada/`**.

Regras: skill [`regras-de-trabalho`](../skills/regras-de-trabalho/SKILL.md).
