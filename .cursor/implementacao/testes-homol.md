# Testes homol (URL) — implementação

Guia das etapas **I13** e **I14** do [fluxo-implementacao.md](fluxo-implementacao.md).

**Paridade com local:** as **mesmas regras** de [testes-local.md](testes-local.md) aplicam-se à homol — matriz idêntica (prefixos **U** vs **L**), critérios HTTP, preenchimento e escopo de telas.

> **Como executar (obrigatório):** `.cursor/scripts/resumo_testes.sh homol` — o stdout completo do Playwright **não entra no contexto**. Registrar apenas `N/N`, tempo e falhas. Ver [testes-resumido.md](testes-resumido.md).

---

## Ambiente alvo

**Homol remoto** — não usar URL local nesta etapa.

| Item | Valor |
|------|--------|
| URL base | URL homol remota do perfil `arquitetura/ambiente-local-{projeto}.md` |
| `PLAYWRIGHT_BASE_URL` | mesma URL homol do perfil |

A URL local é alvo de **I10** (`test:local`) — ver [testes-local.md](testes-local.md) e o perfil `arquitetura/ambiente-local-{projeto}.md`.

---

## Quando executar

**Somente após:**

- **I11** — bloco local L01–LN aprovado no `evidencias.html`
- **I12** — **OK explícito** do usuário confirmando deploy em homol
- Código **deployado** em homol (branch `staging`)

**Proibido** executar `test:homol` antes de I12.

---

## Objetivo

Validar a implementação **no homol real** nas **telas/views alteradas pela demanda**: print **com dados de teste preenchidos** (conforme plano) + evidência HTTP **200** por cenário.

Figuras no `evidenciashomol.html`: **U01–UN** (prefixo homol — **não** misturar com L01–LN do local).

---

## Regras obrigatórias da matriz (homol = local)

Ver [testes-local.md — Regras obrigatórias da matriz](testes-local.md#regras-obrigatórias-da-matriz-local--homol):

1. **Escopo** — somente telas alteradas pela demanda; sem login vazio; sem rotas genéricas não alteradas pelo card.
2. **Preenchimento** — dados de teste do plano/AC aplicados **antes** do screenshot (cadastro, filtro, edição, exibição).
3. **HTTP 200** — 401/403/404/500 = **falha**; **100% pass** obrigatório para I13.
4. **Evidência por tipo** — cadastro/edição: **2 prints + GET + POST**; filtro: 1 print + GET; asset: GET 200. **Sem alertas de erro** nos prints.

---

## Ações que alteram dados (POST/UPDATE) — testar a ação de fato

Quando a demanda altera uma **ação** (desbloqueio, cadastro, baixa, débito — qualquer POST/UPDATE que muda estado), o teste **deve executar a ação real** e evidenciar o efeito. **Não** basta abrir a tela nem só validar o código/SQL.

Sequência obrigatória (local **e** homol):

1. **Estado ANTES** — deixar o registro no estado que a ação vai mudar (ex.: perfil `BLOQUEADO=1`); print da tela + leitura do dado (ex.: saldo).
2. **Executar a ação** — o **POST real** do endpoint alterado (ex.: `perfil/resultado/desbloquear`); registrar **status HTTP + corpo da resposta**.
3. **Estado DEPOIS** — print da tela refletindo a mudança + leitura do dado (ex.: saldo −1; `BLOQUEADO=0`).
4. **Reenvio/idempotência** (quando a correção é sobre isso) — repetir o POST e provar que **não** há novo efeito (ex.: saldo inalterado).

Evidência: **prints antes/depois** + **retorno do POST** + **valor no BD antes/depois**.

### BD para verificar a ação (local × homol)

- **Local (URL L0 do perfil):** a aplicação escreve no **espelho** de homol `aless608_sg_homol` @ `127.0.0.1:3309` (BD central compartilhado) — o agente lê/escreve e verifica o efeito de ponta a ponta.
- **Homol remota:** escreve no **BD do servidor** (o espelho local **não** reflete — gravar no espelho não aparece no servidor). Sem acesso de escrita/leitura ao servidor, o agente executa a ação pela **URL homol** (telas + retorno do POST) e o **estado no BD é conferido pelo usuário** (fluxo de [consultas-bd.md](../sustentacao/consultas-bd.md)). Se o usuário não tiver permissão de escrita em homol, o teste de escrita da ação roda sobre o espelho `aless608_sg_homol` (via URL local), documentando isso.

---

## Ordem obrigatória (I13)

### Passo 1 — Confirmar homol remota

Acesse a URL homol remota do perfil `arquitetura/ambiente-local-{projeto}.md`.

Credenciais: `testes/.credentials.local` — variáveis `PLAYWRIGHT_*_EMAIL` / `PLAYWRIGHT_*_PASSWORD` conforme o perfil `arquitetura/ambiente-local-{projeto}.md`.

### Passo 2 — Executar testes homol (100% pass)

```bash
cd testes
# URL homol: ver o perfil arquitetura/ambiente-local-{projeto}.md
PLAYWRIGHT_BASE_URL={url-homol-do-perfil} npm run test:homol
```

### Passo 3 — I14: criar `evidenciashomol.html`

Arquivo: `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidenciashomol.html`

Conteúdo: bloco **E2E** (print + tabela) + bloco **homol** U01–UN — **sem** implementação, **sem** bloco local.

### Passo 4 — Reverter alterações locais

Executar o comando de restauração de patches do projeto (ver o perfil `arquitetura/ambiente-local-{projeto}.md` — § restauração / `restore-repo`).

> **Por que reverter?** O ambiente local aplica patches em arquivos PHP e arquivos Docker que **não devem entrar no repositório** (ex.: `config.php` com BD local, `docker-compose.yml`). O comando de restauração do projeto reverte esses patches via `git restore` antes de qualquer commit ou PR. As alterações locais são sempre gerenciadas pelo script de ambiente local do projeto (nome e caminho no perfil).

---

## Critério de saída

### I13

- [ ] **I12** OK explícito registrado
- [ ] `npm run test:homol` na homol remota — **100% pass**
- [ ] Cada Uxx: HTTP **200** + evidência conforme tipo
- [ ] Evidências U01–UN em `docs/evidencias/assets/`
- [ ] Patches locais revertidos (comando de restauração do perfil)

### I14

- [ ] `evidenciashomol.html` completo (E2E print+tabela + homol)
- [ ] Seguir **I15** — subagente valida vs análise + plano
