# Ambiente local — CIT

Referência para desenvolvimento local e testes **E2E (I7)**.  
Repositório: `/var/www/html/cit`.

**Documentos relacionados:**

- [Alterações de código para ambiente local](alteracoes-ambiente-local-cit.md)
- [Consultas BD (produção)](../sustentacao/consultas-bd.md)

---

## Gate L0 — antes da bifurcação (B0) e do fluxo (S1/I1)

**Obrigatório** antes de qualquer card. Agente sobe o ambiente, valida e **informa a URL no chat**.

| Passo | Comando / critério |
|-------|-------------------|
| 1. Subir | `cd /var/www/html/cit && docker compose up -d` |
| 2. MySQL | `mysql -h127.0.0.1 -P3309 -uroot homol_cit -e "SELECT 1"` |
| 3. HTTP | `curl -sI http://localhost:8082/ \| head -5` |
| **URL no chat** | **http://localhost:8082/** |

Somente após L0 ok → **B0 (bifurcação)**: perguntar *“SUSTENTAÇÃO ou IMPLEMENTAÇÃO?”* e aguardar a resposta explícita antes de iniciar **S1** ou **I1**.

---

## Dois ambientes — não confundir

| Ambiente | Uso | URL | Banco |
|----------|-----|-----|-------|
| **Local (I7 / I10)** | Dev + Playwright `e2e` e matriz `local` | `http://localhost:8082/` | `homol_cit` @ `127.0.0.1:3309` |
| **Homol remoto (I13)** | Validação pós-deploy | `https://homol.cit.solides.adm.br/` | BD **ao vivo** do servidor de homol |

- **I7:** `cd testes && npm run test:e2e` — project `e2e`.
- **I10:** `cd testes && npm run test:local` — matriz local na **URL local** (L01–LN).
- **I13:** `cd testes && npm run test:homol` — somente após **I12** (OK deploy homol).

Guias: [testes-local.md](../implementacao/testes-local.md), [testes-homol.md](../implementacao/testes-homol.md).

---

## MySQL central compartilhado

O container MySQL (`solides-mysql-homol`, imagem `cit-db:local`) é definido no `docker-compose.yml` do próprio cit como serviço `db` (porta `3309:3306`). **Todos os projetos Solides dependem dele** — subir o cit é necessário para que o MySQL esteja disponível para os demais projetos.

| Item | Valor |
|------|-------|
| Container | `solides-mysql-homol` |
| Imagem | `cit-db:local` |
| Host (host) | `127.0.0.1:3309` |
| Host (dentro do container) | `db` |
| Banco cit | `homol_cit` |
| Banco schema/agente | `solides-pipedrive` |
| Usuário | `root` |
| Senha | *(vazia)* |

---

## Docker — visão geral

| Item | Valor |
|------|-------|
| Stack | PHP + Apache (CodeIgniter) |
| Orquestração | `docker-compose.yml` na raiz do repo |
| Contexto de build | `.` (raiz, Dockerfile em `docker/`) |
| Container app | `solides-cit` |
| Porta HTTP | **8083** → 80 no container (Traefik roteia `localhost:8082`) |
| Código no container | `/var/www/html/cit` (bind mount via volumes) |
| MySQL | Serviço `db` no próprio compose — `127.0.0.1:3309` no host |
| `ENVIRONMENT` | `development` (controlado via `.env`) |

Rede Traefik: roteamento via `http://localhost:8082/` (labels Traefik no compose).

---

## Variáveis de ambiente (`.env`)

O compose carrega `.env` da raiz do repo via `env_file`.

| Variável | Uso local típico |
|----------|-----------------|
| `DEFAULT_HOST` | `localhost` → substituído por `db` dentro do container (`docker/database.php`) |
| `DEFAULT_DATABASE` | `solides-pipedrive` (banco schema) |
| `SOLIDES_PARTNERS_DATABASE` | `aless608_sales_homol` |
| `SOLIDES_MASTER_DEVEL_DATABASE` | `aless608_sg_homol` |
| `MIDDLEWARE_HUBSPOT_*` | Copiar de homol ou backup local |

**Host do MySQL:**

| Onde roda o PHP | host de BD |
|-----------------|------------|
| Docker (`solides-cit`, porta 8083) | `db` (hostname do serviço no compose) |
| CLI no host | `127.0.0.1` |

Modelo: `.env.example` na raiz do repo.

---

## BD para validação de schema (agente)

Usado para montar queries **antes** de pedir execução em produção.

| Parâmetro | Valor |
|-----------|-------|
| Host | `127.0.0.1` |
| Porta | `3309` |
| Banco (schema) | `solides-pipedrive` |

```bash
mysql -h 127.0.0.1 -P 3309 -u root -e "SELECT 1 AS ok, VERSION() AS versao;"
```

### Banco CIT na máquina local

| Parâmetro | Valor típico |
|-----------|--------------|
| Banco | `homol_cit` |
| Usuário | `root` |
| Senha | *(vazia no ambiente documentado)* |

```bash
mysql -h127.0.0.1 -P3309 -uroot homol_cit
```

---

## Pré-requisitos

- Docker e Docker Compose
- Imagem `cit-db:local` disponível localmente (MySQL compartilhado)
- Rede `traefik` externa criada (`docker network create traefik`)
- Volume `cit_mysql_data` criado (`docker volume create cit_mysql_data`)
- `.env` na raiz do repo (copiar de `.env.example`)

---

## Configuração inicial

```bash
cp /var/www/html/cit/.env.example /var/www/html/cit/.env
# Preencher credenciais e tokens conforme homol
```

Rede Docker (criada automaticamente se já existir):

```bash
docker network create traefik 2>/dev/null || true
docker volume create cit_mysql_data 2>/dev/null || true
```

---

## Subir o ambiente

```bash
cd /var/www/html/cit
docker compose up -d
```

Verificar:

```bash
docker ps --filter name=solides-cit
curl -sI http://localhost:8082/ | head -5
```

### Sincronizar código após edições

O código é montado via volume direto — não há rsync. Edições em `/var/www/html/cit` refletem imediatamente no container.

Rebuild apenas se alterar `docker/Dockerfile`, `docker/apache/` ou `docker/php.ini`:

```bash
docker compose up -d --build
```

---

## URLs locais

| Função | URL |
|--------|-----|
| Raiz | http://localhost:8082/ |
| Login | http://localhost:8082/login (conforme rotas do projeto) |

---

## Comandos úteis

```bash
docker logs -f solides-cit
docker compose down
docker compose up -d --build --force-recreate
ss -tlnp | grep 8082
ss -tlnp | grep 3309
```

---

## Testes Playwright (`testes/`)

| Pasta | Etapa | Alvo |
|-------|-------|------|
| `testes/E2E/specs/` | **I7** | `http://127.0.0.1:8083/` (via Traefik → `localhost:8082`) |
| `testes/local/specs/` | **I10** | `http://localhost:8082/` (L01–LN) |
| `testes/homol/specs/` | **I13** | `https://homol.cit.solides.adm.br/` |

```bash
cd testes && npm run test:e2e
cd testes && npm run test:local   # I10
cd testes && npm run test:homol   # I13 — após I12
```

Credenciais: `testes/.credentials.local`. Guias: [testes-e2e.md](../implementacao/testes-e2e.md), [testes-local.md](../implementacao/testes-local.md), [testes-homol.md](../implementacao/testes-homol.md).

### Ciclo I10–I15 (implementação)

1. **I10** — `npm run test:local` — 100% pass na URL local
2. **I11** — `evidencias.html` — bloco local L01–LN + subagente `validador-tecnico` (Opus) valida
3. **I12** — OK explícito do usuário para deploy homol
4. **I13** — `npm run test:homol` — 100% pass na homol remota
5. **I14** — `evidenciashomol.html` — E2E + homol U01–UN
6. **I15** — subagente `validador-tecnico` (Opus) valida `evidenciashomol.html` → encerramento

Antes de **commit/PR**, garantir que não há patches locais ativos (`git status` limpo nos arquivos de código).

---

## Problemas comuns

| Sintoma | Ação |
|---------|------|
| Porta 8082/8083 em uso | `ss -tlnp \| grep 8082` / parar container conflitante |
| Erro MySQL no app | Confirmar `3309`, `.env`, banco `homol_cit`, imagem `cit-db:local` |
| Tokens/API falham | Preencher `MIDDLEWARE_HUBSPOT_*` no `.env` |
| Código não reflete no browser | Edições são ao vivo (volume direto); verificar `docker ps` |
| `base_url` errado em dev | Verificar labels Traefik e variáveis em `.env` |
| MySQL não sobe | Verificar volume `cit_mysql_data` e imagem `cit-db:local` |

---

## Arquivos Docker do projeto

| Arquivo | Função |
|---------|--------|
| `docker-compose.yml` | Serviços `app` (solides-cit) e `db` (solides-mysql-homol) |
| `docker/Dockerfile` | Imagem PHP + Apache + entrypoint |
| `docker/entrypoint.sh` | Copia `docker/database.php` → `application/config/development/database.php` |
| `docker/database.php` | Configuração de BD para development (host `db`, porta 3309) |
| `docker/apache/` | VirtualHost Apache |
| `docker/php.ini` | Configuração PHP local |
| `.env` / `.env.example` | Variáveis de ambiente (tokens, BD) |

---

*Última atualização: junho/2026 — URL de acesso local `http://localhost:8082/` (Traefik), porta Docker `8083`, homol `https://homol.cit.solides.adm.br/`.*
