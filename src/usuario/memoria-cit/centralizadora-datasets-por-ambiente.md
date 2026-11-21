---
name: centralizadora-datasets-por-ambiente
description: Base Centralizadora — mesmo projeto e mesma service account em homol e produção; muda só o dataset (homologacao_centralizador vs gold_centralizador)
metadata:
  type: project
---

O CIT lê a `tabela_centralizadora_assinaturas` no projeto GCP `solides-ai-data-dw`
nos dois ambientes; o que muda é apenas o dataset:

- homologação → `homologacao_centralizador`
- produção → `gold_centralizador`
- local → sem credencial configurada (`BASE_CENTRALIZADORA_*` ausentes no `.env`)

A service account é a mesma nos dois: `svc-ticorp-consultacentralizad@solides-ai-data-dw.iam.gserviceaccount.com`,
com a **mesma** `private_key_id` e a **mesma** chave privada — quem tem a credencial
de homologação lê produção. Timeout de 15s.

Consequência prática: nunca tratar "consegui ler homol" como prova de que produção
está isolado; e qualquer vazamento da chave de homol atinge produção.
Confirmado em 25/08/2026 pelos `.env` dos dois ambientes.

Relacionado: [[credenciais-integracoes-cit]], [[massa-cancelamento-tres-fontes]],
[[cancelamento-produtos-novo-desenho]].
