---
name: nunca-apagar-recurso-externo-sem-backup
description: "Nunca apagar recurso externo (Postman, HubSpot, etc.) numa limpeza/dedup sem antes baixar e salvar o conteúdo; e não chamar de lixo o que eu não provei ser lixo"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1d174958-0e6f-4587-9207-ab6de3756d17
  modified: 2026-09-17T15:14:02.522Z
---

Ao limpar duplicatas ou "lixo" em serviço de terceiro (Postman, HubSpot, ADO, qualquer API), **NUNCA deletar sem antes fazer GET do recurso e salvar o conteúdo em arquivo**. Delete em environment do Postman é **irreversível** (a API responde 404 e não há restore; o Trash do Postman guarda collection, não environment).

**Incidente (17/09/2026):** apaguei um environment chamado `env` (uid `53116224-6ba0eae7-...`) achando que era lixo do script não-idempotente. Estava **errado**: meu script sempre nomeia o environment como `Homol — Cancelamento SENSE`, nunca `env` → o `env` já existia antes, era do Luiz. Apaguei sem ler o conteúdo. Ficou irrecuperável e não sei o que tinha dentro. O Luiz teve que me cobrar.

**Como agir:**
- Antes de qualquer DELETE em terceiro: `GET` o recurso, salvar o JSON num arquivo (docs/ ou backup datado), **depois** apagar.
- **Não** classificar algo como "lixo/duplicata" sem prova objetiva de origem. Se o nome não bate com o que eu mesmo criei, **é de outra pessoa** — não é meu pra apagar.
- Em dedup: manter o mais recente/completo, mas só depois de baixar TODOS os candidatos.
- Depois do incidente: **não apago mais nada em terceiro sem OK explícito do Luiz**, mesmo duplicata óbvia. Ver [[pedir-permissao-antes-de-escrita-externa]] e [[postman-chave-privada-do-luiz]].

**Why:** apagar sem backup destrói dado do usuário de forma irreversível e quebra a confiança. O ganho de "limpar" nunca paga o risco de perder algo real.

**How to apply:** o `push-para-postman.py` faz dedup automático (deleta duplicatas por nome) — isso agora é perigoso; antes de rodar dedup, baixar cada duplicata. Idem para qualquer upsert idempotente que delete.
