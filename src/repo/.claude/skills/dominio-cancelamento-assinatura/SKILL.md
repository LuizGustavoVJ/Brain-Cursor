---
name: dominio-cancelamento-assinatura
description: >-
  Mapa de domínio do fluxo de cancelamento de assinatura do CIT — formulário público
  (OTP → produtos → bloqueio de perfil → submit), montagem de produtos por três fontes
  (CRM/centralizadora/login unificado), solicitação/reversão/efetivação por CODPRODUTO,
  integrações SenseData e Omie (suspensão/reativação de contrato) e a cascata de bloqueio
  GUSUARIO por IDEMP na carteira White Label. Use em qualquer card que toque
  formulario-de-cancelamento, forms_cancelamento, reversão/reativação de cancelamento,
  bloqueio de cancelamento por perfil (avulso/freemium/trial/WL), cron de efetivação, webhook
  SenseData ou suspensão/reativação de contrato no Omie. Aplica-se ao repositório cit.
---

# Domínio — Cancelamento de assinatura (CIT)

Conferido contra o código em 2026-09-25, working tree da branch `167697_fluxo_reativacao`
(cards 151281/166398/167697 — a mesma branch acumula as três entregas). Cada afirmação tem
âncora `arquivo:linha` ou função conferida por `grep`. Ao divergir do código, **o código manda**.

> Cobre o que acontece **dentro do cancelamento**. O gate de acesso ao formulário (login
> unificado, fallback partners/CRM, gate de perfil pulado por origem) é `dominio-login-unificado-partners`
> — não duplicado aqui, só referenciado.

## Visão geral do fluxo

`Otp_cancelamento` (OTP por e-mail, resolve CNPJs) → `Formulario_cancelamento` (lista produtos,
avalia bloqueio de perfil, recebe o submit) → grava `forms_cancelamento` (`status='aberto'`) →
`SenseDataCancelamentoService::processarFormularioCancelamento` (envia ao Sense, suspende contrato
no Omie quando é RH) → `Cron::efetua_cancelamento` (D+30, grava `DATA_CANCELAMENTO` em `ASSINATURAS`
e fecha o pedido) **ou**, para add-on não-RH, `Forms_cancelamento_model::marcarConcluidosNaoRhVencidos`
(D+30 sem contrapartida em `ASSINATURAS`).

## Produtos do formulário — três fontes (desenho ago/2026)

Duas camadas + fallback, todas **por CNPJ**, sem semântica "total/módulos" (removida):

| Camada | Fonte | O que traz |
|---|---|---|
| 1 — pai | `ASSINATURAS ⋈ BPRODUTOS` (CRM, `IDEMP=1`, `DATA_CANCELAMENTO IS NULL`, exceto `CATEGORIA='White Label'`) | produto do CRM, exibindo `BPRODUTOS.NOME` **cru** (decisão de negócio — nomes de plano, não nomes comerciais) |
| 2 — filho | Base Centralizadora (BigQuery, só linhas `ASSINANTE`/`INADIMPLENTE`) | add-ons por SKU (De-Para); `Sólides DP`, `Folha` e `Benefícios` só existem aqui, nunca em `BPRODUTOS` |
| 3 — fallback | login unificado / lista fixa | quando as duas primeiras não resolvem |

**Dois níveis apenas** — todo cliente com produto no CRM tem exatamente um pai; tudo que está
"dentro" dele é filho (não há caixa intermediária para DP/Folha/Benefícios). Marcar o **pai**
cancela ele + todos os filhos (a solicitação ao Sense leva a lista item a item, nunca só o pai);
marcar **um filho** cancela só aquele add-on. **White Label** é item único, só cancelamento total
(carimba todas as assinaturas de categoria White Label do CNPJ).

## Solicitação, reversão e efetivação — por `CODPRODUTO`, não por cliente

`Financeiro_model::processa_solicitacao_cancelamento($idclifor, $type, array $codProdutos = [], ...)`
([Financeiro_model.php:2421](../../../application/models/Financeiro_model.php#L2421)) e
`reverteSolicitacaoCancelamentoAssinatura($idCRM, array $codProdutos, $permiteSemFiltroDeProduto = false, ...)`
([Financeiro_model.php:3751](../../../application/models/Financeiro_model.php#L3751)) **já filtram
por `CODPRODUTO`** quando o array não vem vazio (`WHERE ... AND CODPRODUTO IN (...)` antes do
`UPDATE ASSINATURAS`) — o desenho item-a-item de 27/08/2026 está implementado. **Caveat:** se o
chamador passar `$codProdutos` vazio, o filtro não entra e o efeito volta a ser por cliente
inteiro — a garantia é do chamador, não do método.

Item do formulário só carrega `codprodutos` quando vem do CRM
(`Otp_cancelamento.php`); itens da centralizadora (`base:`/`base:json:`) e do login unificado
(`auth:`) nascem sem CODPRODUTO — por isso um pedido só de add-on (DP/Folha/Benefícios) não tem
contrapartida em `ASSINATURAS` e segue o caminho "não-RH" abaixo, não o cron de `ASSINATURAS`.

### Efetivação — dois caminhos, cada um com seu prazo

| Caminho | Quem efetiva | Regra de elegibilidade | Fecha o `forms_cancelamento` |
|---|---|---|---|
| **RH** (tem `ASSINATURAS`) | `Cron::efetua_cancelamento` ([Cron.php:161](../../../application/controllers/Cron.php#L161)), via `Financeiro_model::get_solicitacoes_cancelamento_assinaturas` ([:1952](../../../application/models/Financeiro_model.php#L1952)) — `DATEDIFF(CURRENT_DATE, DATA_SOLICITACAO_CANCELAMENTO) > 29` e `DATA_CANCELAMENTO IS NULL` | por **assinatura** (D+30 individual) | `Forms_cancelamento_model::marcarConcluidoPorPedidoDoProduto($cnpj, $codProduto)`, chamado em [Cron.php:184](../../../application/controllers/Cron.php#L184) — fecha **só o pedido daquele produto**, por `id` |
| **não-RH** (add-on sem `ASSINATURAS`) | `Forms_cancelamento_model::marcarConcluidosNaoRhVencidos(30)` ([:376](../../../application/models/Forms_cancelamento_model.php#L376)) | `processado_em <= hoje-30d` OU (`processado_em IS NULL` E `criado_em <= hoje-30d`); exige `possuiProdutoRh()=false` e `etapa='processado_sensedata'` | fecha o pedido, mas **não cessa cobrança** — a baixa real é manual, pelo time de retenção via deal do Sense |

`marcarConcluidoPorPedidoDoProduto` exige `status='aberto'` **e** `etapa='processado_sensedata'`
([Forms_cancelamento_model.php:456](../../../application/models/Forms_cancelamento_model.php#L456)
e a constante em [:21](../../../application/models/Forms_cancelamento_model.php#L21)). Um pedido
preso em `erro_sensedata` (ver seção Omie abaixo) nunca é candidato: efetiva no CRM/Omie mas o
`forms_cancelamento` fica `aberto` para sempre — falha de **registro/conciliação**, não de dinheiro
(a cessação de cobrança é por `IDASSINATURA`/`CODPRODUTO`, cortada direto em `ASSINATURAS`).

> **Histórico resolvido (não re-abrir):** até 09/09/2026 a efetivação RH usava
> `marcarConcluidoPorDocumento($cnpj)` — fechava **todos** os pedidos em aberto do mesmo CNPJ,
> inclusive os que não tinham completado 30 dias (vazamento de registro, card 166398). Esse método
> está **órfão hoje** (zero call sites); a chamada atual em
> [Cron.php:184](../../../application/controllers/Cron.php#L184) já é
> `marcarConcluidoPorPedidoDoProduto`. Não recomendar essa correção de novo.

## Bloqueio de cancelamento por perfil (card 151281) — implementado

Regra fechada e **em produção no código atual** — ver `dominio-login-unificado-partners` §"Gate de
perfil pulado por origem" para quando ela roda. `Formulario_cancelamento::avaliarBloqueioPerfil()`
([Formulario_cancelamento.php:351](../../../application/controllers/Formulario_cancelamento.php#L351))
recebe o retorno de `apiGestaoBuscaEmpresaPorEmail` e **itera as entradas casando pelo `cnpj`**
selecionado (um e-mail pode ter vários CNPJs — não usar `$base[0]`), fail-closed (http≠200, vazio
ou CNPJ não localizado → `indisponivel`). Critério, por precedência:

1. `whitelabel_id !== null` → grupo `white_label`.
2. `plano_software_template_id` ∈ `{15 Avulso, 214329 Freemium, 1 Trial, 113632 Pós-trial}`
   (`produtos_cancelamento_planos_bloqueantes`, [produtos_cancelamento.php:296](../../../application/config/produtos_cancelamento.php#L296)) → grupo `sem_contrato`.
3. Nenhum dos dois → `''`, não bloqueia.

Mensagens **verbatim** ([produtos_cancelamento.php:303-315](../../../application/config/produtos_cancelamento.php#L303-L315)) —
`indisponivel` reusa o texto de `sem_contrato` (só existem 2 grupos de texto):

| Grupo | Título |
|---|---|
| `white_label` | "Cancelamento com o seu fornecedor" |
| `sem_contrato` (e `indisponivel`) | "Não é necessário solicitar o cancelamento" |

**Implicação aceita pelo usuário:** cliente pagante durante instabilidade momentânea da API de
gestão vê a mensagem de "sem contrato ativo" (fail-closed técnico reusa o texto de negócio).

## Integração SenseData

- Contrato validado com o SenseData (Paulo Marcio, 03/09/2026): `id_legacy` tem **duas formas
  propositais** — CNPJ puro no `GET /v2/customers`, `CNPJ_idFormulário` no `POST /v2/custom_data`
  (`SenseDataCancelamentoService::montarCustomDataPayload`). `cs_retencao`/`cs_retencao_email`
  **não são obrigatórios** e o CIT não os envia.
- **O Sense é quem avisa o CIT**, não o contrário: efetivação e reativação de cancelamento **não**
  são enviadas ao Sense (eles já têm o dado dos dois lados) — é o Sense que manda ao CIT, via
  webhook, o desfecho da tratativa de retenção. Reduziu o escopo original do card 151281.
- `valor_mensalidade` (MRR) passou a ir no payload — fonte é a **Base Centralizadora** (BigQuery),
  valor **bruto** somado das linhas ativas (rh/dp/fl/ge/be), formato string `'100.00'`, campo
  **opcional** (omitido quando alguma linha ativa vier com valor NULL — decisão fail-closed do
  usuário, não estimar). Ver `centralizadora-datasets-por-ambiente` (memória) para o dataset por
  ambiente.
- **Autenticação do webhook `Sensedata_rest` já é case-insensitive e aceita os dois nomes de
  header** — `authorizationCheck()`
  ([Sensedata_rest.php:73](../../../application/controllers/Sensedata_rest.php#L73)) normaliza as
  chaves com `array_change_key_case(..., CASE_LOWER)` e aceita `X-Authorization` **ou** `Token`,
  ambos com prefixo `Bearer `. **Histórico resolvido:** havia um bug de ternário aninhado que só
  aceitava `Token: Bearer` e devolvia 401 com `X-Authorization` (não era proxy/infra) — já corrigido
  no código atual; não reabrir a hipótese de infraestrutura para 401 nesse endpoint sem antes ler
  este método.

## Integração Omie — suspensão e reativação de contrato

`possuiProdutoRh()` decide se o pedido mexe em contrato Omie
([SenseDataCancelamentoService.php:1004](../../../application/services/SenseDataCancelamentoService.php#L1004)
chama `Forms_cancelamento_model::possuiProdutoRh`,
[Forms_cancelamento_model.php:738](../../../application/models/Forms_cancelamento_model.php#L738)).

**Suspensão (na solicitação)** — `suspendeContratoOmie()`
([SenseDataCancelamentoService.php:507](../../../application/services/SenseDataCancelamentoService.php#L507)):
chama `alterarSituacaoContrato(CODSITUACAO=OMIE_CODIGO_STATUS_SUSPENSO=90)` e **em seguida confirma**
via `confirmaSituacaoContratoOmie()` ([:539](../../../application/services/SenseDataCancelamentoService.php#L539));
se `cCodSit` não vier 90, lança exceção
([:546](../../../application/services/SenseDataCancelamentoService.php#L546)) →
`Forms_cancelamento_model::marcarErroIntegracao()` grava a etapa `erro_sensedata`
([:791](../../../application/services/SenseDataCancelamentoService.php#L791), constante em
[Forms_cancelamento_model.php:21](../../../application/models/Forms_cancelamento_model.php#L21)).

> **Armadilha do rótulo:** a etapa `erro_sensedata` **não significa que o SenseData falhou** — o
> Sense já pode ter retornado 202 (sucesso) antes; o rótulo é genérico e mascara uma falha da
> **suspensão no Omie**. Ao investigar um pedido preso em `erro_sensedata`, checar o `citlog` da
> ação `sensedata_suspensao_contrato_omie` antes de culpar o Sense.

**Reativação** — `ReativacaoAssinaturaCanceladaLib::executaProcessamentoOmie()`
([ReativacaoAssinaturaCanceladaLib.php:324](../../../application/libraries/ReativacaoAssinaturaCanceladaLib.php#L324)):
chama `alterarSituacaoContrato(CODSITUACAO=OMIE_CODIGO_STATUS_ATIVO)` e também confirma com
`confirmaSituacaoContratoOmie()` — mas, diferente da suspensão, **se a confirmação falhar não lança
exceção**: só grava um log INFO dizendo "comportamento esperado de delay no processamento do Omie" e
**segue o fluxo normalmente** ([:345-352](../../../application/libraries/ReativacaoAssinaturaCanceladaLib.php#L345-L352)).

> **Contradição em aberto, não resolvida por este mapa:** documentação do Omie
> (ajuda.omie.com.br/articles/498986 e /10210984) trata cancelar/reativar como **ações de ciclo de
> vida dedicadas**, distintas do campo situação alterado por `alterarSituacaoContrato` — ou seja, um
> contrato já **cancelado** pode não voltar a `ATIVO` só com essa chamada, mesmo com HTTP 200. O
> código atual **assume que a não-confirmação é sempre delay**, nunca um falso-positivo permanente.
> Se um card relatar "reativei mas o contrato no Omie continua cancelado", **não descartar** essa
> hipótese só porque o log diz "delay" — confirmar a situação real do contrato no Omie antes de
> fechar.

### `nCodProj` — o que é "OS de RH" para o Omie

Identificação é por `nCodProj` (não por código de serviço), usado em
`application/controllers/api/Pagarme.php` (linhas 1525, 1598, 1654, 2641). Fonte para descobrir de
novo: `citlog` (banco `solides-pipedrive`), agrupar `acao='IncluirOS'` por `nCodProj` e ler
`cDescServ` — mais confiável que grep, porque as constantes vêm de `.env`.

| `nCodProj` | O que é | Cancela no cancelamento do cliente? |
|---|---|---|
| `2338125453` (constante `NCODPROJ`) | Crédito Recrutamento e Seleção, Crédito Vaga, RH Profiler | **sim** |
| `2746742460` | adesão/implantação | não |
| `2763119767` / `2998812143` / `2998813714` | Folha Digital (Essencial/Premium) | não |
| projetos de benefício (`OMIE_OS_PROJETO_CARTAO_BENEFICIO`, `NCODPROJ_CESTA_BENEFICIOS`) | benefícios | não |
| `3681982958` / `3681983040` / `3681983148` | projetos de **contrato** (`AlterarContrato`) | não é OS |

## Cascata GUSUARIO por IDEMP na carteira White Label — resolvido (card 167697)

**Modelo de negócio confirmado (PO Gustavo):** a carteira de clientes finais de um WL **compartilha
o IDEMP do parceiro** — `CCLIFOR.IDEMP` da carteira = `GEMPRESA.ID` do WL. Três pontos no código
faziam `UPDATE GUSUARIO ... WHERE IDEMP=?` sem filtrar `IDCLIFOR`, o que desativava a **carteira
inteira** ao bloquear/reativar o WL (confirmado por dado em homol e produção: em `GUSUARIO WHERE
IDEMP=<wl>`, linhas com `IDCLIFOR` preenchido são carteira, `IDCLIFOR IS NULL` são os admins do
próprio WL — separador provado em `solides-crm/application/models/modellogin.php:311`,
`logarProfile` exige `IDCLIFOR IS NOT NULL` para cliente final).

Os três pontos, hoje **todos corrigidos** com `WHERE IDEMP IN (<todos os tenants>) AND IDCLIFOR IS NULL`:

| # | Método | Chamado por |
|---|---|---|
| 1 | `setAtivoGusuarioWlPorIdemp` ([Financeiro_model.php:361](../../../application/models/Financeiro_model.php#L361)) | `BaseWhiteLabelLib::aplicaEstadoBaseWhiteLabel` — fluxo automático de cancelamento/reativação |
| 2 | `bloquear_whitelabel_clientes` ([:348](../../../application/models/Financeiro_model.php#L348)) | endpoint manual `financeiro/bloquear-whitelabel-clientes/<idclifor>`, botão da tela de inadimplentes |
| 3 | `bloquearClientesPorInadimplenciaNoCRM` ([:4099](../../../application/models/Financeiro_model.php#L4099)) | chamado em [CancelamentoClienteLib.php:647](../../../application/libraries/CancelamentoClienteLib.php#L647), bloqueio por inadimplência de qualquer cliente (não só WL); comentário no código rotula a variante como "VARIANTE-#3 (A)" — trocar para B só com aval do especialista de SQL |

`getIdsEmpresaPorIdclifor($idclifor)` ([:406](../../../application/models/Financeiro_model.php#L406))
traz todos os `GEMPRESA.ID` do IDCLIFOR (multi-tenant é real: um WL pode ter mais de uma linha em
`GEMPRESA` para o mesmo `IDCLIFOR`, ex. produção 4 tenants). `getIdEmpresaPorIdclifor` (singular)
exige `num_rows===1` e aborta calado em WL multi-tenant — não confundir os dois métodos.

**Ramo partners removido, não corrigido:** `setBloqueioUsuariosGestaoPartners` (escrevia
`usuarios_gestao` e também cascateava a carteira) foi **apagado** de `Cliente_model.php` — confirmado
ausente no código atual (zero ocorrências). O bloqueio do WL em `partners` segue só por
`empresas.status` (`setBloqueioDesbloqueioAcessoPartners`, por `idclifor`, seguro).

**O que já era seguro (nunca cascateava):** `SIDCONEXAO` e `GEMPRESA`
(`setAtivoGempresaPorIdclifor`, [:390](../../../application/models/Financeiro_model.php#L390),
sempre por `IDCLIFOR`) — a carteira não tem linha própria em `GEMPRESA`. **Não é risco de
cobrança:** a carteira do WL não tem `ASSINATURAS` própria (é servida por crédito que o parceiro
compra); risco é só de **acesso**.

## Reativação de assinatura — seleção manual e `DATA_DESVINCULO`

**Qual assinatura reativar (tela manual, card 167697):**
`ReativacaoAssinaturaCanceladaLib` recebe `idassinatura` no payload
([:154](../../../application/libraries/ReativacaoAssinaturaCanceladaLib.php#L154)) — a tela
propaga a linha marcada no checkbox, não mais a mais recente por padrão.
`Financeiro_model::getAssinaturaMaisRecente` (`IDASSINATURA DESC`) só é usado como **fallback**
quando o payload não traz `idassinatura`. Os webhooks automáticos (SenseData/Netsuite/HubSpot)
ainda mandam só `id_crm`, sem `idassinatura` — continuam no fallback "mais recente" (decisão de
produto pendente para esses canais, fora do escopo já entregue).

**`CCLIFOR.DATA_DESVINCULO`** é gravado (não é migration nova, coluna já existe e é usada por
processo legado externo) por `Financeiro_model::marcarDesvinculoSeSemAssinaturaAtiva($idclifor)`
([:2293](../../../application/models/Financeiro_model.php#L2293)) — `UPDATE CCLIFOR SET
DATA_DESVINCULO=NOW() WHERE ... AND DATA_DESVINCULO IS NULL AND NOT EXISTS (SELECT 1 FROM
ASSINATURAS WHERE IDCLIFOR=... AND DATA_CANCELAMENTO IS NULL)` — só grava quando **todas** as
assinaturas do cliente estão canceladas, é **idempotente** (guarda `IS NULL`) e é chamado nos
**dois** fluxos de efetivação: a cron de 30 dias e o cancelamento imediato pela tela do financeiro
([:2179](../../../application/models/Financeiro_model.php#L2179) e
[:2224](../../../application/models/Financeiro_model.php#L2224)). Reativação **zera
incondicionalmente** via `zerarDataDesvinculo()` ([:2312](../../../application/models/Financeiro_model.php#L2312))
— decisão de produto aceita mesmo sabendo que o legado externo às vezes preenche a coluna sem
relação com cancelamento (medido em produção: 64% dos `DATA_DESVINCULO` preenchidos tinham
assinatura ativa na mesma consulta) — o fluxo novo só zera quando é reativação de verdade; não
corrige o que o legado sujou.

**Só produto principal conta para o cálculo** — add-on (DP/Folha/Benefícios, vindos da Base
Centralizadora) não tem `CODPRODUTO`/linha em `ASSINATURAS` e nunca entra nesse `NOT EXISTS`;
cancelar um add-on é *downgrade*, nunca desvincula o cliente.

**Fallback de e-mail no OTP (item 4c) — ordem da cadeia:** login unificado → WL-partners
(`tipo='white_label'`) → **CRM `GUSUARIO` por último** (identidade canônica primeiro, legado por
último, fail-closed). A checagem de e-mail só decide se manda OTP (basta ≥1 `GUSUARIO` com
`ATIVO=1` e `IDCLIFOR IS NOT NULL`); a escolha do CNPJ é sempre do formulário, não do e-mail — não
vazar contagem/identidade de múltiplos CNPJs na resposta (risco de enumeração).

## Retry — só a solicitação de cancelamento tem cron de 10 tentativas

`Cron::reprocessa_cancelamentos_sensedata` ([Cron.php:361](../../../application/controllers/Cron.php#L361))
reprocessa `forms_cancelamento` (fila real; `etapas_fluxos_servicos` é só livro-razão de auditoria)
até `LIMITE_TENTATIVAS_SENSEDATA_CANCELAMENTO=10`
([constants.php:333](../../../application/config/constants.php#L333)); ao esgotar, marca
`falha_permanente_sensedata` + e-mail. **Reativação, reversão e ativação do cliente rodam 1x
transacional, sem retry por cron** (só retry HTTP inline de 3x dentro da chamada). Não supor que
"todo fluxo do cliente" tem a mesma cobertura de retry — reativação/reversão não têm.

## Como testar em homol

Massa por **3 fontes**, só 2 aceitam SQL direto:

1. **Login unificado** (Keycloak) — e-mail precisa existir e estar `enabled`; CNPJs vêm das
   organizações do usuário. Fonte confiável para achar e-mail de teste: **tabela `citlog`**
   (`disparado_por='OTP Cancelamento'`) — o `payload` de cada tentativa traz `email`,
   `motivo_interno` e, nos aprovados, `cnpjs`/`organizacoes`. `termo_aceite.dados_criacao_acesso`
   **não serve** (guarda o e-mail para o qual o CIT enviou acesso, não prova de usuário no Keycloak).
2. **CRM (MySQL homol)** — só o pai da linha `rh` e o White Label aceitam SQL/endpoint direto.
3. **BigQuery** (Base Centralizadora) — linhas `dp`/`fl`/`be`/`ge` e add-ons; a service account do
   CIT é só leitura, escrita exige time de dados (`MERGE`).

Receita de update em homol (via `.claude/scripts/homol.sh`, ver `bd-homol-nao-e-o-mysql-3309` na
memória):

```bash
bash .claude/scripts/homol.sh <select|update> <crm|db> <TABELA> "<SET ou campos>" [<WHERE col=val> ...]
```

- `crm` = banco CRM (`CCLIFOR`, `ASSINATURAS`); `db` = banco CIT (`forms_cancelamento`,
  `etapas_fluxos_servicos`). Só SELECT/UPDATE — sem DELETE/INSERT/DDL.
- Simular efetivação **não-RH** (30 dias): `UPDATE forms_cancelamento processado_em=<30+ dias
  atrás> id=<id>` (se `processado_em` já for NULL, envelhecer `criado_em` em vez disso) —
  **não mexer em `ASSINATURAS`**, esse é o caminho RH.
- Reversão de solicitação **não é SQL** — é webhook `POST
  https://homol.cit.solides.adm.br/sensedata/reverter-cliente-cancelado` →
  `Sensedata_rest::revertCancellationRequest`, header `Token: Bearer <SENSEDATA_WEBHOOK_API_TOKEN
  de homol>`, payload `{id_crm, cnpj, cs_responsavel, cs_responsavel_email}`. Age na última
  solicitação `aberto` do CNPJ, deixa em `retida`.

## Acervo — onde já foi estudado

| Assunto | Cards | Documento |
|---|---|---|
| Novo desenho de produtos | — | `docs/analises/cancelamento-produtos/` |
| Efetivação por CODPRODUTO (vazamento por CNPJ) | 166398 | `docs/analises/cancelamento-produtos/i1-plano-efetivacao-por-pedido-166398.md` |
| Bloqueio de cancelamento por perfil | 151281 | `docs/implementacoes/impl-151281-mensagem-bloqueio-cancelamento.md` |
| Envio de MRR ao SenseData | 151281 | `docs/implementacoes/impl-151281-envio-valor-mrr-sensedata.md`, `docs/analises/base-centralizadora/` |
| Reativação/desvínculo/OTP, cascata GUSUARIO | 167697 | `docs/analises/cancelamento-produtos/diferencas-doc-cancelamento-vs-codigo.md` |
| Reativação Omie falso-positivo | 166398/167697 | citlog homol (idclifor 80359, cCodIntCtr 2998) |

Busca no acervo: `.claude/scripts/kb.sh buscar <termo>`.

## Manutenção

Ao encerrar card deste domínio, atualizar: nova armadilha, correção do que o card provou diferente,
e reconferir a seção "Contradição em aberto" da reativação Omie assim que houver um caso real
resolvido (hoje é hipótese, não fato).
