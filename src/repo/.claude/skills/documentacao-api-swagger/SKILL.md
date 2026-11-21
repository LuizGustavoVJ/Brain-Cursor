---
name: documentacao-api-swagger
description: >-
  Estado real da documentação de API do CIT e como produzir spec em padrão de
  mercado (OpenAPI/Swagger, AsyncAPI, JSON Schema, ADR). Use ao publicar
  endpoint, documentar integração, reativar o Swagger UI do repositório ou
  decidir entre spec estático e spec gerado por anotação. Aplica-se ao
  repositório cit.
---

# Documentação de API — Swagger no CIT

Conferido contra o código em 2026-08-21. Cada afirmação tem âncora `arquivo:linha`. Ao divergir
do código, **o código manda** e esta skill deve ser corrigida no mesmo card.

## O achado que muda a conversa

A documentação de API do CIT está **instalada e desligada**. Não é um repositório sem
documentação: é um repositório com o ferramental completo, nunca ligado.

| Fato conferido | Âncora |
|---|---|
| `zircote/swagger-php ^2.0` está em **`require`** (produção, não dev); instalada 2.0.16 | `composer.json:17` |
| A 2.x lê anotações com o prefixo **`@SWG\`** — `@OA\` é da 3.x e é rejeitado como *deprecated* | `vendor/zircote/swagger-php/src/StaticAnalyser.php:285`, `src/Analyser.php:25` |
| Não existe **nenhuma** anotação `@SWG`/`@OA` em `application/` | `grep -rl '@OA\|@SWG' application/` → vazio |
| O spec servido é o **exemplo de fábrica**: `"title": "My First API"`, 1 path fictício `/api/resource.json` | `application/third_party/swagger.json:4` |
| A UI existe e monta o spec a partir da variável `$urlDoc` | `application/views/swagger/index.php:42` |
| A rota que serviria a UI está **comentada** | `application/config/routes.php:169` |
| O controller `apidocs` **não existe** em `application/controllers/` | `ls application/controllers/ \| grep -i apidoc` → vazio |
| Ainda assim, `apidocs` é a **primeira entrada** da whitelist de classes públicas do `SessionHook` | `application/hooks/SessionHook.php:9` |

Assets da UI já versionados: `css/swagger/`, `js/swagger/`, `img/swagger/`,
`application/views/swagger/oauth2-redirect.html`.

## As três saídas — a escolha é do usuário, não sua

| Saída | O que exige | Quando vale |
|---|---|---|
| **A — religar como está** | criar `application/controllers/apidocs.php` (passa `$urlDoc` para a view) e descomentar `routes.php:169` | quer UI navegável rápido, aceita Swagger 2.0 |
| **B — spec estático versionado** | reescrever `application/third_party/swagger.json` à mão, sem UI | poucos endpoints, público interno |
| **C — migrar para OpenAPI 3.1** | subir `swagger-php` para 3.x/4.x (**troca `@SWG\` por `@OA\` em tudo**) ou gerar o spec fora do PHP | vai publicar para terceiro e precisa de ferramental atual |

**Antes de qualquer uma:** a rota `docs/apis/v1/(:any)` seria **pública** (classe `apidocs` está na
whitelist do `SessionHook`). Publicar spec de API interna sem sessão expõe o mapa das rotas —
decida a exposição junto com `especialista-seguranca`, não depois.

## Regras de spec que valem em qualquer saída

1. **Exemplo de erro é obrigatório**, não só o caminho felizes. O cliente programa o pior caso.
2. **Uma fonte da verdade**: ou anotação no código, ou arquivo à mão. As duas divergem em semanas.
3. **Spec no mesmo commit da mudança de contrato** — documentação em ferramenta separada envelhece.
4. Rota nova em `routes.php` sem entrada no spec = documentação já desatualizada no dia 1.
5. Evento e webhook (Pagar.me, HubSpot, Omie) **não** cabem em OpenAPI — isso é AsyncAPI ou uma
   tabela de payload com JSON Schema.

## Onde as rotas de API do CIT realmente vivem

`application/config/routes.php` — prefixos `api/v1/...`, `api/pagarme/...`, `api/subscription/...`,
`api/backoffice/...`, `termo-cancelamento/api/v1`, além de rotas soltas sem prefixo
(`registrar-ordem-servico-pagarme`, `processar-webhook-agendado`). **Não** existe um índice único:
qualquer inventário de API começa por ler `routes.php` inteiro.

## Agentes

`redator-tecnico` (produz o spec, o README e o runbook) · `especialista-integracao` (fecha o
contrato antes) · `especialista-seguranca` (decide a exposição da UI).
