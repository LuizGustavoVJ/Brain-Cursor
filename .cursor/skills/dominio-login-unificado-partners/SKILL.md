---
name: dominio-login-unificado-partners
description: >-
  Mapa de domínio do login unificado (Keycloak/API externa) e do fallback que
  consulta o banco partners e depois o CRM White Label quando o unificado não
  devolve CNPJ — a causa raiz mais comum de "login OK mas CNPJ vazio" ou
  "dropdown vazio" no formulário de cancelamento. Cobre a semântica do schema
  partners (`empresas`/`usuarios`), o toggle de conexão
  `TOGGLE_LEGACY_CONNECTION_DATABASE` e o gate de perfil que é pulado quando a
  origem dos dados não é `auth_api`. Use em qualquer card que toque
  autenticação de e-mail no cancelamento, dropdown de CNPJ, acesso White
  Label, bloqueio/desbloqueio de acesso partners, ou que investigue por que um
  e-mail "existe" mas não aparece nenhuma empresa/CNPJ vinculado. Aplica-se ao
  repositório cit.
---

# Domínio — Login unificado + partners (fallback WL/CRM)

Conferido contra o código em 2026-09-25, working tree da branch
`167697_fluxo_reativacao` (card 167697 já mergeou o fix do curto-circuito,
commit `c1f9af092`). Cada afirmação tem âncora `arquivo:linha`. Ao divergir do
código, **o código manda**.

## Duas fontes de "isso é um usuário WL válido"

| Fonte | O que é | Onde vive |
|---|---|---|
| **Login unificado** | API externa (Keycloak) com token OAuth próprio, é a fonte "oficial" hoje | `UnifiedAuthenticationService.php`, HTTP via cURL |
| **partners** | banco MySQL próprio do produto partners, schema local `aless608_sales_homol` (:3309) | conexão `solides_partners` / `DataBaseConnect::getConnection('partners')` |
| **CRM (GUSUARIO/GEMPRESA)** | carteira real de clientes, é o fallback final | `Cliente_model::validarEmailGusuarioCrm` |

O código de cancelamento (`Otp_cancelamento.php`) **tenta o unificado primeiro
e só cai no fallback partners→CRM quando o unificado não resolve CNPJ** — não
o contrário.

## O contrato de `UnifiedAuthenticationService::validarEmail()`

[UnifiedAuthenticationService.php:19](../../../application/services/UnifiedAuthenticationService.php#L19).
Sequência: obtém token ([:38](../../../application/services/UnifiedAuthenticationService.php#L38)) →
busca usuário por e-mail ([:45](../../../application/services/UnifiedAuthenticationService.php#L45),
`GET /api/admin/users/username/{email}`) → se `encontrado` e `enabled`, busca
relacionamentos (produtos + organizações,
[:75](../../../application/services/UnifiedAuthenticationService.php#L75)).

O retorno sempre tem o formato `['success','encontrado','permitido','origem','motivo_interno','http_code','dados']`
([:23-31](../../../application/services/UnifiedAuthenticationService.php#L23-L31)).
**`permitido=true` não implica `dados.cnpjs` não vazio** — um usuário pode
existir e estar ativo no Keycloak sem ter organização/CNPJ vinculado lá
([:75-84](../../../application/services/UnifiedAuthenticationService.php#L75-L84),
`buscarRelacionamentosUsuario` monta `cnpjs` só a partir do `alias` de cada
organização retornada por `/api/admin/users/{email}/products`). Essa lacuna —
não uma falha de rede — é a origem do "login OK, CNPJ vazio".

## O curto-circuito e o fallback (a peça central)

`Otp_cancelamento::validarEmailComFallback()`
([:151-175](../../../application/controllers/Otp_cancelamento.php#L151-L175)):

1. Chama o unificado.
2. **Só aceita a resposta do unificado direto** quando `permitido=true` **e**
   `dados.cnpjs` não está vazio
   ([:160-162](../../../application/controllers/Otp_cancelamento.php#L160-L162)).
   Este é o ponto que o card 167697 corrigiu — antes bastava `permitido=true`
   (sem checar CNPJ) para encerrar aqui, e o dropdown vinha vazio mesmo
   existindo cadastro em partners/CRM.
3. Senão, tenta o fallback quando `permitido=true` **ou** o motivo é um dos
   três abaixo ([:164-172](../../../application/controllers/Otp_cancelamento.php#L164-L172)):
   `nao_encontrado`, `auth_token_indisponivel`, `auth_consulta_indisponivel`.
4. `resolverFallbackWlCrm()` ([:177-227](../../../application/controllers/Otp_cancelamento.php#L177-L227))
   tenta **partners primeiro** (`Cliente_model::validarEmailWhiteLabelPartners`,
   origem `'partners'`), depois **CRM** (`Cliente_model::validarEmailGusuarioCrm`,
   origem `'crm_gusuario'`). Só retorna algo se achar CNPJ; se nenhuma das
   duas achar, devolve `null` e o chamador **preserva o retorno original do
   unificado** — ou seja, se o unificado disse `permitido=true` sem CNPJ,
   o e-mail continua autorizado (decisão de produto: "manter como está", não
   bloquear), só que o dropdown fica vazio de novo.

Consequência prática: **"CNPJ vazio" com login que passa não é sempre bug** —
pode ser o comportamento (3) quando nem partners nem CRM têm o e-mail
vinculado a nenhuma empresa White Label. Antes de abrir card, confirme se o
e-mail existe em `partners.usuarios` ou em `GUSUARIO` com `IDCLIFOR` de
empresa `tipo='white_label'`.

## Banco partners — schema e semântica (verificado 02/09/2026 contra dump homol)

Local: schema **`aless608_sales_homol`**, MySQL `127.0.0.1:3309` (dump, sem
senha). Conexão de código: `$db['solides_partners']`
([database.php:167-187](../../../application/config/database.php#L167-L187),
host/usuário/senha por env — não citados aqui). Homol ao vivo não é esse
banco — é execução controlada (ver skill de ambiente); o :3309 é dump
congelado, útil só para estrutura.

| Tabela | O que é | Não é |
|---|---|---|
| `empresas` | parceiros de **vários tipos** (`connect`, `partial`, `white_label`, `NULL`); coluna `tipo` é o que distingue WL dos demais; `idclifor` referencia `CCLIFOR.ID` no CRM; `status` 1=ativo/0=bloqueado | não é só White Label — filtrar sem `tipo='white_label'` libera parceiros de outro tipo |
| `usuarios` | **operadores do painel do parceiro** (login de quem administra a marca WL), `email`, `empresa_id` → `empresas.id`, `status`, `deleted_at` | não é a carteira de clientes finais — a carteira mora no CRM (`GUSUARIO` com `IDCLIFOR` preenchido) |

A query real de validação (`Cliente_model::validarEmailWhiteLabelPartners`,
[:510-544](../../../application/models/Cliente_model.php#L510-L544)) exige
**as quatro condições juntas**: `u.status=1`, `u.deleted_at IS NULL`,
`e.status=1`, `e.tipo='white_label'`, `JOIN e.id = u.empresa_id`. Tirar
qualquer uma libera parceiro errado (connect/partial) ou WL bloqueado.

## O outro lado do fallback: `validarEmailGusuarioCrm`

[Cliente_model.php:546-578](../../../application/models/Cliente_model.php#L546-L578).
Junta `GUSUARIO` → `GEMPRESA` → `CCLIFORTIPOEMPRESA` (filtro
`TIPO='white_label'`) → `CCLIFOR` (filtrado por `IDEMP_SOLIDES`). Também exige
`g.IDCLIFOR IS NULL` e `ge.IDCLIFOR IS NOT NULL` — é o operador da carteira
White Label logado sem CNPJ próprio atrelado à conta, herdando o CNPJ da
empresa. Ambíguo (mais de 1 empresa WL para o mesmo e-mail) retorna `false`
([:572-575](../../../application/models/Cliente_model.php#L572-L575)) —
outro motivo de "e-mail existe mas não aparece CNPJ".

## O toggle de conexão — dois caminhos de código para o mesmo banco

`TOGGLE_LEGACY_CONNECTION_DATABASE` é `false`
([constants.php:265](../../../application/config/constants.php#L265)), o que
faz todo método de `Cliente_model` que fala com partners usar
`DataBaseConnect::getConnection('partners')`
([DataBaseConnect.php:33-34](../../../application/core/DataBaseConnect.php#L33-L34))
em vez de `$this->load->database('solides_partners', true)`. Os dois caminhos
existem lado a lado em cada método (`verificaWhiteLabelAcessoPartners`,
`getStatusAcessoPartners`, `setBloqueioDesbloqueioAcessoPartners`,
`validarEmailWhiteLabelPartners`, `getIdempByIdclifor` — todos com o mesmo
padrão `TOGGLE_LEGACY_CONNECTION_DATABASE ? load->database(...) :
DataBaseConnect::getConnection('partners')`). Se um dia esse toggle virar
`true` em algum ambiente, o comportamento não muda de banco, só de forma de
conectar — mas vale conferir antes de descartar como causa de divergência
entre ambientes.

## Gate de perfil pulado por origem — não é furo, é decisão de negócio

`Formulario_cancelamento.php` só roda `avaliarBloqueioPerfil()`
(fail-closed: API de gestão fora do ar, CNPJ não achado ou plano bloqueante →
bloqueia) quando `otp_cancelamento_origem_dados === 'auth_api'`
([:78-87](../../../application/controllers/Formulario_cancelamento.php#L78-L87),
regra em [:351-395](../../../application/controllers/Formulario_cancelamento.php#L351-L395)).
Origem `'partners'` ou `'crm_gusuario'` **pula o gate inteiro** — confirmado
como intencional (não bug) no card 167697: o admin da marca White Label
(e-mail existe no unificado mas sem organização vinculada, resolve por
`crm_gusuario`) precisa conseguir cancelar a própria marca; fechar o gate
para essas origens bloquearia esse admin também. Cliente final da mesma WL
resolve por `auth_api` e continua barrado. **Não "fechar o furo" sem
reconfirmar esse caso de negócio** — é comportamento pedido, não brecha.

## Desenho WL puro — qual base recebe a escrita

`BaseWhiteLabelLib::aplicaEstadoBaseWhiteLabel()`
([:22-85](../../../application/libraries/BaseWhiteLabelLib.php#L22-L85))
decide o "branch" pela mesma pergunta do fallback de leitura —
`Cliente_model::verificaWhiteLabelAcessoPartners($idclifor)`
([:463-482](../../../application/models/Cliente_model.php#L463-L482), existe
linha em `empresas` para o `idclifor`?):
- **Existe em partners** → escreve `empresas.status`
  (`aplicaEstadoPartners`, [:87-124](../../../application/libraries/BaseWhiteLabelLib.php#L87-L124),
  com transação quando `!TOGGLE_LEGACY_CONNECTION_DATABASE`).
- **Não existe em partners** → cai para `GUSUARIO` no CRM
  (`Financeiro_model::setAtivoGusuarioWlPorIdemp`,
  [:54-65](../../../application/libraries/BaseWhiteLabelLib.php#L54-L65)),
  usando `getIdsEmpresaPorIdclifor` para achar os `IDEMP`.

Em ambos os casos, `GEMPRESA` também é atualizada
([:67](../../../application/libraries/BaseWhiteLabelLib.php#L67)) — o
partners nunca é a única escrita, é sempre CRM + (partners OU GUSUARIO).

`getIdempByIdclifor($idclifor, $tipoEmpresa)`
([Cliente_model.php:180-200](../../../application/models/Cliente_model.php#L180-L200))
exige o par `tipo` + `idclifor` — sem o `tipo`, o mesmo `idclifor` pode casar
com um parceiro `connect`/`partial` em vez do `white_label` certo.

## Cross-repo — o partners tem seus próprios models (não travado por `kb.sh`)

O repositório **partners** (`/var/www/html/partners`, também CodeIgniter 3)
tem `application/models/Empresa_model.php` e `application/models/Usuario_model.php`
gerenciando as mesmas tabelas `empresas`/`usuarios` do lado da aplicação
partners — confirmado apenas a **existência das classes**
(`class Empresa_model extends CI_Model`, `class Usuario_model extends CI_Model`,
ambas na linha 3 de cada arquivo), não o conteúdo dos métodos. **Isto é
código de outro repositório** — não deduza comportamento dele a partir do
cit; se o card exigir mexer ali, peça permissão explícita (regra de escopo
cross-repo do AGENTS.md) e leia o arquivo real antes de afirmar algo. Âncora
não travada pelo `kb.sh` (só cobre `.cursor/skills/dominio-*` dentro do
próprio repo cit).

## Checklist ao investigar "login passou mas CNPJ/dropdown vazio"

1. Qual foi a **origem** salva na sessão (`otp_cancelamento_origem_dados` /
   `otp_cancelamento_origem_validacao`)? `auth_api` com `cnpjs=[]` é o caso
   central deste mapa.
2. O e-mail existe em `partners.usuarios` com `empresas.tipo='white_label'`
   e `status=1` nos dois lados? Se não, confira `GUSUARIO`/`GEMPRESA` com
   `TIPO='white_label'` no CRM.
3. Se nenhum dos dois achar CNPJ, **isso não é bug automaticamente** — pode
   ser e-mail sem organização vinculada em nenhum lugar (fluxo (3) acima);
   confirme com o time de negócio antes de tratar como defeito.
4. Confira se o gate de perfil (`avaliarBloqueioPerfil`) deveria ou não ter
   rodado para aquela origem — rodar para `partners`/`crm_gusuario` bloquearia
   admin de marca WL, que é o caso que o card 167697 preservou de propósito.

## Agentes

`especialista-integracao` (contrato da API do unificado, timeouts, token) ·
`especialista-sql` (queries de `Cliente_model` contra partners/CRM) ·
`especialista-php-legado` (mexer em `Otp_cancelamento`/`BaseWhiteLabelLib`) ·
`revisor-regra-negocio` (antes de "corrigir" o pulo do gate de perfil).
