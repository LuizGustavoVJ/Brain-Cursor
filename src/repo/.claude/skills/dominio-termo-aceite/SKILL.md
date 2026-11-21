---
name: dominio-termo-aceite
description: >-
  Mapa de domínio do termo de aceite do CIT — criação, visualização, aceite,
  roteamento Mid/Farmer por origin, integrações pós-aceite (HubSpot, e-mail,
  ganho) e pagamento via cartão. Use em qualquer card que toque termo de aceite,
  proposta/orçamento, calculadora comercial, ganho Mid/Farmer, validação de
  CNPJ/e-mail no termo, expiração de termo ou pagamento no aceite. Aplica-se ao
  repositório cit.
---

# Domínio — Termo de aceite (CIT)

Destilado do acervo de `docs/` (cards 152452, 156306, 156719, 157713, 158930, 161122, 162988, 163244, 165575) e conferido contra o código e o BD local em 2026-08-24. Cada afirmação abaixo tem âncora em arquivo:linha ou em consulta ao BD — **não** reescrever de memória; ao divergir do código, o código manda e esta skill deve ser corrigida.

## O que é

Documento gerado pelo vendedor na calculadora, enviado por link com token, visualizado e aceito pelo cliente. O aceite grava no banco, atualiza o negócio no HubSpot e dispara e-mail. O **ganho** (criação de cliente, assinatura e integrações) não acontece no aceite — é um webhook posterior do HubSpot quando o deal entra em *Fechado Ganho*.

## Roteamento por `origin` — a bifurcação central

`getTipoTermoAceite($origin)` ([termo_aceite_helper.php:271](../../../application/helpers/termo_aceite_helper.php#L271)) devolve a lib **Farmer** somente quando `origin === 'farmer'`. **Qualquer outro valor, inclusive NULL, cai no fluxo Mid.**

| Fluxo | Lib | Linhas |
|---|---|---|
| Mid/Vsb (default) | [CalculadoraTermoAceiteMidLib.php](../../../application/libraries/CalculadoraTermoAceiteMidLib.php) | 1.461 |
| Farmer | [CalculadoraTermoAceiteFarmerLib.php](../../../application/libraries/CalculadoraTermoAceiteFarmerLib.php) | 1.029 |

Valores reais de `origin` (BD local `solides-pipedrive.termo_aceite`, 2026-08-21):

| origin | termos | origem do valor |
|---|---|---|
| `NULL` | 15.543 | default — **fluxo Mid** |
| `farmer` | 1.882 | único que roteia para a lib Farmer |
| `plg_checkout` | 1.087 | — |
| `beneficios-nmrr` | 212 | forçado na lib Mid ([:777](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L777)) |
| `white_label` | 107 | — |
| `folha-nmrr` | 58 | produtos de folha, forçado na lib Mid ([:759-765](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L759-L765)) |
| `lovecrm` | 52 | — |
| `RHGestor-NMRR` | 40 | gravado como `rhgestor-nmrr` na lib ([:746](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L746)) — **atenção à caixa** |
| `partial` | 28 | — |

> **Armadilha recorrente (cards 157713 e 158930):** título de card com a palavra "farmer" **não** significa fluxo farmer. Antes de qualquer hipótese, confirmar `termo_aceite.origin`. Dois cards abertos como "erro de ganho farmer" eram Mid (`origin=NULL`). Sinal complementar nos logs: `acao = "Ganho Mid/Vsb error"` é Mid; a mensagem "não encontrar uma base no banco de dados do CRM com o documento informado" é exclusiva do farmer ([GanhoFarmerLib.php:197](../../../application/libraries/Ganho/src/GanhoFarmerLib.php#L197)).

> **`origin` é lido de lugares diferentes conforme a operação (card 165575) — não confundir os dois caminhos:**
>
> | Operação | De onde vem `origin` | Âncora |
> |---|---|---|
> | **Visualização** (`GET termo-aceite/{token}`) | Do **registro no banco** | [Termo_aceite.php:47](../../../application/controllers/Termo_aceite.php#L47), [:49-51](../../../application/controllers/Termo_aceite.php#L49-L51) → [:52](../../../application/controllers/Termo_aceite.php#L52) |
> | **Aceite/criação** (`POST`) | Do **`$post['origin']`**, sem checar o banco | [Termo_aceite.php:37](../../../application/controllers/Termo_aceite.php#L37) → `getTipoTermoAceite` ([termo_aceite_helper.php:271-278](../../../application/helpers/termo_aceite_helper.php#L271-L278)) |
>
> O segundo caminho é achado de segurança (**S2**, § 11.2 da análise 165575) — quem controla o POST escolhe a lib, não o registro. Não citar `getTipoTermoAceite`/`:271-278` como prova do caminho de **visualização**: já derrubou uma rodada de validação por isso.

### Seleção de view dentro do Mid — cascata na visualização

`CalculadoraTermoAceiteMidLib::processaVisualizacaoTermo` ([:103-125](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L103-L125)), depois de `trataDadosTermoAceite`:

1. `lingua == 'EN'` → `termo_view_en` ([:104](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L104))
2. senão, `switch($produto)`: lista literal de 8 valores de Cartão/Cesta de Benefícios → `termo_view_beneficios` ([:107-116](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L107-L116)); `'RH Gestor'` → `termo_view_rhgestor` ([:118-120](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L118-L120)); **`default`** ([:121-123](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L121-L123)) → `termo_view` — é a view da maioria dos termos (`lingua=PT`, produto fora das duas listas).

`termo_view.php` troca o rótulo de `dls_email` para **"Email do contratante"** quando `dados_criacao_acesso['login_unificado']` é truthy ([termo_view.php:240](../../../application/views/termo_aceite/termo_view.php#L240)); sem isso o rótulo é "Email de quem vai utilizar o sistema".

## Rotas ([routes.php:86-103](../../../application/config/routes.php#L86-L103))

| Rota | Destino |
|---|---|
| `termo-aceite/criacao-termo` | `Termo_aceite::processaCriacaoTermo` ([:26](../../../application/controllers/Termo_aceite.php#L26)) |
| `termo-aceite/aceite-termo` | `Termo_aceite::processaAceiteTermo` ([:34](../../../application/controllers/Termo_aceite.php#L34)) |
| `termo-aceite/{token}` | `Termo_aceite::processaVisualizacaoTermo` ([:41](../../../application/controllers/Termo_aceite.php#L41)) — catch-all, **declarar rotas novas ANTES desta** |
| `termo-aceite/webhook-pagamento-cartao` | **Em código, ainda não mergeado na `master`** (feature 161899, worktree `~/worktrees/cit/161899_etapa_5_8_11_12_pos_venda`): `PagamentoCartaoTermo::webhook` (`application/controllers/PagamentoCartaoTermo.php:27` na worktree) |
| `ganho-cartao` | **Em código, ainda não mergeado na `master`** (mesma worktree): `GanhoCartao::processaGanhoCartao_post` (`application/controllers/GanhoCartao.php:36` na worktree) → `Cartao/GanhoCartaoLib::processa` (`application/libraries/Cartao/GanhoCartaoLib.php:53` na worktree). Rota **própria** do ganho por cartão, fora do namespace `termo-aceite/` e por isso **não** alcançada pelo catch-all; autenticada por `Authorization: Bearer` (`GANHO_CARTAO_WEBHOOK_SECRET`) e fail-closed por cobrança aprovada no CIT. O ganho por **boleto** segue em `ganhoMidNetsuite` ([routes.php:198](../../../application/config/routes.php#L198)), sem alteração |
| `termo-aceite/orcamento`, `.../orcamento/proposta`, `termo-aceite-farmer/orcamento/proposta` | calculadora e proposta |
| `termo_aceite/historico-termo-aceite[-ajax]` | histórico e filtros |

Endpoints de validação usados pelo front: `validaDocumentoGestao` ([:812](../../../application/controllers/Termo_aceite.php#L812)) e `validaEmailGestao` ([:827](../../../application/controllers/Termo_aceite.php#L827)).

> Rota pública do termo precisa estar na whitelist do [SessionHook.php](../../../application/hooks/SessionHook.php) — fora dela a resposta é 303 para `/`.

## Fluxo do aceite (Mid) — ordem exata

`CalculadoraTermoAceiteMidLib::processaAceiteTermo` ([:47](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L47)):

1. `verificaTermoAceiteEstaAceito` — barra reaceite pelo mesmo link
2. `trataLoginUnificado`
3. `aceitarTermoDeAceite` — **grava o aceite no banco**
4. `desviaParaPagamentoCartao` ([:1136](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L1136)) — se elegível, **retorna aqui**; o resto roda depois, pelo webhook
   - **Em código, ainda não mergeado** (branch `161899_etapa_0_kill_switch_guardas`, feature 161899/T2): o método passa a começar por um guard-clause que consulta `PagamentoCartaoTermoLib::ofertaLigada()` — kill switch por dado em `configuracao_toggle`. Desligado (padrão de nascença) ⇒ devolve `false` **antes** da elegibilidade e o aceite segue no fluxo do boleto, com log `desvioPagamentoCartaoDesligado` em `INFO`. A **retomada** (`retomaPagamentoCartaoPendente`) fica fora do kill switch de propósito.
   - **Em código, ainda não mergeado** (branch `161899_etapa_0_modulo_cartao_extracao`, feature 161899/T11): o cartão sai de dentro da lib do aceite. `desviaParaPagamentoCartao` e `retomaPagamentoCartaoPendente` **deixam de existir** aqui e viram `PagamentoCartaoTermoLib::assumeAceite($post, $emailDisparo)` e `::retomaPagamentoPendente($termoAceite, $emailDisparo)`; sobram duas bifurcações de 3 linhas. `executaAcoesPosPagamentoCartao`, `reservaEtapaCartao` e `liberaEtapaCartao` viram `application/libraries/Cartao/PosPagamentoCartaoLib::executaAcoesPosPagamento`, e a leitura do envelope da Pagar.me mais a decisão do segredo viram `application/libraries/Cartao/EventoPagarmeCartao` (classe estática pura). `processaAcoesHubspot`, `enviaEmailAceiteTermoDeAceite` e `buscaTermoAceite` passam a **públicos** com docblock `@api` — são o contrato que o módulo do cartão consome por chamada. Os logs migrados continuam com `request_from = 'Calculadora'` (constante `TERMO_CARTAO_LOG_ORIGEM_ACEITE`). **Uma diferença declarada de comportamento:** `payload` e `response` do `citlog` `acoesPosPagamentoCartaoHubspot` passam a `{token, produto_hubs}` / `''` — antes carregavam o resíduo de `manageDealCompany`. **A T2 e a T11 escrevem no mesmo método**: se a T2 entrar depois, o guard-clause do kill switch tem de ser reancorado como primeira instrução de `assumeAceite`.
5. `analisaVSBTermoAceite` — mensagem VSB
6. `processaAcoesHubspot` ([:177](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L177)) — propriedades do deal → nota → company, nesta ordem; sai cedo se `produto_hubs` vazio
7. `enviaEmailAceiteTermoDeAceite`

O `PATCH` das propriedades ([:194](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L194)) monta ~70 propriedades via `preenchePropriedadesDeal` ([hubspot_api_helper.php:1591](../../../application/helpers/hubspot_api_helper.php#L1591)) e vai pelo middleware interno autenticado por `x-api-key`. HTTP ≠ 200 vira exceção, **sem retry**.

## Ganho (posterior ao aceite)

HubSpot chama `POST hubspot_rest/ganhoMid` → `GanhoMidLib::executaGanhoMid` ([:49](../../../application/libraries/Netsuite/src/GanhoMidLib.php#L49)), que cria cliente, contatos, assinatura e integrações e marca o termo com `idclifor`, `id_assinatura`, `ganho_realizado`. Rota do webhook Netsuite: `ganhoMidNetsuite` ([routes.php:197](../../../application/config/routes.php#L197)). Farmer: `processa-ganho/farmer` ([routes.php:194](../../../application/config/routes.php#L194)).

Duas validações **bloqueiam** o ganho Mid — causa raiz frequente de "ganho não aconteceu":

| Barreira | Onde |
|---|---|
| E-mail já vinculado a base ativa no Gestão | [GanhoMidLib.php:481](../../../application/libraries/Netsuite/src/GanhoMidLib.php#L481) |
| Assinatura ativa existente para o CNPJ | [GanhoMidLib.php:715](../../../application/libraries/Netsuite/src/GanhoMidLib.php#L715) |

**Qual e-mail o ganho usa:** `getCampoEmailQueVaiUsarOSistema` ([:150](../../../application/libraries/Netsuite/src/GanhoMidLib.php#L150)) resolve `dados_criacao_acesso['email_corporativo_usuario'] ?: termo['email']`. Com login unificado, o determinante é o `email_corporativo_usuario` — não o `email` do termo (card 156719).

### Ganho Mid = aquisição, Farmer = expansão — não trocar método/canal entre os dois

Os dois fluxos escrevem a **mesma** propriedade de negócio `log_ganho_mid`, mas por métodos e canais
diferentes — citar o método errado entrega desenho errado com aparência de precedente válido:

| Fluxo | Sentido de negócio | Método (grava `log_ganho_mid`) | Canal |
|---|---|---|---|
| Mid | aquisição de cliente novo | `GanhoMidLib::insereLogGanhoMidDealHubspot()` (privado, [:497](../../../application/libraries/Netsuite/src/GanhoMidLib.php#L497)) | `hubspotlib->alterarDealHubSpotV3`, PATCH com wrapper `['properties' => [...]]` |
| Farmer | expansão de assinatura existente | `GanhoLib::atualizaLogGanhoDealHubspotFarmer()` ([GanhoLib.php:2177](../../../application/libraries/Ganho/src/GanhoLib.php#L2177)) | `hubspotmiddlewarelib->updateDealProperties`, sem wrapper |

`insereLogGanhoMidDealHubspot` **grava sem ler o valor anterior** — qualquer coisa escrita em
`log_ganho_mid` antes do ganho Mid rodar é **sobrescrita**. Para publicar estado que precisa
sobreviver ao ganho, pedir propriedade dedicada, não reusar `log_ganho_mid`.

### Cadeia da criação de base no Gestão (Mid): CIT → omie-adapter → gestao-adapter

O ganho Mid **não fala direto com o gestao-adapter** para criar acesso (só no Farmer, e ali é para
*editar* acesso existente). A cadeia é em três saltos: CIT (`GanhoMidLib::ganhoMid`,
[:89](../../../application/libraries/Netsuite/src/GanhoMidLib.php#L89)) → POST `CONTRACT_CREATE` no
repositório **omie-adapter** (`ContractCreate`, `src/app/Services/OmieActions/ContractCreate.php`) →
publica `CRIAR_ACESSO` na fila SQS `ti-corp-gestao-adapter` → repositório **gestao-adapter**
(`CriarAcesso`, `src/app/Services/GestaoActions/CriarAcesso.php`) cria a base.

Dois defeitos medidos (16/09/2026, `docs/analises/ganho-mid-base-nao-criada-gestao/analise-tecnica.md`):
- **Retry infinito.** A constante `EMPRESA_NAO_UNIFICADA_MAX_RETRY_ATTEMPTS` foi removida do
  omie-adapter (confirmado ausente em 25/09/2026 — zero ocorrências no repositório); sem teto e com
  delay de 900s, uma mensagem presa reprocessa ~96×/dia. Requeue manual (`sendMessage`+`deleteMessage`)
  zera o `ReceiveCount` e nunca alcança a DLQ.
- **Falha engolida.** `CriarAcesso` e `ContractCreate` capturam `\Exception` sem relançar — a
  mensagem some da fila sem criar a base, sem retry e sem rastro além do `log_ganho_mid` no deal.

Ao triar "base não criada no Gestão", separar os dois sintomas pela tabela
`etapas_fluxos_servicos` (`etapa_servico`='omie-adapter' do CIT vs 'gestao-adapter' do adapter) e
pelo texto de `log_ganho_mid` no deal — são repositórios diferentes, procurar só no CIT não acha
nada.

### Barreira 5.1 do Farmer e `DATA_DESVINCULO` — "base não encontrada" nem sempre é dado ruim

`GanhoFarmerLib::processaGanho` → `definindoAtributosDoGanho` chama
`retornaBaseCrm('cpf_cnpj', getDealDocumento())` → `Cliente_model::get_cliente_by` (`CCLIFOR`,
`IDEMP=1`, `CNPJ IN` com/sem máscara). Vazio → mensagem **exclusiva do Farmer**: "não encontrar uma
base no banco de dados do CRM com o documento informado" ([GanhoFarmerLib.php:173](../../../application/libraries/Ganho/src/GanhoFarmerLib.php#L173)).
O documento vem do **deal HubSpot**, não do termo.

Duas causas raiz já provadas para essa mensagem, nenhuma é "base não existe":

1. **Caractere invisível no CNPJ do deal** (card 158930) — NBSP/zero-width que o HubSpot não
   bloqueia e que `remove_chars`/`trim` ASCII não removem; `get_cliente_by` não normaliza o lado
   esquerdo do `IN`. Correção de dado: apagar e **redigitar manualmente** (sem colar) o CNPJ no
   deal. Melhoria de código sugerida: `preg_replace('/\D/','',$doc)` em `get_cliente_by`.
2. **`DATA_DESVINCULO` preenchida** (card 158930/158931) — desde o hotfix `e624aefdd`,
   `get_cliente_by` tem `->where('C.DATA_DESVINCULO IS NULL')` ([Cliente_model.php:151](../../../application/models/Cliente_model.php#L151)).
   Cliente ativo com assinatura ativa mas `DATA_DESVINCULO` preenchida barra igual. Esse campo
   **não é gravado pelo CIT** (é rotina do ERP "SG", sem trilha auditável) — correção é
   `UPDATE CCLIFOR SET DATA_DESVINCULO=NULL` com aval de negócio, não código.

Logs do ganho Farmer ficam em `cit.citlog` (não `citlog_automacoes`), `acao='automacao_hubspot_ganho_farmer'`;
`citlog_automacoes` guarda automações Omie/pagamento e sofre com índice ausente em produção —
ancorar por `created_at` (janela curta), não por `deal_id`/`idclifor`.

### `forma_de_pagamento` no HubSpot — definição diferente por portal

O CIT grava a propriedade `deal.forma_de_pagamento` via `retornaFormaPagamento()`
([hubspot_api_helper.php:1788](../../../application/helpers/hubspot_api_helper.php#L1788)) com os
literais **`Boleto`**, **`Cartão de crédito`** e **`Transferência`**. A definição da propriedade
**não é a mesma nos dois portais** (medido por API em 10/09/2026):

| Portal | Tipo da propriedade | Valores |
|---|---|---|
| Sandbox `23737834` | `string`/texto livre | 3 grafias vivas medidas: `BOLECODE`, `CARTÃO DE CRÉDITO`, `boleto` |
| `6009739` (o que `HUBSPOT_TOKEN` de `constants.php:96` alcança) | `enumeration`/`select` | só `boleto` e `cartao_credito` (slug) — **sem opção para Transferência** |

**Nenhum** dos três literais gravados pelo CIT casa com a enumeração do portal `6009739`. Antes de
desenhar uma condicional de workflow (ganho, retenção, o que for) contra essa propriedade, medir a
definição real **no portal em questão** — tratar como enumeração em todo lugar assume que o valor
gravado é válido quando não é; tratar como texto livre em todo lugar impede operador de igualdade
único (usar `is equal to any of`). O token do CIT (`6009739`) também não tem escopo `automation` nem
`crm.schemas` — ele grava propriedade existente, não cria workflow nem schema.

## Dados

`termo_aceite` — ~140 colunas. Chaves e campos de decisão:

| Campo | Uso |
|---|---|
| `token` varchar(45) | identidade do termo na URL e FK lógica das tabelas satélites |
| `origin` varchar(20) | roteia Mid/Farmer (tabela acima) |
| `status` varchar(45) | BD local: NULL 18.713 · `aceito` 231 · `pendente` 36 · `expirado` 29 — **a maioria é NULL**, não usar como filtro de aceite |
| `data_aceite` datetime | evidência real do aceite |
| `ganho_realizado` int | 0/1 — se o ganho concluiu |
| `hubspot_id` bigint · `pipedrive_id` int | deal |
| `idclifor`, `id_assinatura` bigint | preenchidos **pelo ganho** |
| `cnpj_cpf` varchar(45) | documento; chega **pré-preenchido** pelo vendedor |
| `produto` varchar(255) · `produto_hubs` varchar(100) | `produto_hubs` vazio pula as ações HubSpot |
| `data_pagamento` date | vira `nDiaFixo` no Omie → `DATAVENCIMENTO` em CMOVIMENTOS |
| `dados_criacao_acesso` json | contém `email_corporativo_usuario` (login unificado) |
| `multibase_*`, `dias_proposta`, `detalhamento_proposta` json | multibase, validade e composição da proposta |

**Cadeia do "Dia de pagamento" até o vencimento real** — `data_pagamento` (select de 3 opções:
10/15/20) alimenta, em paralelo: HubSpot `deal.data_de_vencimento`
([hubspot_api_helper.php:1610](../../../application/helpers/hubspot_api_helper.php#L1610)) e
`deal.dia_pagamento` ([:1651](../../../application/helpers/hubspot_api_helper.php#L1651));
`ASSINATURAS.DIA_VCTO_MENSALIDADE` ([GanhoMidLib.php:1106](../../../application/libraries/Netsuite/src/GanhoMidLib.php#L1106));
e o contrato Omie via `VencTextos.nDiaFixo`
([ContractsLib.php:191](../../../application/libraries/OmieGatewayLib/src/ContractsLib.php#L191)),
com `cPostergar="S"` ([OmieLib.php:142](../../../application/libraries/OmieLib.php#L142)) — se o
vencimento cair em dia não útil, o Omie empurra para o próximo dia útil; o `DATAVENCIMENTO` real em
`CMOVIMENTOS` (banco `aless608_sg_homol`, não `solides-pipedrive`) pode não ser o dia combinado.
Gravar `data_pagamento` como NULL faz o contrato nascer sem dia fixo e quebra o faturamento mensal.
`CFORMASPAGAMENTO.ID=3` é "Cartão de Crédito", `ID=2` é Boleto, nas três bases (`IDEMP` 1/2/3).

**Adesão cobrada = `round(max(adesao, valor_proposto_adesao) * (1 - percentual_desconto_adesao/100), 2)`**
— medido contra `CMOVIMENTOS.VALORLIQUIDO` em 143 parcelas (cliente com 1 termo e 1 parcela de
adesão): a fórmula acerta as 143, só `adesao` acerta 141, só `valor_proposto_adesao` acerta 138.
Dois enganos já custaram implementação errada (card 162988): `valor_proposto_adesao = 0,01` **não**
é marca de isenção (298 dos 306 termos com esse valor simplesmente não têm adesão; nos que têm, o
boleto cobra o valor cheio); e `adesao` **já é o total da implantação** (RH+DP+Folha juntos) —
somar por módulo duplica. Quem isenta é o `percentual_desconto_adesao` acima de ~99,99%. Ao medir,
restringir a cliente com 1 termo e 1 parcela — join por `IDCLIFOR` sozinho cruza termo de um cliente
com parcela de outro.

Satélites: `termo_desconto_mensalidades` (por mês, com `cod_os_omie`) e `termo_aceite_pagamento_cartao` (card 162988 — ids Pagar.me, bandeira, últimos 4, `dia_vencimento`, `status`, `payload_aceite`, `processado_em` para idempotência do webhook; **sem PAN/CVV**).

BD local: `solides-pipedrive` em `127.0.0.1:3309`, usuário `root`, **senha vazia** (o perfil de ambiente diz `homol_cit` — está desatualizado).

## Armadilhas conhecidas

**Frontend do termo** (cards 161122 e 156719):

| # | Armadilha | Onde |
|---|---|---|
| A1 | Validação de CNPJ presa ao evento `change`; o campo chega pré-preenchido e **nenhum `trigger('change')` roda no load** → a regra aprova sem consultar | [termo_view_completo.js:103,114](../../../js/termo_aceite/termo_view_completo.js#L103) |
| A2 | `jquery.mask` e `jquery-validate` vêm de **CDN externa**; se não carregam, `$('.cep').mask()` lança na 1ª linha do `ready` e **todo o `.validate()` nunca inicializa** — mas o `action` do form é registrado fora do `ready`, então o POST vai igual | [termo_view.php:559-560](../../../application/views/termo_aceite/termo_view.php#L559-L560) |
| A3 | `validaEmailGestao` hoje responde `application/json`; um `JSON.parse` sobre objeto lança `SyntaxError` e, com `async:false`, **derruba a validação antes do `preventDefault`** — o form submete sem validação alguma | [termo_view.js:478](../../../js/termo_aceite/termo_view.js#L478) |
| A4 | Regra de e-mail consulta a API **antes** de `this.optional(element)` → uma chamada síncrona por tecla | [termo_view.js:18-21](../../../js/termo_aceite/termo_view.js#L18-L21) |
| A5 | `isValidCnpjCpf` só calcula DV com 11 ou 14 dígitos; máscara presa a `keypress` (colar não formata); 13 dígitos consultados como CPF | [termo_view_completo.js:73-144](../../../js/termo_aceite/termo_view_completo.js#L73-L144) |
| A6 | `only_alphanumeric` remove maiúsculas (`[^a-z0-9]`) — **rejeita CNPJ alfanumérico** | [js/utils.js:176](../../../js/utils.js#L176) |
| A7 | View EN não tem `required` nem classe no documento e não carrega `js/utils.js` → termos EN sem validação de documento | [termo_view_en.php:135](../../../application/views/termo_aceite/termo_view_en.php#L135) |
| A8 | `validacoesMultibase` inerte no controller (card 161122 §8.1.1) | [Termo_aceite.php:660](../../../application/controllers/Termo_aceite.php#L660) |
| A9 | **E-mail com caractere invisível na borda trava o aceite sem dizer por quê (card 165575).** `validateEmail` usa regex **ancorada** `^...$`; o jquery-validate 1.19.5 entrega o valor via `elementValue()`, que só faz `.replace(/\r/g,'')` — **sem `trim()`**. Qualquer espaço, NBSP (`C2A0`), TAB, BOM (`EFBBBF`), ZWSP (`E2808B`) ou LRM (`E2808E`) na borda reprova, com a mesma mensagem genérica de um e-mail malformado | [termo_view_completo.js:147-154](../../../js/termo_aceite/termo_view_completo.js#L147-L154) (`addMethod` em [:18-21](../../../js/termo_aceite/termo_view_completo.js#L18-L21)); em `master` a função é `:142-149` — deslocamento de +10 linhas vindo do handler de `submit` do card 162988 ([:62-68](../../../js/termo_aceite/termo_view_completo.js#L62-L68)), ainda não commitado |

**Fluxo do aceite** (card 163244):

| # | Fragilidade | Consequência |
|---|---|---|
| E1 | `finally` redireciona para a página do termo **mesmo com exceção** | falha silenciosa; aparece dias depois no funil |
| E2 | Aceite gravado **antes** das ações HubSpot + bloqueio de reaceite | estado inconsistente sem autoatendimento |
| E3 | Sem retry no `PATCH`, enquanto outras rotinas usam 3 tentativas ([Hubspot_rest.php:467](../../../application/controllers/Hubspot_rest.php#L467)) | instabilidade momentânea perde o ganho |
| E4 | Mensagem diz "na criação do termo" mesmo ocorrendo no aceite ([:211](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L211)) | dificulta triagem |

Também: `atualizaDealStageParaFechadoGanho` é código morto e retorna `false` até em sucesso, por `return` dentro do `finally` ([Termo_aceite.php:736-738](../../../application/controllers/Termo_aceite.php#L736-L738)).

### Armadilha central: `trim()` não remove ZWSP nem LRM (card 165575)

`String.prototype.trim()` do JS **e** `trim()` do PHP removem espaço, TAB, LF, CR, NBSP e BOM — mas **não** removem `U+200B` (ZWSP) nem `U+200E` (LRM): são caracteres de formatação Unicode, não *whitespace*. Qualquer correção que troque a regra por um `trim()` simples continua reprovando esse caso.

- **Prova no dado:** base local, id `7318`, `resp_financeiro_email` = `[‎janaina.silva@expertise.net.br]` com `HEX` começando em `E2808E` (LRM) — visualmente perfeito, reprova a regra.
- **Consequência de projeto (card 165575, produção, 24/08/2026):** no token do incidente (`id 110254`), `email` e `resp_financeiro_email` vieram **NULL** no banco — não havia pré-preenchimento sujo; o caractere invisível foi produzido no **navegador da cliente**. Logo **não existe `UPDATE` que destrave um cliente assim** — a correção é obrigatoriamente no **front** (normalizar antes de validar, indo além de `trim()`), com o backend como rede de segurança, não como conserto de registro.
- Se a correção normalizar **na gravação**, só é seguro dentro de uma **lista de campos permitidos** — normalizar tudo sem essa lista sana o sintoma e ao mesmo tempo abençoa o *mass assignment* já existente no aceite (ver nota de segurança abaixo).

### Nota de segurança encontrada no caminho (card 165575) — não é a causa raiz, vira card próprio

- **Mass assignment no aceite (Alta) + `origin` decidido pelo POST em vez do registro (Alta)** — tratados como **um único card** a abrir. `marcaTermoComoAceito` faz `update('termo_aceite', $attributes)` sem whitelist ([Termo_aceite_model.php:434-443](../../../application/models/Termo_aceite_model.php#L434-L443)), alimentado pelo POST inteiro, sem sessão e sem CSRF. O achado de `origin` **encosta no card 162988** (pagamento via cartão, em código nesta mesma branch): enviar `origin=farmer` num termo Mid pula `desviaParaPagamentoCartao` e o guard `data_aceite IS NULL` — avisar o dono do 162988 antes do merge.
- **CSRF ausente, CodeIgniter 3.0.6 e exposição LGPD (POST com CPF/CNPJ/e-mail em log)** na rota pública do termo — ver `dominio-superficie-publica` (seção de config globais).

## Onde investigar

- **Log do aceite:** `citlog` com `acao='processaAceiteTermo'`, `setor='comercial'`, `request_from='Calculadora'`, `disparado_por` = e-mail do vendedor. **Não grava `deal_id`** — correlacionar por `payload`/`disparado_por` ([gravaLog :151](../../../application/libraries/CalculadoraTermoAceiteMidLib.php#L151)).
- **Log do ganho:** `citlog` / `citlog_automacoes`; `acao="Ganho Mid/Vsb error"` indica fluxo Mid.
- **Aceite efetivo:** `data_aceite IS NOT NULL` (não confie em `status`).
- **Expiração:** [ExpiracaoDeTermosLib.php](../../../application/libraries/ExpiracaoDeTermosLib.php) + `obterTermoDeAceiteNaoAssinadoNoPrazo` ([Termo_aceite_model.php:694](../../../application/models/Termo_aceite_model.php#L694)); validade no HubSpot via `calcularValidadeHubspot` ([helper:547](../../../application/helpers/termo_aceite_helper.php#L547)).

## Pagamento via cartão no aceite (card 162988 / feature 161899)

> **Reancorado em 25/09/2026 (destilação pós-medição do Brain, 16 órfãs do `kb.sh verificar`)** —
> as 16 âncoras órfãs eram código da feature 161899 que **não existe na `master`/working tree
> atual** (ela vive só em branch/worktree, ainda não mergeada). Reponteadas para o código real na
> worktree **principal** `~/worktrees/cit/161899_etapa_5_8_11_12_pos_venda` (branch de mesmo nome),
> que já está mais evoluída do que a nota anterior deste mapa descrevia: a extração do módulo
> (T11 — `PagamentoCartaoTermoLib`) e a rota própria do ganho (T12 — `GanhoCartao`) **já estão
> integradas nessa worktree**, não mais "em código, ainda não mergeado" como duas branches
> separadas. **Toda linha desta seção pode mudar até o merge para `master`** — antes de citar
> `arquivo:linha` daqui num card, confirme que ainda bate na worktree vigente. Detalhe consolidado
> do fluxo completo (tokenização, JWT, webhook, lambda, cobrança avulsa, régua de recusa) mora em
> `dominio-pagamento-cartao` — este bloco aqui cobre só o que acontece **dentro do aceite**.

Elegibilidade em cascata no helper `termo_aceite_helper.php` (linhas na worktree `161899_etapa_5_8_11_12_pos_venda`):

| Função | Linha | O que faz |
|---|---|---|
| `produtoCrmElegivelPagamentoCartao($produtoCrm)` | :749 | checa `CLASSIFICACAO` do registro de `BPRODUTOS` contra `TERMO_CARTAO_CLASSIFICACAO_PLANO` |
| `composicaoElegivelPagamentoCartao($termoAceite)` | :813 | monta a decisão completa (`elegivel`, `fonte`, `produto`, `produto_hubs`, `codproduto`...) a partir de `produto`/`produto_hubs` do termo |
| `elegibilidadeProdutoPagamentoCartao($termoAceite)` | :904 | wrapper — chama `composicaoElegivelPagamentoCartao((array) $termoAceite)` |
| `produtoDoTermoElegivelPagamentoCartao($termoAceite)` | :915 | devolve só o booleano `elegivel` da função acima — é a chamada usada na **visualização** |
| `elegibilidadeTermoPagamentoCartao($termoAceite)` | :928 | decisão completa no nível do termo (`elegivel`, `forma_cartao`, `fonte`, `categoria`, `classificacao`...) |
| `termoElegivelPagamentoCartao($termoAceite)` | :990 | wrapper booleano de `elegibilidadeTermoPagamentoCartao` |

Configuração em `application/config/constants/pagamento_cartao_termo.php` (mesma worktree).

**O aceite não faz mais o pagamento sozinho — delega para `PagamentoCartaoTermoLib`.**
`CalculadoraTermoAceiteMidLib::processaAceiteTermo`, na worktree `161899_etapa_5_8_11_12_pos_venda`:

1. Antes de gravar o aceite: `PagamentoCartaoTermoLib::retomaPagamentoPendente($termoAceite, $this->email)` (`CalculadoraTermoAceiteMidLib.php:57`, método real em `application/libraries/PagamentoCartaoTermoLib.php:252`) — retoma cobrança pendente e, se aplicável, **retorna aqui**.
2. Depois de `aceitarTermoDeAceite`: `PagamentoCartaoTermoLib::assumeAceite($post, $this->email)` (`CalculadoraTermoAceiteMidLib.php:71`, método real em `PagamentoCartaoTermoLib.php:178`) — se o termo é elegível a cartão, assume o aceite e **retorna aqui**; o resto (ações HubSpot, e-mail) roda depois, pelo webhook.
3. Só quando não é cartão: `normalizaFormaPagamentoParaIntegracao($post)` (`CalculadoraTermoAceiteMidLib.php:76`) segue o fluxo normal (boleto).

O webhook do retorno é `PagamentoCartaoTermo::webhook` (`application/controllers/PagamentoCartaoTermo.php:27`, na worktree) →
`WebhookPagamentoCartaoTermoLib::processa` (`application/libraries/WebhookPagamentoCartaoTermoLib.php:38`), que reidrata `payload_aceite` e, na aprovação, chama
`PosPagamentoCartaoLib::executaAcoesPosPagamento($termoAceite, $post, $registroCartaoId)` (`WebhookPagamentoCartaoTermoLib.php:202` → `application/libraries/Cartao/PosPagamentoCartaoLib.php:38`) — sai da lib do aceite por completo, evitando que a reentrega do webhook pela lambda repita o negócio no HubSpot e o e-mail ao cliente. Idempotência por `processado_em` + unique `(termo_aceite_token, pagarme_order_id)`. **Não há recorrência na Pagar.me** — cobrança avulsa; a recorrência segue por CMOVIMENTOS/DATAVENCIMENTO (ver `dominio-pagamento-cartao`).

**Rota própria do ganho por cartão**, fora do namespace `termo-aceite/`: `GanhoCartao::processaGanhoCartao_post` (`application/controllers/GanhoCartao.php:36`) → `Cartao/GanhoCartaoLib::processa` (`application/libraries/Cartao/GanhoCartaoLib.php:53`), autenticada por `Authorization: Bearer` contra `GANHO_CARTAO_WEBHOOK_SECRET` (`application/config/constants/pagamento_cartao_termo.php:90`). O ganho por **boleto** segue em `ganhoMidNetsuite` (`routes.php:197`), sem alteração — ver `dominio-superficie-publica` para a whitelist do `SessionHook`.

## Acervo — onde já foi estudado

| Subtema | Cards | Documento |
|---|---|---|
| Validação de CNPJ no termo | 161122 | [docs/analises/validacao-cnpj-termo-aceite/](../../../docs/analises/validacao-cnpj-termo-aceite/) |
| Validação de e-mail + CNPJ | 156719 | [docs/analises/validacao-email-cnpj-termo-aceite/](../../../docs/analises/validacao-email-cnpj-termo-aceite/) |
| Propriedades HubSpot pós-aceite | 163244 | [docs/analises/falha-propriedades-hubspot-termo-aceite/](../../../docs/analises/falha-propriedades-hubspot-termo-aceite/) |
| Downgrade de plano | 152452 | [docs/analises/termo-downgrade-plano/](../../../docs/analises/termo-downgrade-plano/) |
| Ganho Mid confundido com farmer | 157713, 158930 | [docs/analises/erro-ganho-farmer/](../../../docs/analises/erro-ganho-farmer/) |
| Ganho barrado por inadimplência | 156306 | [docs/analises/ganho-farmer-inadimplencia/](../../../docs/analises/ganho-farmer-inadimplencia/) |
| Pagamento via cartão | 162988, 161899 | [docs/implementacoes/plano/impl-162988-pagamento-cartao-apos-aceite.md](../../../docs/implementacoes/plano/impl-162988-pagamento-cartao-apos-aceite.md) |
| Adição de novo produto | — | [docs/analises/addd-novo-produto/](../../../docs/analises/addd-novo-produto/) |
| E-mail sempre inválido — falta de normalização | 165575 | [docs/analises/falha-preenchimento-termo-aceite/](../../../docs/analises/falha-preenchimento-termo-aceite/) |

Busca no acervo: `.claude/scripts/kb.sh buscar <termo>`.

## Manutenção

Ao encerrar card deste domínio (Pós-S6a / Pós-I15), atualizar esta skill: nova armadilha na tabela, nova linha no acervo, correção do que o card provou diferente. Registrar a data da conferência no topo.
