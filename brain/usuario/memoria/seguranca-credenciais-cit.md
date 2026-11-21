---
name: seguranca-credenciais-cit
description: "Levantamento de credenciais do CIT vive em docs/credenciais-integracoes.md (233 chaves/62 segredos no .env.example, só 2 preenchidas local); 3+ segredos reais estão versionados em código (constants.php:172/:174, payment-processing-service/.env.example, omie-adapter) — corrigir exige card próprio de rotação, nunca por iniciativa do Brain"
metadata:
  node_type: memory
  type: project
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:05:02.695Z
---

Consolida `credenciais-integracoes-cit` e `segredo-versionado-payment-processing-service`
(destilação de 25/09/2026).

**Levantamento completo em `docs/credenciais-integracoes.md`** — por integração: variáveis,
`arquivo:linha`, tipo de autenticação, pedido pronto e para quem pedir. `.env.example` tem 233
chaves/62 segredos; o `.env` local só preenche 2 (`MIDDLEWARE_HUBSPOT_API_V1_TOKEN`,
`TERMO_CARTAO_WEBHOOK_SECRET`) — é por isso que nenhum cliente de API de terceiro pode ser testado
de verdade hoje: falta credencial, não falta código. Antes de dizer que uma integração "não dá para
testar", conferir esse documento. `application/config/constants/gcp.php` lê 6 variáveis `GOOGLE_*` +
3 `CODPRODUTO_*` que **não existem** no `.env.example` — achado à parte.

**Segredos reais dentro de código versionado (não copiar/usar, não é exemplo):**

| Onde | O que | Registrado |
|---|---|---|
| `cit/application/config/constants/solidesapi.php:40` | `API_TOKEN` literal | único do CIT em git |
| `cit/application/config/constants.php:172` (CRM) e `:174` (fallback CHECKOUT) | tokens do Wilker (06/09/2026) | `docs/credenciais-integracoes.md` §12 |
| `omie-adapter/src/app/Enums/SolidesService.php` | token CIT | idem |
| `payment-processing-service/.env.example` | `HUBSPOT_API_TOKEN` real, commit `d592b66` (21/08/2023) | `.claude/arquitetura/estado-projeto-payment-processing-service.md` |

`.env.example` existe para ter chave **vazia** — token real ali fica no histórico de todo clone, e
quem copia o exemplo para `.env` usa produção sem perceber. **Corrigir qualquer um desses (rotacionar
+ esvaziar o exemplo) exige card próprio** — muda valor em todos os ambientes que usam o token; não
entra de carona em outro card nem por iniciativa do Brain.
