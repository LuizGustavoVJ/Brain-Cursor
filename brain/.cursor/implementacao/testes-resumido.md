# Saída resumida de testes (I7, I10, I13)

Como executar as suítes sem despejar o stdout do Playwright no contexto. Vale para **I7** (E2E),
**I10** (local) e **I13** (homol).

Política geral: [otimizacao-custos.md](../otimizacao-custos.md) § *Playwright*.
Execução das suítes: [testes-e2e.md](testes-e2e.md) · [testes-local.md](testes-local.md) ·
[testes-homol.md](testes-homol.md).

---

## Como rodar

```bash
.claude/scripts/resumo_testes.sh e2e     # I7  — equivale a: cd testes && npm run test:e2e
.claude/scripts/resumo_testes.sh local   # I10
.claude/scripts/resumo_testes.sh homol   # I13
```

O wrapper roda o mesmo `npm run test:*`, grava o stdout completo em
`.claude/cache/logs-testes/{alvo}-{timestamp}.log` e devolve ao contexto apenas:

- a linha de cada cenário (`✓` / `✘`), truncada em 140 colunas;
- o sumário `N passed (Xs)`;
- se falhou, as primeiras 40 linhas do bloco de erro;
- o caminho do log.

Código de saída = o do `npm`. **`0` continua sendo o gate de 100% pass** — nada muda no critério.

Abrir o log completo **só** quando o trecho de falha não bastar para diagnosticar.

---

## O que entra e o que não entra no contexto

| Entra | Não entra |
|-------|-----------|
| Resultado final `N/N` + tempo total | Stdout completo do Playwright |
| Tabela “Detalhamento dos cenários” | Output por assertion / passo |
| Print do relatório Playwright (`{card-id}-e2e-playwright.png`) | Print de cenário que passou e não está na matriz do plano |
| Prints dos cenários **da matriz do plano** (L01–LN / U01–UN) | Trace, vídeo, HTML report inteiro |
| Bloco de erro dos cenários que falharam | Logs de setup, warnings do Node, saída do `npm install` |

A matriz do plano (§ *Testes local/homol*) é o que define quais prints existem. Cenário fora
dela não vira figura — a regra já vale em I11/I15 e continua valendo aqui.

---

## Formato do registro (I8 / I11 / I14)

No `testes-e2e.md` / `testes-local.md` e no bloco do HTML, registrar assim — **não** colar o
stdout:

```markdown
## Execução

- **Comando:** `npm run test:e2e`
- **Resultado:** 12/12 pass (0 falhas) · 2min 45s
- **Data:** 2026-08-05
- **Log completo:** `.claude/cache/logs-testes/e2e-20260805-143012.log` (local, não versionado)

### Detalhamento dos cenários

| # | Cenário | Documento / entrada | AC | Resultado |
|---|---------|---------------------|----|-----------|
| 1 | ... | ... | AC1 | Pass |
```

O bloco E2E do HTML continua exigindo **print do relatório Playwright + tabela de detalhamento**
— isso não muda ([documento-evidencias-html.md](documento-evidencias-html.md)).

---

## Depois de cada suíte

Um hook `PostToolUse` ([`hook_pos_testes.py`](../scripts/hook_pos_testes.py)) dispara após
qualquer `test:e2e` / `test:local` / `test:homol` e injeta o lembrete de resumo + `/compact`.

Quem decide se a aba estourou é o **medidor** (`hook_contexto.py`) — orçamento em fonte única no
[fluxo-completo.md](../fluxo-completo.md) § *Aba única por card e orçamento de contexto*. Fim de
suíte é o melhor momento para compactar antes de I8 / I11 / I14. O que precisa sobreviver ao
compact: resultado N/N, caminhos dos prints capturados, tabela de cenários.

---

## Se o wrapper não servir

Rodar direto (`cd testes && npm run test:e2e`) continua válido — mas então **é responsabilidade
do agente** não reproduzir o stdout no chat: reportar só `N/N`, tempo e falhas. Redirecionar
manualmente também funciona:

```bash
cd testes && npm run test:e2e > /tmp/e2e.log 2>&1; echo "exit=$?"; grep -E '[0-9]+ (passed|failed)' /tmp/e2e.log
```
