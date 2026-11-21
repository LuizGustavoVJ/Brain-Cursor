---
name: regras-de-trabalho
description: >-
  Rigor de escopo, repositório permitido, gate de card de sustentação e ciclo de
  implementação de código. Use ANTES de I5 (leitura completa obrigatória, inclusive
  o arquivo de referência), ao decidir se pode ler/copiar/alterar arquivo de outro
  repositório, ao receber card ou incidente de sustentação, e sempre que aparecer a
  dúvida "isso está no escopo?" ou "posso mexer nisso?".
---

# Regras de trabalho — escopo, repositório e código

> **Checkpoint I5.** Antes de **qualquer** alteração de código, ler esta skill por completo,
> incluindo [escopo-e-permissoes.md](escopo-e-permissoes.md). Limite de escopo registrado aqui
> tem prioridade sobre suposição do agente.

**Contexto:** a equipe atua na **sustentação da operação antiga** — é daí que vem o gate por card
(L0 → B0 → S1–S6 ou I1–I15), e não de burocracia. Quem executa a etapa é sempre um agente da
frota; esta skill diz o que **não** pode variar de card para card.

## As regras que existem só aqui

| # | Regra | Erro que ela evita |
|---|-------|--------------------|
| 1 | **Escopo completo dentro do repo aberto** — implementar **todos** os touchpoints mapeados na demanda. Exclusão só vale se registrada na análise/plano **e** aprovada pelo humano. | Entregar metade do card alegando "só o que foi pedido" |
| 2 | **Consultar outro repositório é livre** — ler é sempre permitido, e **copiar/adaptar para dentro do workspace aberto não exige permissão nenhuma**. Permissão é só para **alterar** arquivo de fora. | Parar e pedir autorização para uma leitura |
| 3 | **Regra explícita da demanda é literal** — texto de aceite, integrações, textos de tela, **nomes de propriedade** e chaves de payload saem exatamente como o card definiu. | "Melhorar" o nome de um campo e quebrar o contrato |
| 4 | **Código em I5 é incremental** — passo a passo, só o estritamente necessário conforme o plano aprovado; sem invenção, sem melhoria não pedida, **sem refatoração desnecessária**. | Diff de 800 linhas para um card de 20 |
| 5 | **Correção não dispensa revalidação** — documento ou código ajustado após recusa em **I2-val, I6, I11 ou I15** volta ao subagente validador. | Corrigir, seguir em frente e o gate ficar aprovado sobre a versão antiga |

Detalhe, exemplos e o checklist do checkpoint I5: [escopo-e-permissoes.md](escopo-e-permissoes.md).

## O que **não** está aqui (fonte única em outro lugar)

Não copiar nada disto para cá — tabela repetida vira contradição na primeira divergência.

| Assunto | Fonte única |
|---------|-------------|
| Gates de cada etapa, proibições, bifurcação B0, propagação do Brain | **`fluxo-completo.md`** § *Tabela mestra* / § *Proibido* · **AGENTS.md** § *Regras de escopo* / § *Propagação do Brain* |
| Etapas, modos plan/agent, gatilhos de especialista, orçamento de contexto | [`fluxo-completo.md`](../../fluxo-completo.md) |
| Idioma, ADO, git, banco por ambiente, verificação, retorno de 15 linhas | [`frota/regras.md`](../../frota/regras.md) |
| Como conduzir o card etapa por etapa | skill [solides-sustentacao](../solides-sustentacao/SKILL.md) |
