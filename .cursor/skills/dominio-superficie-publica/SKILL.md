---
name: dominio-superficie-publica
description: >-
  Mapa de domínio da superfície pública do CIT — como o SessionHook decide o que
  responde sem sessão, as duas whitelists (classe e método), a exceção do
  termo_aceite e o que isso implica ao criar rota, controller ou método novo. Use
  em qualquer card que crie rota, endpoint, webhook ou método público, que
  investigue redirect para "/" sem log, ou que avalie exposição. Aplica-se ao
  repositório cit.
---

# Domínio — Superfície pública do CIT

Conferido contra o código em 2026-08-24 (card 165575). As âncoras de `PagamentoCartaoTermo` e
`GanhoCartao` foram reconferidas em 25/09/2026 e **não existem na `master`/working tree padrão** —
só na worktree da feature 161899 (`~/worktrees/cit/161899_etapa_5_8_11_12_pos_venda`), citada
explicitamente onde aparecem. Cada afirmação tem âncora `arquivo:linha`. Ao divergir do código,
**o código manda**.

## Quem decide

Dois hooks `post_controller_constructor`, na ordem: `check_login` e depois `check_permission`
([hooks.php:11](../../../application/config/hooks.php#L11) e [:18](../../../application/hooks/SessionHook.php#L18)). Ambos no mesmo arquivo:
`application/hooks/SessionHook.php`.

O hook roda **depois** do construtor do controller — logo, código no `__construct()` executa mesmo
em requisição que será redirecionada. Efeito colateral em construtor acontece sem sessão.

## A regra exata de `check_login`

[SessionHook.php:102](../../../application/hooks/SessionHook.php#L102). A condição que **exige** login é, respeitando a
precedência de `&&` sobre `||`:

```
( classe NÃO está em $array_classes  E  método NÃO está em $array_methods )
OU
( classe == 'termo_aceite'  E  método fora de
  [processaVisualizacaoTermo, processaAceiteTermo, proposta_view, get_info_company_api, validaDocumentoGestao] )
```

Consequências que importam:

| Consequência | Detalhe |
|---|---|
| **Classe na whitelist → tudo dela é público** | qualquer método novo naquele controller nasce sem sessão. [SessionHook.php:8](../../../application/hooks/SessionHook.php#L8) — 40 entradas, 38 únicas (`Hubspot_rest` e `HistoricoDeAssinaturas` duplicadas, sem efeito). **Em código, ainda não mergeado na `master`** (feature 161899, worktree `~/worktrees/cit/161899_etapa_5_8_11_12_pos_venda` — reancorado em 25/09/2026, linha pode mudar até o merge): `GanhoCartao` entra na whitelist (`SessionHook.php:59` na worktree) — com restrição de método no `check_login` (`SessionHook.php:131-132` na worktree, `in_array($this->router->fetch_method(), ['processaGanhoCartao'])`), com comentário de guarda avisando que a whitelist desliga `check_permission` para a classe inteira, no mesmo padrão de `termo_aceite`. `PagamentoCartaoTermo` **também não existe na `master`** — está na mesma worktree, whitelist em `SessionHook.php:55`, restrição em `SessionHook.php:125` (`in_array(..., ['webhook'])`) |
| **Método na whitelist → público em qualquer classe** | a comparação é só pelo **nome do método**, sem par classe+método. Criar `my_profile` ou `ganhoMid` em outro controller torna esse método público. [SessionHook.php:52](../../../application/hooks/SessionHook.php#L52) — 31 métodos |
| **`termo_aceite` é a exceção invertida** | está na whitelist de classes, mas só 5 métodos são públicos; qualquer outro método dessa classe **exige** sessão |
| **Comparação sensível à caixa** | `in_array` sem flag; `fetch_class()` devolve a classe como o roteador a resolveu, sem normalizar ([Router.php:434](../../../system/core/Router.php#L434) faz apenas `str_replace(['/','.'],'')`). A entrada da whitelist tem que bater exatamente com o destino escrito em `routes.php` — `ContaReceberTangerino` e `termo_aceite` convivem por isso |
| **Falha é redirect, não erro** | sem sessão: `sess_destroy()` + `redirect('/')`. No navegador vira 303 para a home; em `curl` vira 302/303 **sem nada no log da aplicação** — é a causa mais comum de "meu endpoint novo não responde" |
| **`index` é tratado à parte** | classe `index` com sessão ativa e método diferente de `logout` é redirecionada para `/dashboard` |

`$classes_bypass = ["auth"]` é atribuído no construtor ([:90](../../../application/hooks/SessionHook.php#L90)) e **não** é usado por `check_login`.

## Ao criar rota ou endpoint novo — a checagem de 30 segundos

1. Qual **classe** o `routes.php` aponta? É essa string que o `in_array` compara.
2. O endpoint deve ser público? → a classe precisa estar em `$array_classes` **com a mesma caixa**.
3. Deve exigir sessão? → **não** ponha a classe na whitelist e **não** reaproveite nome de método
   que já está em `$array_methods`.
4. Vai adicionar classe à whitelist? Então **todo** método dela fica público — inclusive os que
   você não escreveu. Se só um método deve abrir, o padrão do repositório é a exceção do
   `termo_aceite` ([:108](../../../application/hooks/SessionHook.php#L108)).
5. Rota pública que recebe token na URL precisa de resposta a enumeração — leve para
   `especialista-seguranca` antes de subir.

## Config globais que ampliam qualquer exposição em rota pública (card 165575)

Quatro flags de `application/config/config.php`, todas conferidas nesta data, valem para **toda** rota pública, não só o termo de aceite — quem investiga XSS, CSRF ou vazamento de sessão numa rota da whitelist não precisa reabrir esse debate a cada card:

| Flag | Valor | Âncora | Efeito |
|---|---|---|---|
| `global_xss_filtering` | `FALSE` | [config.php:444](../../../application/config/config.php#L444) | POST chega intacto ao controller — nenhum filtro automático de tag/atributo |
| `csrf_protection` | `FALSE` | [config.php:460](../../../application/config/config.php#L460) | qualquer rota pública aceita POST forjado de outro domínio |
| `cookie_httponly` | `FALSE` | [config.php:416](../../../application/config/config.php#L416) | JS pode ler `ci_session` — pré-condição para um XSS armazenado virar sequestro de sessão |
| `cookie_secure` | `FALSE` | [config.php:415](../../../application/config/config.php#L415) | cookie de sessão trafega mesmo sem HTTPS |

Some a isso `CI_VERSION = 3.0.6` ([CodeIgniter.php:58](../../../system/core/CodeIgniter.php#L58)), de 2016 — CVE específico não verificado, mas a base é antiga. Rota pública que ecoa valor do banco/POST sem `htmlspecialchars` no HTML **não é "fragilidade menor"** com essas quatro flags juntas: é XSS armazenado com caminho aberto para leitura de cookie de sessão. Achado original: análise do card 165575, § 9.4 e § 11.3.

## Pegadinha de ambiente local

Há patch local que mascara o comportamento do hook no ambiente local — inventário em
`.cursor/arquitetura/alteracoes-ambiente-local-cit.md` e os arquivos em
`/home/luizfinotello/patches-locais-cit/`. Endpoint que funciona no local e responde 303 em
homologação é, quase sempre, whitelist — não código do controller. Confira se o patch está
aplicado (`git status`, `git diff application/hooks/SessionHook.php`) **antes** de concluir
qualquer diagnóstico de acesso.

## Agentes

`especialista-seguranca` (exposição, abuso e autorização dentro do
método) · `especialista-php-legado` (mexer no hook) · `especialista-docker` (quando o 3xx vem antes
do PHP).
