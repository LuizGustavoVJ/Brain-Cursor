# Estado do projeto — CIT

Registrar somente decisões **estáveis** e úteis para próximas tarefas. Formato: Contexto → Decisão → Impacto.

## Estado atual

- Projeto principal: `/var/www/html/cit`
- Repositório de trabalho: `cit` por padrão — alterar outro repo é possível **com permissão pedida antes** (CLAUDE.md § *Regras de escopo*)
- Estrutura `docs/`: [estrutura-docs.md](estrutura-docs.md) — índice em [`docs/README.md`](../../docs/INDICE.md)
- Ambiente local: [ambiente-local-cit.md](ambiente-local-cit.md) + [alteracoes-ambiente-local-cit.md](alteracoes-ambiente-local-cit.md)
- Env local: `.env` na raiz do repo (modelo: `.env.example`)
- **L0 (pré-requisito):** subir ambiente local + URL no chat antes de B0 (bifurcação) → S1 (`docker compose up -d`)
- Testes Playwright: `testes/E2E/` (I7) + `testes/local/` (I10, URL local, L01–LN) + `testes/homol/` (I13, URL remota)
- BD local (schema agente): `127.0.0.1:3309` / `solides-pipedrive`
- BD local (I7 / dev): `homol_cit` em `127.0.0.1:3309` — **não é produção**; instância MySQL local (container `solides-mysql-homol`)
- MySQL central: container `solides-mysql-homol` (imagem `cit-db:local`, serviço `db` no compose do cit) — compartilhado por todos os projetos Solides; subir cit é necessário para disponibilizá-lo
- Homol remoto (I13): `https://homol.cit.solides.adm.br/` — BD do **servidor** de homol (deploy); ambiente **externo**, acesso por URL + usuário/senha, **sem subir ambiente local**
- Subagentes de validação: `validador-leve` (Haiku) em S2/plano curto e `validador-tecnico` (Opus) em S4/S6a-val/I2-val/I6/I11/I15 — validação binária: **Aprovado** ou **Recusado**

## Decisões consolidadas — Sustentação

| Contexto | Decisão | Impacto |
|----------|---------|---------|
| Operação geral | Ciclo fluxo → validação → análise → validação → decisão | Padroniza entendimento antes de alterar código |
| Decisão de implementação | Agente avalia se código precisa mudar ou análise basta | Evita mudanças desnecessárias |
| Ciclo de implementação | I1–I15 em `.claude/implementacao/` | Plano → E2E → HTML E2E → local URL → HTML local → entrega das evidências (pergunta antes de postar) → homol → HTML homol → validação final → encerramento |
| Plano de implementação | `docs/implementacoes/plano/`; validação **I2-val** pelo subagente | Código segue plano revisado |
| Consolidação executada | `docs/implementacoes/executada/`; validações **I6** e **I11** | Registro pós-código e testes |
| Testes E2E (I7) | Playwright `testes/E2E/`; URL Docker `http://127.0.0.1:8083/` (Traefik → `localhost:8082`); `testes-e2e.md` (I8) | 100% pass antes de I9 |
| Testes local URL (I10) | `testes/local/` + URL **local** (`http://localhost:8082/`) — L01–LN | Obrigatório quando houve implementação |
| Testes homol URL (I13) | `testes/homol/` + URL **homol remota** | **Sempre obrigatório** quando houve implementação; nunca localhost; apenas após I12 OK |
| Validação HTML local (I11) | Subagente `validador-tecnico` (Opus) vs análise + plano — Aprovado/Recusado | Gate do bloco local; segue Pós-I11 (entrega ao usuário) → I12 |
| Validação HTML homol (I15) | Subagente `validador-tecnico` (Opus) valida `evidenciashomol.html` — Aprovado/Recusado | **Único gate de encerramento** do card com implementação |
| Ambiente local vs homol | L0 obrigatório antes de B0 (bifurcação) → S1; URL no chat | Agente só inicia fluxo após app+BD locais ok |
| Homol remoto | Ambiente **externo** — sem Docker, sem subir local; acesso por URL+credenciais | Nunca usar localhost em I13 |
| MySQL central | Container `solides-mysql-homol` definido no compose do cit; compartilhado por todos os projetos | Subir cit = subir MySQL para todos |
| Organização `docs/` | Por `{tipo}` + `{card-id}` | Consulta a incidentes e demandas |
| Evidências | HTML + imagens por card; `{card-id}-qN.png` | Separação clara por card |
| Azure DevOps | Agente monta o HTML final e **pergunta a cada postagem** se posta ele (`ado_update_comment.py`, só com "sim") ou entrega o comando | Publicação segue sob controle humano, sem o passo manual quando o usuário autoriza (decisão de 25/09/2026) |
| BD produção | Agente monta queries; usuário executa | Sem acesso do agente a produção |
| Conclusão análise | 100% causa raiz + resposta/solução | Evita fechamento prematuro |
| Escopo | Nunca implementar além do pedido; nunca renomear variáveis sem solicitação | Aderência estrita ao escopo da demanda |
| Skills por stack | Consultar skill relevante antes de codar/testar | Agente usa contexto de stack correto |
| Documentação ambiente | Operacional em `.claude/arquitetura/`, não em `docs/` | `docs/` reservado a artefatos de card |

Novas decisões estáveis devem ser acrescentadas nesta tabela.
