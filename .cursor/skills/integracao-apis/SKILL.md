---
name: integracao-apis
description: >-
  Integra APIs externas no projeto atual (CNPJá, e-mail, HubSpot, Omie,
  webservices curl). Use ao alterar libraries, helpers de envio, chamadas HTTP ou
  consumo de serviços terceiros em application/libraries/ e helpers/.
---

# Integrações de API — Solides

> O inventário de libraries/helpers abaixo (`application/libraries/`, `helpers/`) refere-se aos projetos **CodeIgniter 3 / PHP legado**. Nos adapters **Laravel** (omie-adapter, hubspot-adapter, debt-processing-service) a estrutura é outra — use os princípios (curl, e-mail, consumo de terceiros) e ver o código do projeto atual. Caminhos e tokens reais: perfil `arquitetura/ambiente-local-{projeto}.md`.

## Documentação oficial

| Integração | Documentação |
|------------|--------------|
| CNPJá (open.cnpja.com) | https://open.cnpja.com/docs |
| PHP cURL | https://www.php.net/manual/en/book.curl.php |
| CodeIgniter Email | https://codeigniter.com/userguide3/libraries/email.html |
| HubSpot CRM API | https://developers.hubspot.com/docs/api/overview |
| Omie API | https://developer.omie.com.br/ |
| JSON em PHP | https://www.php.net/manual/en/book.json.php |

**Nota:** não há módulo dedicado a **webhooks** no repo. Callbacks e integrações usam **curl/POST** em libraries ou controllers.

## Libraries e helpers existentes (exemplo em projetos CI3)

| Arquivo | Uso |
|---------|-----|
| `application/helpers/emails_helper.php` | `enviar_email($dataMail, $attach)` — monta `CI_Email`, prefixa `[HOMOL]` fora de produção |
| `application/libraries/HubspotMiddlewareLib.php` | HubSpot via middleware (`x-api-key`) |
| `application/libraries/Omie/src/OmieApiLib.php` | Omie ERP |
| `application/libraries/Financeiro_lib.php` | Baixa de movimento financeiro (ver "APIs financeiras" abaixo) |
| `application/models/Superlogica_updates_model.php` | Baixa de pagamento via Superlógica (ver "APIs financeiras" abaixo) |

**Podem não existir no repo atual** (validar antes de usar como exemplo): `Cnpja.php`, `envio_email_helper.php`,
`application/libraries/Services/AlterarCliente/` — validado por `find`/`grep` vazios em 2026-09-25.
Se outro repositório da frota tiver uma dessas libraries, a referência é daquele projeto, não do repo.

## Padrão CNPJá (função `get_info_cnpj()`)

Não é uma library `Cnpja.php` — é uma função de helper:

```php
$this->load->helper('hubspot_api');
$cnpja = get_info_cnpj($cnpj);
if (empty($cnpja['razao_social'])) { /* fallback */ }
```

- Definida em [`hubspot_api_helper.php:746-747`](../../../application/helpers/hubspot_api_helper.php#L746),
  usada em [`Cron.php:662`](../../../application/controllers/Cron.php#L662)
- `curl` GET para `URL_CNPJA . $cnpj` com header `Authorization: <TOKEN_CNPJA>` (constantes de `config/constants.php`)
- Mapeia o JSON de retorno (`company`, `address`, `phones`, `emails`) para um array plano
  (`razao_social`, `nome_fantasia`, `cnae`, `rua`, `cep`, `status`, ...)
- Existe também `get_info_cnpj_receitaws()` no mesmo helper (`hubspot_api_helper.php:837`) — fonte
  alternativa (ReceitaWS), não confirmado onde é usada

## Padrão e-mail (`emails_helper.php`)

```php
$this->load->helper('emails');
enviar_email([
    'assunto'  => '...',
    'email'    => $destinatario,
    'mensagem' => $html,
], $attach = false);
```

- Prefixo `[HOMOL]` no assunto e redirecionamento para `EMAIL_BOPE` quando `ENVIRONMENT !== 'production'`
  — [`emails_helper.php:6-7`](../../../application/helpers/emails_helper.php#L6)
- Remetente padrão `noreply@solides.com.br` / `Sólides Tecnologia`, com override por `from`/`from_name`
  — [`emails_helper.php:21-30`](../../../application/helpers/emails_helper.php#L21)
- Anexos: `$attach` aceita array ou item único, carregado antes do `send()`
  — [`emails_helper.php:49-56`](../../../application/helpers/emails_helper.php#L49)

## Padrão HTTP externo (HubSpot, webservice legado)

- `HubspotMiddlewareLib` (ex.: `updateCompanyProperties()`, `getDeal()`) monta URL + header
  `x-api-key` a partir de constantes `MIDDLEWARE_HUBSPOT_*` e delega o `curl` para a função de
  helper `returnCurlRequest($curl, $url, $header, $method, $bodyData)`, definida em
  [`utils_helper.php:253`](../../../application/helpers/utils_helper.php#L253) (há uma segunda
  definição em `app_helper.php:2322` — mesma assinatura, checar qual autoload está ativo antes de
  editar as duas)
- Controllers não chamam `curl_init()` diretamente — a chamada HTTP sempre passa por library ou
  helper; validar nomes de helpers no autoload do projeto

## APIs financeiras (baixa automática de movimento)

Não existe `modelmovimentos` nem `$this->SESS_IDEMP` no repo (grep vazio) — são dois pontos reais,
em arquivos diferentes, que marcam a baixa como automática antes de repassá-la ao sistema legado
(`repo-php-legado`, outro repositório):

- **Omie:** `Financeiro_lib::entrega_mrr_old()` seta `$movimento['apiomie'] = true` e faz `curl` POST
  do array inteiro (`http_build_query`) para o endpoint de movimentos no sistema legado —
  [`Financeiro_lib.php:1974`](../../../application/libraries/Financeiro_lib.php#L1974).
- **Superlógica:** `Superlogica_updates_model::registra_baixa_pagamento()` seta
  `$movimento['apisuperlogica'] = 1` na mesma lógica de baixa —
  [`Superlogica_updates_model.php:29`](../../../application/models/Superlogica_updates_model.php#L29).
- O que essas duas flags **desbloqueiam no sistema legado** (checagem de sessão/empresa em
  `repo-php-legado/application/libraries/Usuarios.php` e afins) é código de **outro repositório** —
  não deduzir o comportamento aqui sem ler o `repo-php-legado`.

Alterações aqui impactam Omie/Superlógica — validar escopo do card e, se o comportamento do lado
Integração cruzada: confirmar no outro repositório, não supor.

## Regras de implementação

1. **Nova integração:** preferir **library** CI3 em `application/libraries/`
2. Tokens/URLs em **config/constants** — não hardcodar no controller
3. Timeout + retry para APIs externas; logar falhas com `log_message`
4. Validar input **antes** da chamada HTTP
5. Não expandir escopo para refatorar integrações adjacentes

## Testes

- E2E isolado quando possível (validator, mock)
- Testes local (I10) e homol remoto (I13) para telas que disparam integração
- Credenciais de API: ambiente homol/produção — **nunca** commitar tokens
