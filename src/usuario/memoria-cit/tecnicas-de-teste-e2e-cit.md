---
name: tecnicas-de-teste-e2e-cit
description: "Técnicas de teste no cit: baseline de regressão exige limpar cache de autoload + application/ da cópia; teste de tela/URL tem de ser QA ponta a ponta com dado real do banco (nunca massa fabricada); formulário de cancelamento é capturável em tela real via URL local semeando a sessão CIT (não é forjar login unificado)"
metadata:
  node_type: memory
  type: project
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:04:47.794Z
---

Consolida `baseline-de-teste-cache-autoload`, `teste-url-deve-ser-qa-real` e
`form-cancelamento-via-url-local-semear-sessao` (destilação de 25/09/2026).

**Baseline de regressão contra o HEAD** — rodar a suíte duas vezes (código atual e HEAD; um processo
só não fecha nem no HEAD por contaminação de estado entre testes). Montar a cópia do HEAD tem 3
armadilhas medidas: (1)
`vendor/kenjis/ci-phpunit-test/application/tests/_ci_phpunit_test/tmp/cache/autoload.php` guarda
**caminhos absolutos** — copiado junto, o "baseline" carrega as classes do código alterado; apagar
antes. (2) `docker cp <dir>` **mescla** em vez de substituir — `rm -rf <copia>/application` antes de
copiar. (3) Usar o `vendor/bin/phpunit` **da própria cópia** (o original dá "Cannot redeclare
composerRequire"). Sem os três, o placar mente nos dois sentidos.

**Todo teste de tela/URL é QA ponta a ponta, nunca captura de estado montado.** Fluxo completo por
cenário alterado: abrir a tela real → exibir/acionar o que a demanda mudou (ex.: tooltip) →
preencher → enviar/submeter → conferir o retorno real (mensagem, redirect, gravação no banco,
integração disparada). **Dado tem de ser REAL, existente no catálogo** — massa sintética com nome
fabricado ("Produto Fixture A0x", "TESTE 167697 WL/COMUM") já foi barrada pelo usuário 3 vezes; se o
rótulo na tela não bate com o `BPRODUTOS` real, é sinal de texto fixo/fallback sendo exibido em vez
do dado — investigar antes de evidenciar.

**O formulário de cancelamento é capturável em tela real via URL local, sem precisar de homol** —
semeando a sessão do próprio CIT: a ação `semear_sessao` do harness E2E grava
`application/cache/ci_session<id>` já com `otp_cancelamento_autorizado=true` e as flashdata
necessárias (como `new`, não `old` — senão somem antes do render); o Playwright adiciona o cookie
`ci_session=<id>` e navega direto — a view real renderiza. **Isto é legítimo e diferente de forjar o
login unificado** (`UnifiedAuthenticationService`/`SessionHook`, que o classificador de segurança
barra) — semear sessão própria ≠ burlar autenticação de terceiro. Produto exibido precisa vir do
banco de verdade (sem `produtos_override` fabricado): resolver pelo CNPJ real da massa
(`aless608_sg_homol`), nunca por override no JS do teste. Antes de rodar, lembrar que o código de
produto e o harness (`testes/E2E`, untracked) precisam de `docker cp` para o container (código não é
bind mount).
