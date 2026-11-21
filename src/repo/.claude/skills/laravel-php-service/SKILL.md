---
name: laravel-php-service
description: >-
  Implementa backend PHP nos serviços/adapters Laravel do Solides
  (omie-adapter, hubspot-adapter, debt-processing-service, gestao-adapter,
  payment-processing-service). Use ao editar controllers, services,
  repositories, models, jobs, commands, consumers, rotas ou configuração em
  app/ (raiz ou src/). Não se aplica aos projetos CodeIgniter 2 (partners,
  solides-crm, checkout, cit, ibc-assessment) nem aos pacotes Composer
  (gestao, omie).
---

# Laravel — serviços/adapters Solides

Skill de stack dos **serviços Laravel** do Solides. É a contrapartida da
[`codeigniter2-php-legacy`](../codeigniter2-php-legacy/SKILL.md) (que vale só nos projetos CI2).

## Onde esta skill se aplica

| Projeto | Laravel | PHP | Raiz do app | Entrada |
|---------|---------|-----|-------------|---------|
| `omie-adapter` | 11.x | 8.2 / 8.3 | **`src/`** (`src/app`, `src/routes`, `src/artisan`) | HTTP |
| `hubspot-adapter` | 11.x | 8.2 / 8.3 | **`src/`** | HTTP |
| `gestao-adapter` | 11.x (`v11.44.7`) | 8.2 / 8.3 | **`src/`** | HTTP + fila SQS |
| `debt-processing-service` | 10.x | 8.2 | **raiz** (`app/`, `routes/`, `artisan`) | HTTP |
| `payment-processing-service` | **9.x** (`v9.37.0`) | **8.1** | **raiz** | **só fila SQS — sem porta HTTP** |

> **Atenção ao diretório-base:** em `omie-adapter`, `hubspot-adapter` e `gestao-adapter` o projeto Laravel fica em `src/`; em `debt-processing-service` e `payment-processing-service` fica na raiz. Todos os caminhos abaixo são **relativos a essa base**.

> **Duas exceções que mordem:** `payment-processing-service` está em **Laravel 9 / PHP 8.1** — receita de Laravel 10/11 (ex.: `bootstrap/app.php` novo, `casts()` em vez de `$casts`) **não vale lá**. E ele **não publica porta HTTP**: é consumidor de fila, então "abrir a URL para ver se subiu" não existe — o sinal de vida é `docker compose ps` e o log do consumidor.

Perfil de ambiente de cada um: `.claude/arquitetura/ambiente-local-<projeto>.md` no repositório correspondente. **Nunca** usar porta, banco ou URL de um serviço em outro.

## Arquitetura (padrão comum dos serviços)

Camadas em `app/`:

| Camada | Pasta | Responsabilidade |
|--------|-------|------------------|
| **HTTP** | `app/Http/Controllers`, `app/Http/Requests`, `app/Http/Middleware` | Entrada da requisição, validação (FormRequest), resposta |
| **Service** | `app/Services` | **Regra de negócio** — orquestra repositories e integrações |
| **Repository** | `app/Repositories` | Acesso a dados (models/queries) isolado da regra |
| **Model** | `app/Models` | Eloquent — tabelas, relações, casts |
| **Console** | `app/Console/Commands` | Comandos `artisan` (rotinas, sincronizações) |
| **Enum** | `app/Enums` | Enums de domínio (status, tipos) |
| **Provider** | `app/Providers` | Bindings de container, boot de serviços |
| **Outros** | `app/Helpers`, `app/Mail`, `app/Mixins`, `app/Builders`, `app/Utils` | Conforme o serviço |

Rotas: `routes/api.php` (endpoints REST do adapter), `routes/console.php` (schedule/commands), `routes/web.php`. **`gestao-adapter` não tem `routes/api.php`** — as rotas HTTP estão em `web.php`.

Nos serviços que consomem fila (`payment-processing-service`, `gestao-adapter`) há uma camada a mais: `app/Consumers` (o loop que lê o SQS) acionada por um comando em `app/Console/Commands`. Mensagem que falha vai para a DLQ — no `payment-processing-service` o consumidor da DLQ está **comentado** no `docker-compose.yaml` e o limite de tentativas é `PAYMENT_PROCESSING_QUEUE_DLQ_ATTEMPTS_MAXIMUM`.

**Regra de ouro:** controller fino → **service** (regra) → **repository** (dados). Não colocar regra de negócio no controller nem query crua no service.

## Convenções ao implementar

- **Não inventar** rota, coluna, binding ou classe — confirmar no código (`grep`/`artisan route:list`) e no schema antes de alterar.
- **Não renomear** classes, métodos ou variáveis existentes sem pedido explícito.
- **Injeção por construtor** (type-hint) — seguir o padrão de DI já usado no serviço; não instanciar `new` onde há binding.
- **Validação** via `FormRequest` (`app/Http/Requests`) — não validar no corpo do controller quando já existe request.
- **Config/segredos** via `config/*.php` + `.env` (`env()` só dentro de `config/`, nunca espalhado). Não commitar `.env`.
- **PSR-12** e o padrão do arquivo vizinho (imports, tipos de retorno, nullable). Respeitar `pint`/`php-cs-fixer` se configurado.
- **Migrations** em `database/migrations` — nunca editar migration já aplicada; criar nova.

## Comandos úteis (a partir da base do projeto: `src/` ou raiz)

```bash
php artisan route:list          # descobrir endpoints reais
php artisan tinker              # inspecionar models/queries
php artisan migrate --pretend   # ver SQL de migration sem aplicar
composer test                   # ou: php artisan test / ./vendor/bin/phpunit
./vendor/bin/pint --test        # lint (se configurado)
```

## Testes

- **Unit/Feature Laravel:** `tests/` (PHPUnit) — rodar com `php artisan test`.
- **E2E/homol (Playwright):** quando o serviço tem pasta `testes/` própria (ex.: `hubspot-adapter/testes`), seguir [`ambientes-e-testes`](../ambientes-e-testes/SKILL.md) — E2E (I7), local (I10), homol (I13).

## Banco de dados

O BD alvo/porta consta no perfil `arquitetura/ambiente-local-{projeto}.md`. O MySQL central `127.0.0.1:3309` é compartilhado por vários sistemas Solides — confirmar no perfil qual BD cada serviço usa antes de montar query. Consultas de produção seguem o fluxo colaborativo de [`consultas-bd.md`](../../sustentacao/consultas-bd.md) (agente monta, usuário executa).

## Integração externa

Cada adapter integra um sistema: `omie-adapter` → Omie; `hubspot-adapter` → HubSpot; `debt-processing-service` → processamento de débitos. Chamadas HTTP externas seguem [`integracao-apis`](../integracao-apis/SKILL.md) (cliente HTTP, retries, tratamento de erro, timeouts).

## Deploy

Pipeline GitLab — ver [`gitlab-deploy-cicd`](../gitlab-deploy-cicd/SKILL.md). Deploy é responsabilidade humana, fora do fluxo do agente.
