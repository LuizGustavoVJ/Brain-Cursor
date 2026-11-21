# Skills do projeto (Brain / Solides)

Skills **por repositório** (`.cursor/skills/`). O agente deve **ler o `SKILL.md` relevante** antes de implementar, testar ou documentar na stack correspondente.

## Índice

| Skill | Quando usar |
|-------|-------------|
| [antialucinacao-eficiencia](antialucinacao-eficiencia/SKILL.md) | Sob demanda: rigor factual, retomada sem recomeçar, economia de token (complementa o núcleo, não o repete) |
| [regras-de-trabalho](regras-de-trabalho/SKILL.md) | **Transversal:** rigor de escopo, repositório permitido, literalidade da demanda, revalidação após correção — **leitura obrigatória antes de I5** |
| [solides-sustentacao](solides-sustentacao/SKILL.md) | Cards, incidentes, fluxo S1–S6 + I1–I15 — **qualquer repo da frota Solides** |
| [codeigniter2-php-legacy](codeigniter2-php-legacy/SKILL.md) | Controllers, models, helpers, libraries PHP (CodeIgniter 2) |
| [laravel-php-service](laravel-php-service/SKILL.md) | Serviços/adapters Laravel (PHP 8+) |
| [legacy-frontend-jquery](legacy-frontend-jquery/SKILL.md) | Views PHP, jQuery, JS em `assets/` |
| [mysql-solides](mysql-solides/SKILL.md) | Schema, queries, validação local vs produção — genérica, qualquer projeto Solides |
| [evidencias-html-ado](evidencias-html-ado/SKILL.md) | HTML de evidências (I9, I11, I14) |
| [ambientes-e-testes](ambientes-e-testes/SKILL.md) | Docker local + testes Playwright ponta a ponta: E2E (I7), local (I10), homol (I13) |
| [gitlab-deploy-cicd](gitlab-deploy-cicd/SKILL.md) | Pipeline GitLab (deploy staging/prod) + estado do Playwright em CI (roadmap) |
| [integracao-apis](integracao-apis/SKILL.md) | Integrações HTTP (CNPJá, e-mail, HubSpot, Omie, curl) |
| [postman-operacao](postman-operacao/SKILL.md) | Operar o Postman via MCP — antes de qualquer `mcp__postman__*` ou fallback REST |
| [azure-devops-cards](azure-devops-cards/SKILL.md) | Work items, respostas, anexos ADO |

## Mapas de domínio (`dominio-*`)

Skills prefixadas com `dominio-` são **conhecimento de negócio destilado do acervo de `docs/`**, criadas **no repositório de produto**, não no Brain-Cursor canônico.

Regras de uso:

- Ler o mapa **antes** de abrir o acervo bruto — o mapa é a destilação; a análise do card é o detalhe.
- O **código manda**: se o mapa divergir do código, corrigir o mapa no mesmo card.
- Busca no acervo: `.cursor/scripts/kb.sh buscar <termo>` · índice: [`docs/INDICE.md`](../../docs/INDICE.md) (`kb.sh indice` regenera).

São **específicos do repositório** — não entram na replicação cross-repo.

## Relação com regras e guias

- **Regra sempre válida** — AGENTS.md (carregado em toda mensagem) e [`frota/regras.md`](../frota/regras.md) (rodapé de todo agente).
- **Skills** — conhecimento de domínio, stack e processo; consultar quando a tarefa tocar o tema.
  [regras-de-trabalho](regras-de-trabalho/SKILL.md) é a que carrega os limites de escopo e o
  checkpoint I5.
- **Guias** (`.cursor/sustentacao/`, `.cursor/implementacao/`, `.cursor/arquitetura/`) — processo detalhado por etapa.

## Manutenção

Ao adicionar nova skill transversal: criar `{nome}/SKILL.md` e registrar **nesta tabela**. Mapas `dominio-*` nascem no repo de produto via `destilador-dominio`; rodar `kb.sh ancorar` e `kb.sh indice`.