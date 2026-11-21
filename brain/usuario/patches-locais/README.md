# Patches locais — repositório `cit`

Extraídos em 31/07/2026 dos 2 commits "Ajuste local" (`a3a8704b9`, `d75b323c1`, de 19/06/2026) que estavam
commitados por engano na branch `master` local, à frente de `origin/master`.

Nenhum desses ajustes existe em `origin/master` nem em `origin/staging` — são exclusivamente para rodar o
ambiente local.

## Conteúdo

| Arquivo | Uso |
|---|---|
| `ajustes-locais-cit.patch` | Diff único de tudo. Aplicar com `git apply` (não cria commit). |
| `0001-Ajuste-local.patch` / `0002-Ajuste-local.patch` | Formato `format-patch`, preservam autor/data. Aplicar com `git am` (cria commits). |

## O que os patches mudam

- **`index.php`** — carregamento do `cit-<ENV>.env` passa a ser opcional (`safeLoad` + `is_readable`).
  Necessário porque `/var/www/html/cit-development.env` não existe na máquina local; o código original faz
  `$dotenv->load()` obrigatório e lança exceção.
- **`application/hooks/SessionHook.php`** — desliga o profiler (`enable_profiler(false)`) e libera do bypass de
  sessão os métodos `validaEmailGestao`, `verificarProdutoRadarPodeSerAdquirido`,
  `buscaInformacaoContratualVigente`, `buscaInformacaoMultibase`, `buscaNomeNegocioHubspot` do controller
  `termo_aceite`.
- **`application/libraries/LogLib.php`**, **`application/models/Cron_model.php`**,
  **`application/models/Cliente_model.php`**, **`application/models/Hubspot_model.php`**,
  **`application/helpers/utils_helper.php`** — ajustes de log e cron para execução local.

## Como aplicar numa branch nova

```bash
cd /var/www/html/cit
git apply /home/luizfinotello/patches-locais-cit/ajustes-locais-cit.patch
```

Conferir se aplica limpo antes, sem alterar nada:

```bash
git apply --check /home/luizfinotello/patches-locais-cit/ajustes-locais-cit.patch
```

## Como remover antes de commit / PR

Os patches **nunca** devem ir para `origin`. Antes de commitar ou abrir MR:

```bash
git checkout -- index.php application/hooks/SessionHook.php \
  application/libraries/LogLib.php application/models/Cron_model.php \
  application/models/Cliente_model.php application/models/Hubspot_model.php \
  application/helpers/utils_helper.php
```

Ou reverter o patch inteiro:

```bash
git apply -R /home/luizfinotello/patches-locais-cit/ajustes-locais-cit.patch
```

## Histórico

Esses commits também estavam em `origin/158930_release_ajuste_recebimetno_deal_cnpj` — branch remota
**excluída pelo usuário em 31/07/2026**, antes de ser mergeada em `master` ou `staging`. Localmente, os
commits seguem preservados nas branches `158930_ajuste_recebimento_deal_cnpj` e
`158930_release_ajuste_recebimetno_deal_cnpj`.
