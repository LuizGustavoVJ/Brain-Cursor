# Resposta no chat — implementação

Após cada etapa do [fluxo-implementacao.md](fluxo-implementacao.md):

## I1 — Plano produzido ou atualizado

1. Resumir escopo, ordem de execução e critérios de aceite.
2. Caminho: `docs/implementacoes/plano/impl-*.md`.
3. Informar que segue para a validação do plano (I2-val).

## I2-val — Plano validado

1. Status final (`Aprovado` ou motivos de recusa).
2. Se recusado: apontamentos + nova rodada.
3. Se aprovado: seguir I3.

## I3–I4 — Aprovação humana do plano

### I3 — Aguardando revisão

1. Confirmar fluxo, análise e plano aprovados.
2. Caminho do documento para revisão.
3. **Solicitar OK explícito** para I5.
4. **Não** alterar código.

### I4 — OK recebido

Confirmar OK e iniciar I5.

## I5 — Código entregue

1. Resumir alterações vs plano.
2. Doc **executada:** `docs/implementacoes/executada/impl-*.md`.
3. Seguir **I6** (validação código).

## I6 — Implementação validada

1. Status em `## Validação do código`.
2. Se aprovado: seguir I7 (E2E).

## I7 — Testes E2E executados

1. Comando: `cd testes && npm run test:e2e`.
2. Resultado: **N/N pass (100%)** ou falhas a corrigir.
3. Se 100% pass: seguir I8.

## I8 — Documento testes E2E

1. Caminho: `docs/evidencias/anexos/{tema-slug}/{card-id}-{Titulo-Slug}/testes-e2e.md`.
2. Seguir I9.

## I9 — HTML de evidências (E2E + implementação)

1. Caminho: `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidencias.html`.
2. Secções: plano executado, alterações, ACs, **testes E2E** (print Playwright + tabela “Detalhamento dos cenários” — padrão de referência).
3. PNG: `docs/evidencias/assets/.../{card-id}-e2e-playwright.png`.
4. **Não encerrar** — informar que segue **I10 local**.

## I10 — Testes local URL

1. Comando: `cd testes && npm run test:local` (URL L0: ver o perfil `arquitetura/ambiente-local-{projeto}.md`).
2. Resultado: **N/N pass (100%)**; evidências tela + HTTP 200 (L01–LN).
3. **Não encerrar** — informar que segue **I11** (doc + HTML local + subagente).

## I11 — HTML local validado (subagente)

1. `testes-local.md` registrado.
2. Bloco **local** L01–LN em `evidencias.html`.
3. Subagente `validador-tecnico` valida bloco local **e bloco E2E (I9)** — aprovação pelo agente **não conta**.
4. Status em `## Validação do HTML local` (`Aprovado` ou recusa).
5. Se aprovado: seguir **I12** — solicitar deploy homol e **OK explícito**.

## I12 — Gate deploy homol

1. Informar que local (I10/I11) está concluído.
2. **Solicitar ao usuário** confirmar deploy em homol remota.
3. **Aguardar OK explícito** antes de I13.
4. **Não** executar `test:homol` nesta etapa.

## I13 — Testes homol URL remoto

1. Confirmar I12 OK recebido.
2. Comando: `PLAYWRIGHT_BASE_URL={url-homol-do-perfil} npm run test:homol` (URL homol: ver o perfil `arquitetura/ambiente-local-{projeto}.md`).
3. Resultado: **N/N pass (100%)**; evidências U01–UN.
4. Reverter patches locais após evidências (comando de restauração do perfil).
5. **Não encerrar** — informar que segue **I14**.

## I14 — HTML homol

1. Caminho: `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/evidenciashomol.html`.
2. Conteúdo: bloco **E2E (print Playwright + tabela detalhada — mesmo padrão I9)** + bloco homol U01–UN — **sem** impl, **sem** local.
3. **Não encerrar** — informar que segue **I15** (validação subagente).

## I15 — HTML homol validado (subagente)

1. Subagente compara `evidenciashomol.html` com análise + plano + executada.
2. Status em `## Validação do HTML homol` em **`executada/`**.
3. Se **aprovado:** seguir **Pós-I15** (perguntar: posto eu ou entrego o comando?) antes do encerramento.
4. Se **recusado:** apontamentos + correções + revalidação.

## Pós-I15 — entrega das evidências homol (só se houve desenvolvimento)

**Pergunte antes de postar:** *"Posto eu o `evidenciashomol.html` no card `<n>`, ou te entrego o comando para você postar?"* — posta só com "sim" explícito (vale só para aquela postagem); senão entrega o comando.

1. Informar o caminho do `evidenciashomol.html` e que o destino é o **card de DESENVOLVIMENTO** — pode ser diferente do card do incidente; deixar o número como placeholder, nunca assumir que é o mesmo.
2. Postar (após o "sim") ou exibir o comando pronto: `ADO_PROJECT=<GUID-do-card-de-dev> python3 .cursor/scripts/ado_update_comment.py <evidenciashomol.html> <card-de-dev> [comment_id]` (mesmo método da Pós-I11).
3. **Encerramento** do ciclo de implementação.
