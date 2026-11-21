---
name: solides-sustentacao
description: >-
  Conduz cards e incidentes de QUALQUER repositório da frota Solides (cit,
  solides-crm, partners, checkout, omie-adapter, hubspot-adapter,
  gestao-adapter, debt-processing-service, payment-processing-service etc.)
  pelo ciclo de sustentação (S1–S6) e implementação (I1–I15) do Brain — não é
  exclusiva do Solides CRM, é a skill de processo que roda em todos os repos.
  Use sempre que o usuário mencionar card, incidente, sustentação, análise,
  plano, evidências, homol, deploy ou fluxo por card, em qualquer repositório
  aberto na IDE.
---

# Sustentação Solides — multi-repo

## Leitura obrigatória (projeto)

1. **L0** — o perfil `.cursor/arquitetura/ambiente-local-{projeto}.md` (§ Gate L0)
2. [fluxo-completo.md](../../fluxo-completo.md) — mapa C0 + L0 + B0 + S1–S6 + I1–I15 **e a tabela
   "Especialistas por etapa"**, que diz quem consultar dentro de cada gate
3. Skill [regras-de-trabalho](../regras-de-trabalho/SKILL.md) — escopo completo interno, repositório
   permitido, literalidade da demanda e o **checkpoint I5** (leitura obrigatória antes de codar)

**Cada etapa tem agente próprio** — despache em vez de fazer no contexto principal: `/card`
`/ambiente` `/requisitos` `/fluxo` `/analise` `/plano` `/dev` `/testar` `/evidencias` `/destilar`.
Quando o assunto exigir profundidade **dentro** da etapa, chame um dos especialistas (`frota.sh grupos`)
(`/frota <tema>`) — consulta é insumo do gate, nunca substituto dele. Catálogo e regras:
[`.cursor/frota/README.md`](../../frota/README.md).

## Sequência de entrada (C0 → L0 → B0)

1. **C0** — buscar o card no ADO (`mcp__azure-devops__wit_work_item`) e resumir no chat.
2. **L0** — subir app + BD e **informar a URL no chat**.
3. **B0** — perguntar *“SUSTENTAÇÃO ou IMPLEMENTAÇÃO?”* e **aguardar resposta explícita**:
   - **sustentação** → **S1** (mesma aba)
   - **implementação** → confirmar **(Y/n)** que S1–S6 serão pulados → **I1** (mesma aba)

**Proibido:** iniciar S1/I1 sem L0 ok, sem a resposta da bifurcação, ou (no caminho direto) sem o **(Y/n)**.

## Aba e contexto

**Aba única por card.** C0 → I15 na mesma aba: o principal só **orquestra** — despacha a etapa ao
agente dela e guarda **caminho do artefato + veredito de 15 linhas**. Abrir aba ou `/clear` é
**exceção cobrada pelo medidor**, e só no **corte de exceção do bloco**. Orçamento, blocos e regra
de `/compact`: **fonte única** em [`.cursor/fluxo-completo.md`](../../fluxo-completo.md)
§ *Aba única por card e orçamento de contexto*; quem mede e cobra é `.cursor/scripts/fase.sh` +
o hook `hook_contexto.py`. Não repetir número aqui — número repetido desatualiza e passa a
contradizer o medidor.

No handoff **S6b**, sinalizar no chat *“análise completa → implementação necessária, seguindo para
I1”* — a aba continua a mesma; aba nova só se o medidor cobrar.

## Modos de atuação

| Fase | Modo | Alterar código? |
|------|------|-----------------|
| **B0** | plan | **Não** — aguardar resposta |
| **S1–S6** | plan | **Não** |
| **I1–I4** | plan | **Não** |
| **I12** (gate deploy) | plan | **Não** — aguardar OK |
| **I5–I11, I13–I15** | agent | **Sim**, após I4 |

## Decisão S5

- **Análise suficiente** → S6a (sem I1–I15) → **Pós-S6a:** entregar no chat o `evidencias.html` (diagnóstico) + comando pronto `ADO_PROJECT=<GUID> python3 .cursor/scripts/ado_update_comment.py <html> <card>` — **quem posta no card é o usuário**
- **Implementação necessária** → S6b → **I1–I15** integral

## Gates críticos

- **S2-S4 consolidada (padrão):** subagente `validador-tecnico` valida fluxo **e** análise numa rodada · se separadas, **S2** vai no `validador-leve` (Haiku)
- **S6a-val** *(análise suficiente)*: subagente `validador-tecnico` valida o `evidencias.html` **consolidado** — **antes** de entregá-lo ao usuário (Pós-S6a). Último gate sobre o HTML: o agente **não** posta no card nem confere postagem
- **I2-val:** `validador-tecnico` (completa, `plano.html`) ou `validador-leve` (curta, plano curto) · **I6 / I11 / I15:** `validador-tecnico` (Opus) · teto de 3 rodadas por etapa; trilha curta/completa no B0 (`fluxo-completo.md` § Trilhas) — aprovação pelo agente **não conta**
- **I7:** E2E 100% pass
- **I9:** E2E no HTML — print Playwright + tabela “Detalhamento dos cenários” (padrão de referência)
- **I10:** local 100% pass (`test:local`)
- **I12:** OK explícito deploy homol
- **I13:** homol remota 100% pass + restaurar patches locais (comando no perfil `arquitetura/ambiente-local-{projeto}.md`)
- **I15:** encerramento — `evidenciashomol.html` aprovado

## HTML de evidências

| Arquivo | Conteúdo |
|---------|----------|
| `evidencias.html` | Diagnóstico + impl + **E2E (print+tabela)** + **local** L01–LN |
| `evidenciashomol.html` | **E2E (print+tabela)** + **homol** U01–UN |

## Entregáveis

| Tipo | Caminho |
|------|---------|
| Testes local (I11) | `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/testes-local.md` |
| Specs local | `testes/local/specs/{card-id}/` |
| Specs homol | `testes/homol/specs/{card-id}/` |
