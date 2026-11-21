# Alterações para ambiente local — CIT

Mudanças **locais** (Docker, patches PHP, env) para rodar o CIT. Gerenciadas fora do commit versionado — não subir artefatos locais ao repositório.

**Como operar:** [ambiente-local-cit.md](ambiente-local-cit.md). **Este arquivo** documenta *o que muda* vs deploy de produção/homol.

**Data de referência:** junho/2026.

---

## Resumo executivo

| Área | Problema sem as alterações | Solução local |
|------|---------------------------|---------------|
| Container | Sem stack padronizada | `docker-compose.yml` + `docker/` (PHP + Apache, porta 8083) |
| Código no container | Volume aponta para repo direto | Volume bind mount em `docker-compose.yml` (sem rsync) |
| MySQL | App no Docker não alcança `127.0.0.1` do host | Serviço `db` no próprio compose; host `db` dentro do container |
| BD config | Variáveis de produção/homol no código | `docker/database.php` copiado pelo entrypoint em `development` |
| Captcha / auth | Captcha ativo em produção impede login local | Desligado em `development` via constants |
| URL/roteamento | `base_url` fixo para produção | Dinâmico via `HTTP_HOST` em `development` |
| Tokens externos | `MIDDLEWARE_HUBSPOT_*` e outros não versionados | Arquivo `.env` local (gitignored) |

---

## Onde ficam os arquivos

```
/var/www/html/cit/
├── docker-compose.yml          # Gitignored — compose local (app + db)
├── .env                        # Gitignored — variáveis locais (copiar de .env.example)
├── docker/
│   ├── Dockerfile              # PHP + Apache + entrypoint
│   ├── entrypoint.sh           # Copia database.php de desenvolvimento
│   ├── database.php            # Config de BD para development (host=db, porta=3309)
│   ├── apache/                 # VirtualHost Apache
│   └── php.ini                 # Configuração PHP local
└── .env.example                # Modelo de variáveis (versionado)
```

**O `docker-compose.yml` e o `.env` não entram no commit.** Confirmar `git status` antes de PR.

---

## Patches PHP locais — `.cursor/scripts/local.sh`

Além dos artefatos Docker acima, há **patches de código PHP** que só valem localmente. Eles moram
**fora do repositório**, em `~/patches-locais-cit/` (variável `PATCHES_LOCAIS_CIT` sobrescreve),
justamente para não poderem ser commitados por acidente. Origem: dois commits *"Ajuste local"*
(`a3a8704b9`, `d75b323c1`) extraídos em 31/07/2026 — o `README.md` da pasta descreve cada trecho.

| Comando | O que faz |
|---|---|
| `.cursor/scripts/local.sh status` | diz se o patch está aplicado e quais arquivos ele toca |
| `.cursor/scripts/local.sh apply` | aplica o patch (sem commit) |
| `.cursor/scripts/local.sh restore-repo` | reverte **só** o patch — **obrigatório antes de commit/PR** |

O que o patch muda: `index.php` (dotenv opcional — sem ele o app **não sobe** local),
`application/hooks/SessionHook.php` (profiler off + 5 métodos de `termo_aceite` fora do bypass de
sessão), `LogLib.php`, `Cron_model.php`, `Cliente_model.php`, `Hubspot_model.php`,
`utils_helper.php` e uma view de cron.

**Por que `restore-repo` nunca usa `git restore`:** `SessionHook.php` costuma ter patch local *e*
trabalho de card ao mesmo tempo. `git restore` apagaria os dois. O script reverte pelo próprio
patch (`git apply -R`) e **para com erro** se os dois estiverem misturados de forma que não dê
para separar — nesse caso a separação é manual.

---

## Configuração de BD (`docker/database.php`)

Copiado pelo `entrypoint.sh` para `application/config/development/database.php` na subida do container.

| Constante | Valor local | Motivo |
|-----------|-------------|--------|
| `DEFAULT_HOST` | `db` | Hostname do serviço MySQL no compose |
| `DEFAULT_DATABASE` | `solides-pipedrive` | Schema central / agente |
| `SOLIDES_MASTER_DEVEL_DATABASE` | `aless608_sg_homol` | BD do CRM |
| `SOLIDES_PARTNERS_DATABASE` | `aless608_sales_homol` | BD do Partners |
| `PROFILE_GESTAO_DB_DATABASE` | `solides_profiler_production` | BD gestão |
| `SOLIDES_EAD_DATABASE` | `solidesb_solidesead` | BD EAD |
| `SOLIDES_RH_DB_DATABASE` | `aless608_rh_arfernandez` | BD RH |

Dentro do container, o host de BD é **`db`** (serviço no compose). No host (CLI), usar **`127.0.0.1:3309`**.

---

## Docker — detalhes

| Componente | Alteração |
|------------|-----------|
| `entrypoint.sh` | Copia `docker/database.php` → `application/config/development/database.php` antes de subir Apache |
| Volume app | Bind mount direto do repo — edições refletem imediatamente (sem rsync) |
| Volume cache/logs | Bind mounts em `application/cache` e `application/logs` para permissão `www-data` |
| Volume propostas | `assets/propostas` montado para persistir arquivos gerados |
| Rede Traefik | Labels Traefik roteiam `Host(localhost)` / `Host(127.0.0.1)` → container na porta 8083 → URL final `http://localhost:8082/` |
| Rede interna | `solides-cit-internal` (bridge) entre `app` e `db` |
| MySQL container | `solides-mysql-homol` (imagem `cit-db:local`) — compartilhado por todos os projetos Solides |

---

## Alterações de código específicas de `development`

| Área | O que muda em `development` | Impacto em produção |
|------|------------------------------|---------------------|
| Captcha | `CAPTCHA_ATIVO = 0` — login sem reCAPTCHA | Não aplica (constante condicional) |
| `base_url` | Dinâmico via `HTTP_HOST` | Produção usa host oficial fixo |
| Conexão BD | Host `db` (Docker); porta `3309` | Produção usa RDS / host de prod |
| Tokens externos | Lidos do `.env` local | Produção usa variáveis de servidor |
| `ENVIRONMENT` | `development` | Produção/homol: `production` / `homologation` |

**Deploy:** garantir `ENVIRONMENT !== 'development'` e hosts oficiais (`homol.cit.solides.adm.br`) para não aplicar bypass de captcha nem resolução de gateway Docker.

---

## MySQL central — atenção especial

O container `solides-mysql-homol` é definido **neste compose** (cit). Todos os projetos Solides (Partners, CRM etc.) dependem dele em `127.0.0.1:3309`. Portanto:

- **Subir o cit = subir o MySQL compartilhado**.
- Não derrubar o cit enquanto outros projetos estiverem em uso.
- `docker compose down` remove o `solides-mysql-homol` — confirmar que nenhum outro projeto depende naquele momento.

---

## Checklist para nova máquina

1. [ ] Criar imagem MySQL: `docker build -t cit-db:local .` (ou restaurar dump)
2. [ ] Criar volume: `docker volume create cit_mysql_data`
3. [ ] Criar rede Traefik: `docker network create traefik`
4. [ ] Copiar env: `cp /var/www/html/cit/.env.example /var/www/html/cit/.env`
5. [ ] Preencher tokens em `.env` (copiar de homol ou backup anterior)
6. [ ] Subir: `cd /var/www/html/cit && docker compose up -d`
7. [ ] Validar: `curl -s http://localhost:8082/` → resposta HTTP 200
8. [ ] Validar BD: `mysql -h127.0.0.1 -P3309 -uroot homol_cit -e "SELECT 1"`
9. [ ] Antes de commit: `git status` — confirmar que `docker-compose.yml` e `.env` estão gitignored

---

## O que não alterar em produção

Alterações **específicas de development** (comportamento diferente em prod/homol):

- Captcha desligado (`CAPTCHA_ATIVO = 0`) — condicionado a `ENVIRONMENT === 'development'`
- `docker/database.php` — nunca deployar; é copiado pelo entrypoint apenas em `development`
- `docker-compose.yml` e `.env` — gitignored; nunca commitar
- Host `db` no `database.php` — válido apenas dentro do container Docker local

---

## Env nova no `.env` não chega ao container — o atalho do `cit-<env>.env`

**Sintoma:** você acrescenta uma chave ao `.env`, o `getenv()` continua devolvendo `false` dentro do
container e a constante nasce vazia.

**Causa medida (27/08/2026):** o `docker-compose.yml` injeta o `.env` por `env_file`, e `env_file`
só é aplicado **na criação do container**. Chave acrescentada depois não entra — e recriar o
container **não é opção**, porque o código do cit não é bind mount: um `--force-recreate` devolve o
código da imagem e apaga tudo que foi levado por `docker cp`.

**Saída sem recriar container:** o `index.php:343-346` carrega, por Dotenv, o arquivo
`../cit-<ENVIRONMENT>.env` — isto é, `/var/www/html/cit-<env>.env`, um nível **acima** da raiz do
projeto dentro do container. Medido: `vlucas/phpdotenv` v4.3.0 com `createImmutable(...)->safeLoad()`
**popula o `getenv()`**, não só `$_ENV`, então as constantes que usam `getenv()` funcionam.

São **dois** arquivos, porque o `ENVIRONMENT` muda com o canal (`index.php:60-79`):

| Arquivo | Quando é lido |
|---|---|
| `/var/www/html/cit-development.env` | acesso **web** local (qualquer host que não seja o de prod/homol) |
| `/var/www/html/cit-production.env` | **CLI e cron** — em linha de comando `$env = 'production'` (`#CRONJOBS`) |

```bash
grep -E '^(CHAVE_A|CHAVE_B)=' .env > /tmp/novas.env
docker cp /tmp/novas.env solides-cit:/var/www/html/cit-development.env
docker cp /tmp/novas.env solides-cit:/var/www/html/cit-production.env
# conferir (sem imprimir segredo, só a chave que interessa):
docker exec solides-cit php -r 'require "vendor/autoload.php";
  Dotenv\Dotenv::createImmutable("/var/www/html","cit-production.env")->safeLoad();
  var_dump(getenv("CHAVE_A"));'
```

**Não commitar nada disso:** os arquivos vivem só dentro do container, e o patch do `index.php` que
torna o Dotenv opcional (`is_readable`) é patch local — `.cursor/scripts/local.sh restore-repo`
antes de qualquer commit.

**Estado em 27/08/2026 (card 166398):** os dois arquivos existem no container com as 5 chaves do
card — `EMAIL_ALERTA_REPROCESSAMENTO_CANCELAMENTO` e as quatro `OMIE_OS_PROJETO_*`. Sem elas, a
guarda de `CancelamentoDeClienteNetsuiteLib.php:1069-1085` aborta o cancelamento de OS por
configuração incompleta, e nenhum teste de cancelamento de OS sai do lugar.

---

*Atualizar este arquivo quando novas alterações forem necessárias para o ambiente local do cit.*

### `TOGGLE_FLUXO_CANCELAMENTO` faltava no ambiente local (27/08/2026)

**Sintoma:** `http://127.0.0.1:8083/formulario-de-cancelamento` devolvia **404**, e os cenários locais
do card 161125 caíam em `expectHttp200`.

**Causa medida:** `application/config/constants.php:330` define a constante a partir de `getenv`, e
`application/controllers/Formulario_cancelamento.php:14` faz `show_404()` quando ela é falsa. A chave
**não estava** no `.env` local nem no ambiente do contêiner — `docker exec solides-cit printenv | grep TOGGLE`
devolvia só `TOGGLE_NOVA_CALCULADORA_FARMER`. Está no `.env.example:297`, vazia.

**Correção:** `TOGGLE_FLUXO_CANCELAMENTO=true` no `.env` (para quando o contêiner for recriado) **e**
nos dois `cit-<env>.env` de dentro do contêiner, pelo atalho da seção anterior. Depois disso a rota
responde **307** (redireciona para a verificação de identidade) em vez de 404 — o fluxo está de pé.

Sem essa chave, **todo** cenário local ou E2E que abra o formulário de cancelamento falha, em qualquer
card — não é regressão de quem está mexendo no fluxo.

### `session.save_path` vazio derrubava HTTP 500 (08/09/2026)

**Sintoma:** toda requisição HTTP ao container solides-cit retornava **500 Internal Server Error** antes do roteamento, bloqueando todos os cenários de teste local da feature 161899. `curl -sI http://localhost:8080/` confirmava: HTTP 500.

**Causa medida:** `php -i` no container mostrava `session.save_path => no value => no value`. Diretório `/var/lib/php/sessions` não existia (confirmado: `ls -ld` retornava "cannot access"). PHP não conseguia gravar a sessão (`$_SESSION`) e falava com 500 genérico.

**Correção:** 
1. Adicionado `session.save_path = /var/lib/php/sessions` ao `docker/php.ini` (linha nova após xdebug)
2. Adicionado `RUN mkdir -p /var/lib/php/sessions` + `chown www-data:www-data` + `chmod ug+rwX` ao `docker/Dockerfile` (após mpdf setup)
3. Container reconstruído: `docker compose up -d --build`

**Prova de que resolveu:** 
- `php -i | grep session.save_path` agora mostra: `session.save_path => /var/lib/php/sessions => /var/lib/php/sessions`
- `ls -ld /var/lib/php/sessions` mostra: `drwxrwxr-x 2 www-data www-data`
- `curl -sI http://localhost:8080/` retorna **HTTP/1.1 200 OK** (era 500)

**Durabilidade:** ambas as alterações (php.ini e Dockerfile) estão versionadas e sobrevivem a `docker compose up -d --build`. Sem patches locais em ~/patches-locais-cit/.
