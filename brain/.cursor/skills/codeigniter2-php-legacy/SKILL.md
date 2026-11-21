---
name: codeigniter2-php-legacy
description: >-
  Implementa backend PHP em projetos Solides CodeIgniter 3 / PHP legado. Use ao
  editar controllers, models, helpers, libraries, routes ou lógica server-side
  em application/.
---

# CodeIgniter 3 + PHP legado — Solides

> Aplica-se aos projetos Solides em **CodeIgniter 3 / PHP legado**. Versão exata, PHP, caminhos e
> env variam por projeto → ver o perfil `arquitetura/ambiente-local-{projeto}.md`. No **cit**,
> confirmado `CI_VERSION` = `3.0.6` em [`system/core/CodeIgniter.php:58`](../../../system/core/CodeIgniter.php#L58)
> — projetos mais antigos da frota podem estar em CI2 genuíno; conferir a constante antes de aplicar
> o padrão de construtor abaixo.

## Documentação oficial (consultar quando necessário)

| Tema | URL |
|------|-----|
| CodeIgniter 3 User Guide | https://codeigniter.com/userguide3/ |
| Controllers | https://codeigniter.com/userguide3/general/controllers.html |
| Models | https://codeigniter.com/userguide3/general/models.html |
| Active Record (Query Builder) | https://codeigniter.com/userguide3/database/query_builder.html |

**Versão do projeto (cit):** CI **3.0.6** (não CI2, não CI4).

## Estrutura do projeto

```
application/
├── controllers/     # Auth, Clientes, Lovecrm*, Orcamento, Trial, ...
├── models/          # *_model.php — Active Record
├── views/
├── helpers/
├── libraries/
└── config/          # routes.php, database.php, constants.php
system/              # Core CI3 — evitar alterar
```

## Padrões deste codebase

- Construtor **moderno**: `public function __construct()` + `parent::__construct()` — confirmado
  em **40/40** controllers de `application/controllers/*.php`, ex.:
  [`Beneficios.php:11-13`](../../../application/controllers/Beneficios.php#L11),
  [`Cliente.php:4-6`](../../../application/controllers/Cliente.php#L4),
  [`Comercial.php:6-8`](../../../application/controllers/Comercial.php#L6).
  **Não** é `parent::Controller()` (esse era o padrão CI2 antigo — não existe no cit).
- Models: `$this->db->get()`, `$this->db->where()`, `$this->db->insert()`
- URLs: `site_url('controller/method')`
- `ENVIRONMENT`: `development` (local) · `production` (deploy). **Homol é ambiente externo** — acesso por URL + usuário/senha, **sem subir ambiente local** (ver [ambientes-e-testes](../ambientes-e-testes/SKILL.md))
- Env: arquivo `{projeto}-{ENVIRONMENT}.env` — caminho exato no perfil `arquitetura/ambiente-local-{projeto}.md`

## Regras de implementação

1. **Minimal diff** — seguir estilo do arquivo
2. **Não renomear** variáveis salvo pedido explícito
3. **Sem** namespaces, PSR-4 ou features PHP 8+
4. Validar SQL via Active Record

## Ambiente local

- Stack, porta, URL e comando de subida variam por projeto — ver skill [ambientes-e-testes](../ambientes-e-testes/SKILL.md) e o perfil `arquitetura/ambiente-local-{projeto}.md`

## Referência

- o perfil `arquitetura/ambiente-local-{projeto}.md`
- o perfil `arquitetura/alteracoes-ambiente-local-{projeto}.md`
