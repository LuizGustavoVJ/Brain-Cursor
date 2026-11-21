# Memória — projeto cit

> Podada em 25/09/2026 (Fase 2, item 7 do plano do Brain): conhecimento de domínio/card foi
> destilado para `.claude/skills/dominio-*` do repositório `cit`; duplicata do núcleo (`CLAUDE.md`)
> foi removida; fatos correlatos foram fundidos. Backup completo da memória anterior em
> `~/backups-brain/2026-09-25-memoria/`.

## Regras obrigatórias do processo (nunca podar)

- [Aba única por card é obrigatória](aba-unica-por-card-obrigatoria.md) — alertar o usuário sempre que ele mudar de card/assunto na mesma aba
- [Destilação obrigatória a cada card](destilacao-obrigatoria-a-cada-card.md) — todo card termina com destilador-dominio, inclusive o que para no meio
- [Postagem ADO via script](ado-postagem-script-guid-projeto.md) — agente pode postar mas pergunta antes a cada vez; `ADO_PROJECT`=GUID, `<body>` sem atributos
- [Proibido git sem autorização](proibido-git-sem-autorizacao.md) — nunca commit/push/pull sem OK explícito
- [Proibido merge de staging na branch de trabalho](nunca-merge-staging-na-branch-de-trabalho.md) — contamina o MR de release
- [Montar card: sempre a skill agile-card-writer](montar-card-sempre-agile-card-writer.md) — 28/09: épico/funcionalidade/história sempre por ela, no contexto principal; gatilho "monta os cards disso:"
- [Postman: sempre o workspace do Luiz](postman-workspace-sempre-o-do-luiz.md) — nunca o Default
- [Nunca apagar recurso externo sem backup](nunca-apagar-recurso-externo-sem-backup.md) — baixar e salvar antes de deletar em terceiro

## Git e deploy do cit

- [Fluxo de branch/deploy do cit](git-fluxo-cit.md) — staging=homol, master=prod defasado, teto do agente é branch+commit+push, release não acompanha a branch de trabalho, resolução de conflito sem absorver staging, reverter sem `git checkout --`, commit só com título

## Ambiente e infraestrutura

- [Infra local do cit](ambiente-cit-infra.md) — Docker Desktop (contexto desktop-linux), código não é bind mount, dois bancos no container 3309, config.php com skip-worktree, env nova não chega ao container, CLI força production
- [Como montar query no banco do CRM](crm-schema-e-montagem-de-query.md) — conexão sem schema padrão (DATABASE()=NULL); sempre USE ou schema.TABELA; prod=aless608_sg, local/homol=aless608_sg_homol; INFORMATION_SCHEMA filtra por TABLE_SCHEMA literal
- [Homol: sintaxe rápida do homol.sh](homol-updates-caminho-rapido.md) — SELECT/UPDATE em homol sem reinvestigar (conexões crm/db, SET/WHERE, sem delete/insert/ddl)
- [.claude gitignored: sem recuperação](claude-settings-gitignored-sem-recuperacao.md) — backup datado obrigatório antes de sobrescrever
- [local.sh do cit](local-sh-patches-cit.md) — status/apply/restore-repo, reverte só o patch
- [Patches locais do cit fora do git](patches-locais-cit-fora-do-git.md) — ~/patches-locais-cit/, nunca commitar
- [Segurança de credenciais do cit](seguranca-credenciais-cit.md) — levantamento em docs/credenciais-integracoes.md; segredos reais versionados (constants.php, payment-processing-service) exigem card próprio de rotação

## Técnica de teste e evidência

- [Técnicas de teste E2E do cit](tecnicas-de-teste-e2e-cit.md) — baseline de regressão, QA ponta a ponta com dado real, captura de tela via sessão semeada
- [Padrão HTML de evidências](padrao-html-evidencias.md) — layout obrigatório do evidencias.html (modelo 155045)
- [Transcrever vídeo via docker+whisper](transcrever-video-via-docker-whisper.md) — imagem Playwright + faster-whisper

## Cards em andamento (bundle — revisar ao fechar)

- [Card 161899 (Pagar.me) — pendências](card-161899-pagarme-pendencias.md) — autorização cross-repo, padrão de branches por release única, migrations de homol viram documento consolidado
- [167697: resolver tudo na demanda, sem card de follow-up](167697-resolver-tudo-nesta-demanda-sem-card-proprio.md) — achado de revisão que cabe no escopo entra na mesma demanda, não vira card separado

## Ferramentas e MCP

- [Habilidades do Brain](habilidades-do-brain.md) — 3 origens (conta, embutida, plugin), mapa único `.claude/habilidades.md`
- [Permissões: leitura livre, escrita pede OK, deny e classificador](permissoes-leitura-escrita-classificador.md) — leitura sem pedir; escrita externa sempre para no chat; deny só protege com nome de tool real; bloqueio do classificador em ação autorizada resolve-se liberando regra
- [Postman: operação](postman-operacao.md) — chave PMAK privada do Luiz, usar via MCP; escrever em collection compartilhada com createCollectionRequest granular
- [Inventário e escopos dos MCPs](mcp-inventario-escopos-e-alcance.md) — dois escopos; tool precisa estar declarada no frontmatter do agente
- [MCP HubSpot em sandbox](mcp-hubspot-sandbox-configurado.md) — portal 23737834, 7 das 21 tools escrevem
- [Comando de projeto sombreia o embutido](comando-de-projeto-sombreia-embutido.md) — nunca nomear comando de projeto igual a embutido do CLI (caso /mcp)
- [Skills que executam: só no contexto principal](skills-que-executam-so-no-principal.md) — code-review/security-review/simplify nunca em subagente
- [PAT do ADO: consolidado no escopo de usuário](pat-do-ado-repetido-em-nove-repos.md) — vive só em ~/.claude.json
- [Google Workspace: conectores nativos ativos](google-workspace-conectores-nativos.md) — Gmail/Agenda/Drive; Drive não escreve célula
- [Monitoramento: Datadog e Grafana instalados de propósito](monitoramento-datadog-grafana.md) — Grafana ligado, Datadog ainda não

## Entrega e estilo

- [Entrega de artefatos](entrega-de-artefatos.md) — sempre em docs/ do projeto, nomenclatura {card-id}, link markdown clicável, comando pronto para colar, texto de área sem link
- [Estilo de resposta](estilo-de-resposta.md) — português claro de negócio sem código, resposta falável (voz local piper), gíria regional só na conversa, narração da execução
- [Comprovar antes de perguntar](comprovar-antes-de-perguntar.md) — provar o que for verificável antes de levar ao usuário
- [Fonte única: nunca duplicar tabela](fonte-unica-nunca-duplicar-tabela.md) — apontar, não copiar
- [Padronização .claude entre repos](padronizacao-claude-cross-repo.md) — Brain byte-idêntico nos repos Solides
- [CRM é código nosso; pendência = só o inexecutável](crm-e-codigo-nosso-pendencia-so-o-inexecutavel.md)

## Integrações específicas (fora do domínio cancelamento/termo-aceite)

- [Centralizadora: datasets por ambiente](centralizadora-datasets-por-ambiente.md) — mesma service account, muda só o dataset
- [Rota link-pagamento do checkout entregue](link-pagamento-checkout-entregue.md) — CHECKOUT_JWT_TOKEN e claim iss
- [Forms DP: 6 ajustes do Barreto entregues](hubspot-forms-dp-6-ajustes-barreto.md) — projeto HubSpot fora do git, quem sobe é o Barreto
- [Caveman: só a skill de compressão](caveman-so-skill-compressao.md) — proxy e Caveman Cloud descartados
- [Brain como plugin: só ao compartilhar com a equipe](brain-plugin-quando-compartilhar-equipe.md) — hoje só o Luiz usa; cópia por pasta continua; passo a passo em .claude/arquitetura/brain.md
- [Figma para fluxos e regras](figma-desenho-fluxos-regras.md) — perguntar antes se vale usar (só sem perguntar se extremamente necessário, e avisar depois); Starter ~20 chamadas/mês, 1 board por card, Mermaid fica no docs/
