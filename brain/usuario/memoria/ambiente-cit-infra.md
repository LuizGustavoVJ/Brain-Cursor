---
name: ambiente-cit-infra
description: "Infra local do cit — Docker Desktop (contexto desktop-linux), código não é bind mount, dois bancos no mesmo container 3309, config.php com skip-worktree invisível ao sync, env nova não chega ao container, CLI força ENVIRONMENT=production"
metadata:
  node_type: memory
  type: project
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:02:57.902Z
---

Consolida `ambiente-cit-porta-banco-divergentes`, `bancos-locais-cit-e-crm`,
`bd-homol-nao-e-o-mysql-3309`, `cit-cli-forca-environment-production`,
`cit-codigo-nao-e-bind-mount`, `config-php-skip-worktree-invisivel-ao-sync` e
`env-nova-nao-chega-ao-container-cit` (destilação de 25/09/2026). **O perfil
`.claude/arquitetura/ambiente-local-cit.md` diverge do que está medido aqui em vários pontos —
não corrigido por este agente (fora do escopo desta destilação); conferir os dois antes do L0.**

**Docker Desktop, contexto `desktop-linux`.** O `docker`/`docker compose` padrão do shell aponta
para o contexto `default` (outro daemon, sem os containers do cit). **Sempre** `docker -c
desktop-linux ...` para inspecionar/subir. Portas do host: Traefik `:8080` (não `:8082`), Apache
direto `:8083`, MySQL `:3309`.

**Código NÃO é bind mount** no `solides-cit` — só `assets/propostas`, `application/cache` e
`application/logs` são montados; o resto vem copiado na imagem (com os patches locais aplicados).
Editar no host não reflete: `docker cp <arquivo> solides-cit:/var/www/html/cit/<arquivo>` antes de
testar via HTTP. Armadilha: copiar sem o `/cit` final faz `php -l` rodar sobre a cópia antiga e
"passar" mesmo com erro real — usar sempre o caminho completo e `docker exec -w
/var/www/html/cit`.

**`application/config/config.php` tem skip-worktree** — invisível para `git diff`, então a
sincronização automática por diff nunca o copia; o container fica com `sess_save_path=NULL` e
`base_url` fixo, o que quebra a sessão semeada dos testes E2E (parecia "curl não mantém sessão",
era o `config.php` velho). Corrigir com `docker cp` manual sempre que o container for recriado —
`local.sh` ainda não cobre esse arquivo.

**Dois bancos no mesmo container `solides-mysql-homol` (:3309), sem senha (`-uroot`, `-proot`
dá acesso negado):** `solides-pipedrive` (CIT: `forms_cancelamento`, `termo_aceite`, `citlog`) e
`aless608_sg_homol` (CRM: `ASSINATURAS`, `CMOVIMENTOS`). Rodar migration nos dois quando a tabela
existir nos dois. **Este MySQL é 8.0.45 e é dump congelado (jun/2026)** — não representa
homologação nem produção; o servidor real recusa `ALGORITHM=INSTANT` (< 8.0.12) — nunca usar essa
cláusula em migration. **Dado ao vivo de homol não está aqui**: é o endpoint
`POST /homologacao/execucao-controlada` do próprio CIT (`select`/`update`, sem auth, sem
INSERT/DELETE/DDL — `Homologacao_rest.php`, rotas `routes.php:218-219`); migration em homologação
depende de quem tem acesso direto ao MySQL de homol (é a única parte de "local e homol o agente
executa" que o agente não fecha sozinho).

**Env nova não chega ao container já criado** — `env_file` só é lido na criação; recriar não é
opção (apaga tudo copiado via `docker cp`). Atalho: Dotenv do `index.php` lê
`/var/www/html/cit-<ENVIRONMENT>.env` (um nível acima da raiz, dentro do container) — só funciona
para chave que o container **ainda não tem**; `createImmutable` não sobrescreve chave já presente
no ambiente (só recriação resolve troca de valor). Três ambientes por host:
`cit.solides.adm.br`→`production`, `homol.cit.solides.adm.br`→`staging` (usa `cit-staging.env`),
qualquer outro→`development`. PHPUnit fica **fora** desse atalho (`Bootstrap.php` não passa pelo
`index.php`) — para teste, `putenv()` direto no `Bootstrap.php` antes do `init()`.

**CLI força `ENVIRONMENT=production`** (`index.php`, comentário `#CRONJOBS`) — cron rodado local
via linha de comando procura `cit-production.env` no diretório pai; sem ele, `mysqli::real_connect`
falha silenciosamente (retorna o valor padrão de cada guarda, não estoura erro). Testar cron pelo
navegador **não** exercita esse caminho (HTTP carrega `development`).
