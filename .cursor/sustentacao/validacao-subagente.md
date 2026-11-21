# Validação por subagente

Validação de **fluxo, análise e HTML final de sustentação** (quando S5 = análise suficiente, antes da entrega ao usuário). Para **plano, código e HTML final de implementação** (I2-val/I6/I11/I15) → [implementacao/validacao-subagente.md](../implementacao/validacao-subagente.md).

## Qual subagente usar

| Etapa | Subagente | Modelo | Por quê |
|-------|-----------|--------|---------|
| **S2** — fluxo | [`validador-leve`](../agents/validador-leve.md) | **Haiku** | Verificação estrutural: completude, coerência, referências existem no repo |
| **S4** — análise | [`validador-tecnico`](../agents/validador-tecnico.md) | **Opus** | Causa raiz e julgamento técnico |
| **S6a-val** — HTML final | [`validador-tecnico`](../agents/validador-tecnico.md) | **Opus** | Conferência visual e cruzamento com a análise |

**Não usar `general-purpose` para validar** — ele herda o modelo da sessão (Opus) mesmo em validação estrutural. Passar ao subagente o **caminho do arquivo**, nunca o conteúdo colado: ele lê com `Read`. Política: [otimizacao-custos.md](../otimizacao-custos.md) § *Subagentes*.

Se o `validador-leve` responder `Status: Escalonar`, reexecutar a mesma validação com `validador-tecnico`.

## Validação consolidada S2-S4 (padrão)

**Padrão em sustentação:** produzir **S1 (fluxo)** e **S3 (análise + HTML)** na mesma passada e submeter **uma única validação consolidada S2-S4** ao `validador-tecnico`, cobrindo os dois documentos. Na recusa, revalidar **somente o documento recusado**.

**Manter S2 e S4 separadas** (e registrar o motivo no chat) quando: incidente crítico ou com impacto em produção; o fluxo tem ambiguidade que muda a análise; ou o usuário pedir as duas rodadas. Nesses casos, S2 vai para o `validador-leve` e S4 para o `validador-tecnico`, como na tabela acima.

## Cache de validação

Antes de disparar o subagente, checar se o documento idêntico já foi aprovado:

```bash
python3 .cursor/scripts/cache_validacao.py check S4 docs/analises/{tipo}/{card-id}.md   # HIT → reaproveitar
python3 .cursor/scripts/cache_validacao.py save  S4 docs/analises/{tipo}/{card-id}.md Aprovado
```

Chave = `sha256(etapa + conteúdo)`, TTL 1h, só `Aprovado` é reaproveitado — qualquer byte alterado é MISS, então não há risco de reaproveitar veredito de outra versão.

> **Gate S6a-val (análise suficiente):** o `evidencias.html` **final** deve ser aprovado por subagente `validador-tecnico` **antes** de ser postado ou entregue ao usuário (Pós-S6a). A validação do S4 cobre a análise; se o HTML for atualizado depois (resultados de queries, remoção/inclusão de blocos), é **obrigatória** nova conferência do HTML consolidado antes de finalizar. Não há conferência depois da postagem (seja do agente após o "sim", seja do usuário), então o HTML precisa sair 100% pronto daqui.

Mapa completo: [fluxo-completo.md](../fluxo-completo.md).

---

## Ciclo obrigatório (regra)

Toda entrega de documento em `docs/` que exija validação segue este loop **até aprovação total**:

```
Agente elabora o .md
        ↓
Subagente valida (rodada N)
        ↓
    ┌─── Aprovado? ─── SIM ──→ Avançar próxima etapa do fluxo-por-card
    │
    NÃO (Recusado ou ressalvas bloqueantes)
        ↓
Mesmo agente que elaborou o documento aplica as correções sugeridas
        ↓
Atualiza secção ## Validação no .md (status, motivos, ações)
        ↓
Subagente valida NOVAMENTE (rodada N+1) — obrigatório após qualquer correção
        ↓
(repete até Status: Aprovado, sem pendências bloqueantes)
```

### Regras do ciclo

1. **Quem valida:** sempre o subagente da etapa (`validador-leve` em S2, `validador-tecnico` em S4/S6a-val), **nunca** o mesmo turno que acabou de escrever o documento sem passar pelo subagente.
2. **Quem corrige:** o agente que elaborou o documento (ou retoma a sessão com o mesmo contexto).
3. **Nova validação após correção:** **obrigatória**. Não avançar para análise, implementação ou código sem revalidar.
4. **Critério de saída:** `Status: Aprovado` na secção `## Validação` do `.md` — **sem** encerrar sustentação com “Aprovado com ressalvas” quando houver itens bloqueantes ou handoff para implementação pendente.
5. **Registro:** somente no próprio documento em `docs/` (secção `## Validação`) e no chat. **Não** criar arquivos paralelos em `.cursor/` para histórico de validação.
6. **Rodadas:** numerar no `.md` (Rodada 1, Rodada 2, …) quando houver recusa e correção.

### Por tipo de documento

| Documento | Quando validar | Pré-requisito | Guia |
|-----------|----------------|---------------|------|
| **Fluxo** | Imediatamente após etapa 1 | — | Este arquivo |
| **Análise** | Imediatamente após etapa 3 | Fluxo **aprovado** | Este arquivo |
| **HTML final (`evidencias.html`) — sustentação** | **S6a-val**, quando S5 = análise suficiente — **antes de entregar ao usuário** (Pós-S6a) | Análise **aprovada** (S4) + HTML **consolidado** (queries, resultados de produção, sem pendências) | Este arquivo |
| **Implementação (plano)** | Etapa **I2-val** — após S6b | Fluxo e análise **aprovados** (S4) | `docs/implementacoes/plano/` — [implementacao/validacao-subagente.md](../implementacao/validacao-subagente.md) |
| **Implementação (executada)** | Etapas **I6**, **I11** | I5 concluída / I10 concluída | `docs/implementacoes/executada/` — [implementacao/validacao-subagente.md](../implementacao/validacao-subagente.md) |
| **Código (pós-I5)** | Etapa I6 | Plano **aprovado** e I5 concluída | [implementacao/validacao-subagente.md](../implementacao/validacao-subagente.md) |
| **HTML final (`evidencias.html`)** | Etapa I11 | I7–I10 concluídas; HTML completo | [implementacao/validacao-subagente.md](../implementacao/validacao-subagente.md#ciclo-obrigatório-etapa-i11) |

**Análise:** ao concluir o `.md` (e HTML, quando aplicável), o agente **deve** disparar validação do subagente antes de apresentar como concluído ao usuário ou registrar a decisão de implementação.

**Plano de implementação:** validação na etapa **I2-val** — [implementacao/validacao-subagente.md](../implementacao/validacao-subagente.md). **I2-val é obrigatória** para todo card com implementação; não antecipar na sustentação.

---

## Critérios mínimos

- Fluxo/análise/implementação cobre o problema do card (sem lacunas)
- Referências a arquivos, rotas, métodos e integrações conferem com o código
- Sem suposições não fundamentadas (ambíguos → ponto de esclarecimento)
- Análise alinhada ao fluxo aprovado
- HTML de evidências existe, referencia imagens/anexos e está coerente com o `.md` *(quando exigido pelo card)*
- Queries usam tabelas/colunas reais (schema local); resultados de produção nas evidências
- Análise aprovada só com **100% do problema** + resposta ao incidente ou solução completa *(incidentes)*; ou proposta executável e As-Is conferido *(arquitetura/melhoria)*
- Decisão de implementação fundamentada na análise
- Plano resolve a causa raiz sem expandir escopo
- Escopo, riscos e fora de escopo coerentes

---

## Formato da secção `## Validação` (no `.md` em `docs/`)

Registrar **cada rodada** no documento validado:

```markdown
## Validação

### Rodada 1 (YYYY-MM-DD)

- **Status:** Recusado | Aprovado
- **Revisor:** subagente `validador-leve` (S2) ou `validador-tecnico` (S4/S6a-val)
- **Commit base:** `{hash}` (`git rev-parse HEAD`)
- **Motivos de recusa:** (lista objetiva; omitir se aprovado)
- **Ações corretivas:** (o que foi ou deve ser ajustado no documento)

### Rodada 2 — revalidação pós-correções (YYYY-MM-DD)

- **Status:** Aprovado
- **Revisor:** subagente `validador-leve` (S2) ou `validador-tecnico` (S4/S6a-val)
- **Commit base:** `{hash}`
```

Quando **aprovado na primeira rodada**, uma única subsecção basta.

---

## Após o resultado

| Resultado | Ação |
|-----------|------|
| **Aprovado** | Avançar para a próxima etapa em [fluxo-por-card.md](fluxo-por-card.md) |
| **Recusado** | Agente corrige o `.md` → **nova rodada** de validação (subagente) → repetir até 100% aprovado |

**Não existe "Aprovado com ressalvas"** — o resultado é binário: aprovado ou recusado. Se recusado, corrigir e revalidar até aprovação plena.

**Proibido:** avançar para a próxima etapa com documento em `Recusado`.
