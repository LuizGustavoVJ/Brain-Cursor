---
name: card-161899-pagarme-pendencias
description: "Feature 161899 (cartão de crédito Pagar.me) ainda em andamento — autorização cross-repo + padrão de branches por release única, e migrations de homol viram documento consolidado em vez de execução direta"
metadata:
  node_type: memory
  type: project
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:05:48.240Z
---

Bundle de fatos que só valem enquanto a feature 161899 estiver aberta (destilação de 25/09/2026;
o desenho técnico já estável vive em `dominio-pagamento-cartao` e `dominio-termo-aceite`).

**Autorização cross-repo (exceção à regra geral do AGENTS.md, só para esta demanda):** trabalhar em
todos os repositórios de `/var/www/html`, não só `cit`. Padrão fixo por repo: `161899_release` a
partir da default branch atualizada, push sem alteração, branch de trabalho a partir da release com
o **mesmo nome em todos os repos**. A release **acumula a fase 1 inteira** — cada etapa nasce de
`origin/161899_release` (nunca de `staging`) e volta para ela por merge ao concluir; só vai para
`master` depois de todas as etapas prontas (MR de promoção fica em Draft até lá). Se faltar um repo
localmente, avisar o usuário para clonar — não clonar por conta própria.

**Migrations em homol não são executadas pelo agente nesta feature** (exceção à regra geral "local e
homol o agente executa"): DDL aqui toca schema de outro time (`aless608_sg_homol`) e exige janela de
quem administra o banco. Rodar tudo no MySQL local sem perguntar; para homol, consolidar as
migrations da fase num documento único em `docs/implementacoes/` (ordem, schema, DDL, rollback,
pré-condições, consulta de conferência) para o responsável de infra/BD executar quando disponível.
Nunca DDL direto em homol ou produção nesta feature.
