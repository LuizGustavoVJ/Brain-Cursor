# Documento de análise e HTML de evidências

**Análise:** `docs/analises/{tipo}/{card-id}.md`  
**HTML:** `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html`  
**Imagens:** `docs/evidencias/assets/{tema-slug}/{card-id}-{Titulo-Slug}/{card-id}-qN.png`

Estrutura completa: [../arquitetura/estrutura-docs.md](../arquitetura/estrutura-docs.md)

## Quando produzir

**Depois** do fluxo aprovado.

## Documento de análise (MD)

- Levantamento técnico, impactos, arquivos, riscos, fora de escopo
- Título, subtítulo, índice, listas, tabelas quando útil
- Referenciar o fluxo em `docs/fluxos/{tipo}/`
- Apontar para HTML, imagens e anexos
- Registro de S3-rev **no `_processo-revisoes.md` interno**, não neste `.md` (regras.md § 11) — abaixo

## Revisões de especialistas (S3-rev) — no `_processo-revisoes.md` interno

A análise `.md` e o `evidencias.html` **não citam agente da frota** (regras.md § 11). O registro de
**S3-rev** vive no **`_processo-revisoes.md` da pasta do card** — arquivo interno não-entregável,
com **uma linha por especialista disparado** (gatilhos e forma de chamada:
[fluxo-por-card.md](fluxo-por-card.md) § *S3-rev*):

| Especialista | Veredito | Ponto (`arquivo:linha`) | Onde foi acatado |
|---|---|---|---|
| `especialista-financeiro-cobranca` | `Ajustar` | `application/...php:214` — ganho recalculado sem trava | § *Causa raiz*, item 3 |

- **Veredito** vem do retorno fixo do especialista: `Bloqueante`, `Ajustar` ou `OK`.
- **Onde foi acatado** aponta a seção da análise que mudou (ou `não acatado — por quê`).
- Fecha com **uma linha** para o que foi avaliado e não disparou:
  `Gatilhos avaliados e não disparados: …`.

**Gatilho disparado sem linha no `_processo-revisoes.md` é motivo de recusa em S4** — a validação não
aprova análise com revisão feita e não registrada, nem com gatilho aplicável e não avaliado.

## HTML de evidências (obrigatório)

Destinado à **área de negócios**:

- Estilos **inline**, pt-BR
- **Resposta ao incidente** e **proposta de solução no topo**
- **Resumo executivo em tabela** (duas colunas, `table-layout:fixed`, `word-wrap:break-word`, largura controlada ~480px)
- Evidências das queries e status da análise
- **Não incluir** caminhos internos `docs/` ou `.md` técnicos
- Imagens: caminhos relativos `../../../assets/{tema-slug}/{card-id}-{Titulo-Slug}/` — **não usar base64**
- Imagens no Azure DevOps: sobem pelo script de postagem (`ado_update_comment.py`, executado **pelo usuário** — ver [fluxo-por-card.md](fluxo-por-card.md) § Pós-S6a) — no HTML basta o caminho relativo do PNG em `assets/`

### Atualização após implementação (I9–I15)

Quando a análise registrou **implementação necessária**, **atualizar** o mesmo `evidencias.html` ao longo do ciclo:

| Etapa | Arquivo | Conteúdo no HTML |
|-------|---------|------------------|
| **I9** | `evidencias.html` | Plano executado, alterações, ACs, testes E2E (print + tabela) |
| **I11** | `evidencias.html` | Bloco **local** L01–LN (figuras + HTTP) + *(validação)* subagente vs esta análise + plano |
| **I14** | `evidenciashomol.html` | Bloco E2E (cópia I9) + bloco **homol** U01–UN, figuras, status operacional |

Guia: [documento-evidencias-html.md](../implementacao/documento-evidencias-html.md). Visão geral: [fluxo-completo.md](../fluxo-completo.md).

## Critério de conclusão

A análise **só finaliza** quando:

- Causa raiz **100% comprovada** (sem lacunas)
- **Resposta ao incidente** ou **proposta de solução** executável (passos, queries, rollback, verificação)
- Todas as consultas necessárias registradas nas evidências
- Pendências em seção **Em andamento** / **Pendências / próximas queries** até concluir

## Consultas ao banco

Quando exigir dados de BD: [consultas-bd.md](consultas-bd.md)

## Validação

Após elaborar análise (e HTML, quando aplicável), o agente **deve** submeter à validação do subagente **antes** de considerar a etapa concluída. Fluxo aprovado é pré-requisito. Se recusado: corrigir e **revalidar** até `Status: Aprovado`. Ver [validacao-subagente.md](validacao-subagente.md).

**Gate S6a-val (análise suficiente):** se o `evidencias.html` for atualizado após o S4 (resultados de queries de produção, inclusão/remoção de blocos), é **obrigatória** nova validação do HTML **consolidado** por subagente `validador-tecnico` **antes** de entregá-lo ao usuário para postagem (Pós-S6a). Não entregar/finalizar com o HTML sem essa conferência — o agente **não** posta no card.
