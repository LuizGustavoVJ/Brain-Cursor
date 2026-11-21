# Documento de implementação — executada

**Pasta:** `docs/implementacoes/executada/`  
**Nome:** mesmo basename do plano (ex.: `impl-cnpj-alfanumerico.md`)

Plano correspondente: `docs/implementacoes/plano/impl-*.md` (mesmo nome de arquivo).

Guia operacional: [fluxo-implementacao.md](fluxo-implementacao.md).

## Quando produzir

| Momento | Ação |
|---------|------|
| **I5** (início ou fim) | Criar ou atualizar o `.md` em **`executada/`** — consolida o que foi implementado |
| **I6** | Subagente valida código vs **plano**; registrar em `## Validação do código` |
| **I6-rev** | Especialistas revisam o **diff** por gatilho (segurança **obrigatória** se houve segurança em I1-rev); registrar em `## Revisões de especialistas (código)` no **`_processo-revisoes.md` interno** (regras.md § 11) |
| **I7–I10** | Acrescentar resultados de testes (E2E, local URL), passos condicionais avaliados |
| **I11** | Subagente valida HTML local; registrar em `## Validação do HTML local` |
| **I15** | Subagente valida HTML homol; registrar em `## Validação do HTML homol` |

O documento em **`executada/`** é o registro **oficial pós-código** do card. O plano em **`plano/`** permanece **congelado** após **I2-val** (alterações de escopo exigem nova rodada I2 no `.md`, novo `plano.html` em I2-html e nova I2-val).

## Conteúdo mínimo

- **Referência ao plano aprovado:** link para `docs/implementacoes/plano/impl-*.md` (I2-val aprovada)
- Referências a fluxo, análise e evidências (links)
- **Alterações realizadas** — tabela arquivo/função/status (o que de fato entrou no diff)
- **Plano executado** — passos concluídos vs ordem do plano; passo 7 / condicionais com decisão
- **Critérios de aceite** — AC1…ACN com status e referência a testes
- **Testes E2E** — resultado I7 (N/N pass), link para `testes-e2e.md`
- **Testes local URL** — resultado I10 (N/N pass), matriz resumida
- Registro de I6-rev **no `_processo-revisoes.md` interno**, não neste `.md` (regras.md § 11)
- Secção **`## Validação do código`** (I6)
- Secção **`## Validação do HTML local`** (I11)
- Secção **`## Validação do HTML homol`** (I15)

## Revisões de especialistas (código) — I6-rev, no `_processo-revisoes.md` interno

Dentro do I6, antes de fechá-lo. Gatilhos sobre o **diff** (lista em [fluxo-implementacao.md](fluxo-implementacao.md#ciclo-i6-rev--revisões-de-especialistas-sobre-o-diff)); a revisão de **segurança** é **obrigatória** quando houve revisão de segurança em **I1-rev** (o diff cumpre o que o plano decidiu?).

O documento oficial **não cita agente da frota** (regras.md § 11): a tabela `Especialista ·
Veredito · Ponto · Onde foi acatado` entra no **`_processo-revisoes.md` da pasta do card**, nunca
neste `.md`.

Fechar com **uma** linha: *“Gatilhos avaliados e não disparados: …”*. Aqui também se **reconfere** o checklist de `## Conformidade e segurança` do plano — item que virou `Pendência` no plano precisa estar resolvido ou explicitamente mantido com motivo.

## Validação do código (I6)

Subagente compara **diff/código** com o **plano em `plano/`** (não altera o plano).

1. Registrar rodadas em `## Validação do código` no `.md` de **`executada/`**.
2. **Aprovado** → I7.

Detalhes: [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i6).

## Validação do HTML local (I11)

Subagente compara `evidencias.html` com **análise**, **plano (`plano/`)** e resultados registrados em **`executada/`**.

1. Registrar rodadas em `## Validação do HTML local` no `.md` de **`executada/`**.
2. **Aprovado** → Pós-I11 (entregar HTML + comando de postagem ao usuário) → I12.

Detalhes: [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i11).

## Relação plano × executada

| Aspecto | `plano/` | `executada/` |
|---------|----------|--------------|
| Etapa | I1, I1-rev, validação I2-val | I5–I11 |
| Conteúdo | O que **será** feito (detalhado) | O que **foi** feito + testes + validações |
| Revisões de especialistas | `_processo-revisoes.md` interno (I1-rev, sobre o plano) | `_processo-revisoes.md` interno (I6-rev, sobre o diff) |
| Validação subagente | `## Validação do plano` (I2-val — gate do I4) | `## Validação do código` (I6), `## Validação do HTML local` (I11), `## Validação do HTML homol` (I15) |
| Alteração após I2-val | Só com revalidação I2-val | Atualizado até I15 |
