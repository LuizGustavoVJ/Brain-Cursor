# Sustentação — fluxo por card

Card recebido segue **C0** (busca ADO) → **L0** (ambiente local) → **B0** (bifurcação). Quando o usuário declara **sustentação** em B0, o ciclo **S1–S6** abaixo roda na **mesma aba do card** (aba única é o padrão), **antes** de qualquer implementação de código.

**Mapa completo (C0 + L0 + B0 + S + I):** [fluxo-completo.md](../fluxo-completo.md).

**Implementação de código** (I1–I15) inicia por dois caminhos: após **S5 = implementação necessária** com handoff **S6b**, ou direto por **B0 = implementação** com o **(Y/n)** confirmado (pulando S1–S6).

---

## C0 · L0 · B0 — pré-requisitos

Os três pré-requisitos (buscar o card no ADO, subir o ambiente local, perguntar a bifurcação) têm
**fonte única**: [fluxo-completo.md](../fluxo-completo.md) §§ *C0*, *L0*, *B0*. Não estão repetidos
aqui de propósito — duas versões da mesma regra divergem na primeira mudança.

Resumo operacional: **C0** (resumo do card no chat) → **L0** (app + BD no ar, **URL no chat**) →
**B0** (usuário declara **SUSTENTAÇÃO ou IMPLEMENTAÇÃO**; se implementação, **(Y/n)** confirmando
que S1–S6 são pulados) → **S1** ou **I1** na mesma aba.

**Proibido:** iniciar **S1** antes de L0 operacional ou sem a resposta explícita da bifurcação.

---

## Ordem de entrega (sustentação)

| Etapa | Entrega | Pasta | Modo |
|-------|---------|-------|------|
| **S1** | Documento de **fluxo** | `docs/fluxos/{tipo}/{card-id}.md` | Plan |
| **S2** | Validação do fluxo (subagente) | — | Plan |
| **S3** | Documento de **análise** + **evidências em HTML** | `docs/analises/{tipo}/{card-id}.md` e `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html` | Plan |
| **S3-rev** | **Revisões de especialistas** por gatilho sobre a análise | `## Revisões de especialistas` no **`_processo-revisoes.md` interno** (não no `.md` da análise — regras.md § 11) | Plan |
| **S4** | Validação da análise (subagente) | — | Plan |
| **S5** | **Decisão do agente:** implementação necessária ou análise suficiente | Seção `## Decisão de implementação` no `.md` da análise | Plan |
| **S6a** | *(se análise suficiente)* Encerramento com recomendações ao usuário | — | Plan |
| **S6a-val** | *(se análise suficiente)* **Validação do `evidencias.html` consolidado** por subagente `validador-tecnico` — antes da entrega | Seção `## Validação` no HTML/`.md` | Plan |
| **Pós-S6a** | *(se análise suficiente)* **Entregar no chat** o caminho do `evidencias.html` + GUID do projeto + **comando pronto** de postagem — **só após S6a-val aprovada**. Pergunta **posto eu ou entrego o comando?** e posta só com "sim" | comando `ADO_PROJECT=<GUID> python3 .claude/scripts/ado_update_comment.py <html> <card>` | Plan |
| **S6b** | *(se implementação necessária)* **Handoff** para ciclo **I1–I15** | [implementacao/fluxo-implementacao.md](../implementacao/fluxo-implementacao.md) | Plan |

**Checklist S1–S5 (+ I1–I15 se S6b):** [fluxo-completo.md](../fluxo-completo.md#checklist-rápido--antes-de-avançar).

### S3-rev — conferência dos gatilhos da análise

**O gatilho já disparou antes daqui.** Ele é por **artefato**: a consulta SQL que você escreveu na
análise, a rota que citou, o número de dinheiro que apurou — cada um chamou o especialista da classe
**no momento em que foi produzido**, e [`hook_gatilhos.py`](../scripts/hook_gatilhos.py) cobrou na
hora. O S3-rev é onde você **confere** que todos foram respondidos e registrados, não onde você
lembra deles.

**Tabela de gatilhos: uma fonte só** — [`frota/gatilhos.tsv`](../frota/gatilhos.tsv), via
`.claude/scripts/frota.sh gatilhos`. Aqui não há cópia. Mecanismo, formato de retorno e limites:
[`frota/gatilhos.md`](../frota/gatilhos.md).

**Antes de submeter ao S4, confira:**

1. Toda consulta SQL da análise passou pelo `especialista-sql` — inclusive as que o **usuário** vai
   rodar em produção. Query entregue sem essa passagem é falha de processo.
2. Cada especialista disparado tem **uma linha** em `## Revisões de especialistas` do
   **`_processo-revisoes.md` interno** (nunca no `.md` da análise — regras.md § 11):
   `<agente> · OK|Ajustar|Bloqueante · ponto · onde foi acatado`
   (formato em [documento-analise.md](documento-analise.md)).
3. Os que não dispararam entram em **uma única linha** ao fim da mesma seção:

```
Gatilhos avaliados e não disparados: dado exposto/rota pública (a análise não expõe dado nem rota).
```

Fan-out **na mesma mensagem**, sempre com o **caminho** da análise — nunca o conteúdo colado.
Sem essa seção, o `validador-tecnico` recusa o S4.

**Proibido:** entrar em **S4** com gatilho disparado e sem linha registrada — é motivo de **recusa**
na validação. Especialista é insumo da etapa: não substitui **S4** nem dispensa gate.

### Após S6b — implementação obrigatória integral

Todo card com **implementação necessária** percorre a trilha confirmada no B0 — completa:
**I1 → I2-val → … → I15**; curta: `fluxo-completo.md` § *Trilhas* — sem pular etapa da trilha
escolhida. Checklist: [fluxo-completo.md](../fluxo-completo.md#checklist-rápido--antes-de-avançar).

**Passagem S→I (o que sinalizar no chat):**

1. *“Análise completa → implementação necessária (S6b)”*
2. Seguir na **mesma aba do card**; `/clear` só se o medidor cobrar, no corte de exceção do bloco.
3. Iniciar **I1** (plano) referenciando o fluxo e a análise já aprovados.

---

## Validação entre etapas (sustentação)

**S2-S4 consolidada** (padrão) exige subagente `validador-tecnico`; quando separadas, **S2** vai no `validador-leve` (Haiku) e **S4** no `validador-tecnico` (Opus). **Após qualquer recusa ou correção**, nova validação é obrigatória. Ciclo: [validacao-subagente.md](validacao-subagente.md).

Validação do **plano de implementação** (I2-val) → [implementacao/validacao-subagente.md](../implementacao/validacao-subagente.md).

---

## Modo de operação (plan × agent)

| Modo | Escopo | O que inclui |
|------|--------|--------------|
| **Plan** | Sustentação **S1–S6** + implementação **I1–I4** | Documentação, análise, plano, validações, OK. **Não** altera código. |
| **Agent** | Implementação **I5–I11**, **I13–I15** | Código, validação pós-código, E2E, local, homol, HTMLs, validações. |

Se **S5 = análise suficiente** (**S6a**), o ciclo **I1–I15 não se aplica**.

---

## Decisão de implementação (S5 — agente)

Após fluxo e análise **aprovados** (**S4**), o **agente** avalia se é necessário **ajuste em código** ou se **somente a análise basta**. A mesma regra vale para **todos** os cards.

Registrar no chat e na seção `## Decisão de implementação` do documento de análise:

| Resultado | Próximo passo |
|-----------|---------------|
| **Análise suficiente** | **S6a** — apresentar conclusão e recomendações. **Não** alterar código. **S6a-val:** validar o `evidencias.html` consolidado por subagente `validador-tecnico`. **Pós-S6a:** só após aprovado, **entregar no chat** o caminho do `evidencias.html` e o comando pronto `ADO_PROJECT=<GUID> python3 .claude/scripts/ado_update_comment.py <html> <card>` para o **usuário** postar — o agente **não** posta no card. |
| **Implementação necessária** | **S6b** — iniciar [ciclo de implementação](../implementacao/fluxo-implementacao.md) em **I1**. |

---

## Guias por tipo de documento (sustentação)

| Documento | Guia |
|-----------|------|
| Fluxo | [documento-fluxo.md](documento-fluxo.md) |
| Análise + HTML | [documento-analise.md](documento-analise.md) |
| Validação subagente (fluxo/análise) | [validacao-subagente.md](validacao-subagente.md) |
| Consultas BD | [consultas-bd.md](consultas-bd.md) |
| Resposta no chat (sustentação) | [resposta-chat.md](resposta-chat.md) |

Plano de implementação e execução de código → [`.claude/implementacao/`](../implementacao/).

---

## Exceções

Não exigem fluxo/análise prévios:

- Perguntas conceituais ou leitura de código sem mudança (não exigem C0, L0 nem B0).
- Quando o usuário pedir **explicitamente** pular o fluxo, a análise ou ir direto à implementação.
- **B0 = implementação** com o **(Y/n)** confirmado — S1–S6 pulados por decisão explícita do usuário; o ciclo começa em **I1**.
