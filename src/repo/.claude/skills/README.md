# Skills do projeto (Solides)

Skills **por repositório** (`.claude/skills/`). O agente deve **ler o `SKILL.md` relevante** antes de implementar, testar ou documentar na stack correspondente.

## Índice

| Skill | Quando usar |
|-------|-------------|
| [antialucinacao-eficiencia](antialucinacao-eficiencia/SKILL.md) | Sob demanda: rigor factual, retomada sem recomeçar, economia de token (complementa o núcleo, não o repete) |
| [regras-de-trabalho](regras-de-trabalho/SKILL.md) | **Transversal:** rigor de escopo, repositório permitido, literalidade da demanda, revalidação após correção — **leitura obrigatória antes de I5** |
| [solides-sustentacao](solides-sustentacao/SKILL.md) | Cards, incidentes, fluxo S1–S6 + I1–I15 — **qualquer repo da frota Solides**, não só o CRM |
| [codeigniter2-php-legacy](codeigniter2-php-legacy/SKILL.md) | Controllers, models, helpers, libraries PHP |
| [laravel-php-service](laravel-php-service/SKILL.md) | Contrapartida Laravel: os 5 serviços/adapters (`omie-adapter`, `hubspot-adapter`, `gestao-adapter`, `debt-processing-service`, `payment-processing-service`) — atenção ao Laravel 9/PHP 8.1 do `payment-processing-service` |
| [legacy-frontend-jquery](legacy-frontend-jquery/SKILL.md) | Views PHP, jQuery, JS em `assets/` |
| [mysql-solides](mysql-solides/SKILL.md) | Schema, queries, validação local vs produção — genérica, qualquer projeto Solides |
| [evidencias-html-ado](evidencias-html-ado/SKILL.md) | HTML de evidências (I9, I11, I14) |
| [ambientes-e-testes](ambientes-e-testes/SKILL.md) | Docker local + testes Playwright ponta a ponta: E2E (I7), local (I10), homol (I13) — specs, `npm run test:*`, matriz L01–LN/U01–UN |
| [gitlab-deploy-cicd](gitlab-deploy-cicd/SKILL.md) | Pipeline GitLab (deploy staging/prod) + estado do Playwright em CI (roadmap) |
| [integracao-apis](integracao-apis/SKILL.md) | CNPJá, e-mail, HubSpot, Omie, curl |
| [postman-operacao](postman-operacao/SKILL.md) | Operar o Postman do Luiz via MCP (workspace, chave, collections, environments) — antes de qualquer `mcp__postman__*` ou fallback REST |
| [azure-devops-cards](azure-devops-cards/SKILL.md) | Work items, respostas, anexos ADO |
| [dominio-termo-aceite](dominio-termo-aceite/SKILL.md) | **Domínio (cit):** termo de aceite — criação, aceite, roteamento Mid/Farmer, ganho, pagamento no aceite |
| [dominio-superficie-publica](dominio-superficie-publica/SKILL.md) | **Domínio (cit):** o que responde sem sessão — `SessionHook`, as duas whitelists, exceção do `termo_aceite` |
| [dominio-login-unificado-partners](dominio-login-unificado-partners/SKILL.md) | **Domínio (cit):** login unificado + fallback partners/CRM — causa raiz de "CNPJ vazio" no dropdown de cancelamento |
| [dominio-cancelamento-assinatura](dominio-cancelamento-assinatura/SKILL.md) | **Domínio (cit):** cancelamento de assinatura — formulário público, produtos por 3 fontes, solicitação/reversão/efetivação por CODPRODUTO, SenseData, Omie, cascata GUSUARIO por IDEMP |
| [dominio-pagamento-cartao](dominio-pagamento-cartao/SKILL.md) | **Domínio (cit):** pagamento por cartão (Pagar.me, feature 161899) — JWT ao checkout, webhook via lambda, cobrança avulsa mensal, régua de recusa |
| [documentacao-api-swagger](documentacao-api-swagger/SKILL.md) | Spec de API (OpenAPI/Swagger, AsyncAPI, ADR) e o estado real do Swagger no cit |
| [financeiro-modulo](financeiro-modulo/SKILL.md) | Movimentos, baixa de boleto, retorno bancário — **só** onde existe o diretório `financeiro/` (tipicamente o CRM) |


## Mapas de domínio (`dominio-*`)

Skills prefixadas com `dominio-` são **conhecimento de negócio destilado do acervo de `docs/`**, não de stack: entidades, tabelas, rotas, ordem do fluxo, integrações e armadilhas já comprovadas em cards anteriores, cada afirmação ancorada em `arquivo:linha` ou consulta ao banco.

Servem para o agente **não redescobrir** o que já foi apurado. Regras de uso:

- Ler o mapa **antes** de abrir o acervo bruto — o mapa é a destilação; a análise do card é o detalhe.
- O **código manda**: se o mapa divergir do código, corrigir o mapa no mesmo card.
- **Alimentar ao encerrar** (Pós-S6a / Pós-I15): nova armadilha, nova linha no acervo, correção do que o card provou diferente.
- **Âncoras se autocorrigem:** `kb.sh ancorar` trava o texto da linha apontada — linha única (`#L123`) e faixa (`#L123-L145`); `kb.sh verificar` conserta os números que o código moveu e aponta as **órfãs** (afirmação que não vale mais — decisão humana).
- **`MOVEU?` = palpite explícito:** fim de faixa (`});`, `}`) repete no arquivo, então o desempate é por proximidade. A marca `?` existe para você conferir; nunca corrige no escuro.
- **`S/TRAVA` = âncora que ninguém verifica** — está no mapa e fora do lock. Rode `kb.sh ancorar` depois de acrescentar âncora nova.
- O ciclo é cobrado por hook: editar arquivo citado marca o mapa como sujo, e o encerramento pede `/destilar`.
- Busca no acervo: `.claude/scripts/kb.sh buscar <termo>` · índice: [`docs/INDICE.md`](../../docs/INDICE.md) (`kb.sh indice` regenera).

São **específicos do repositório** — não entram na replicação cross-repo.

## Relação com regras e guias

- **Regra sempre válida** — CLAUDE.md (carregado em toda mensagem) e [`frota/regras.md`](../frota/regras.md) (rodapé de todo agente).
- **Skills** — conhecimento de domínio, stack e processo; consultar quando a tarefa tocar o tema.
  [regras-de-trabalho](regras-de-trabalho/SKILL.md) é a que carrega os limites de escopo e o
  checkpoint I5 (por que não é mais pasta de regras:
  [estrutura-claude.md](../arquitetura/estrutura-claude.md) § `skills/`).
- **Guias** (`.claude/sustentacao/`, `.claude/implementacao/`, `.claude/arquitetura/`) — processo detalhado por etapa.

## Manutenção

Ao adicionar nova skill: criar a pasta `{nome}/SKILL.md` e registrar **nesta tabela** — ela é a
fonte única do catálogo de skills. Não replicar a lista em [estrutura-claude.md](../arquitetura/estrutura-claude.md):
aquela árvore descreve **pastas**, não arquivos, justamente para não desatualizar. Se a skill for
um mapa `dominio-*`, rodar também `kb.sh ancorar` e `kb.sh indice`.
