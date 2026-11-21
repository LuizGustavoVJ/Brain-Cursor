# Regras invioláveis da frota

Fonte única. O rodapé de cada agente tem só 3 linhas (leia `regras.md`, gatilho, retorno) e aponta
para cá — **leia este arquivo antes de agir**. Ao editar, edite **aqui**, nunca no agente.

## 1. Idioma

**Português BR sempre**, em toda saída, independente do idioma da pergunta. Sem exceção.

## 2. Azure DevOps

**Subagente NUNCA posta** — nem comentário, nem anexo, nem alteração de estado, nem link de PR.
Ler card, ler comentários, montar o HTML: **sim**. Publicar: **não**.
Você entrega caminho do arquivo + GUID do projeto + comando pronto ao orquestrador.

Quem posta é **só o contexto principal** (é quem fala com o usuário), e só depois de perguntar
no chat *"Posto eu o `<arquivo>` no card `<n>`, ou te entrego o comando?"* e receber **"sim"
explícito** — autorização por postagem, não por sessão. Estado/campos do work item, links, anexo
avulso, PR/MR, pipeline, wiki e test plan seguem proibidos para todos.

## 3. Git

Leitura (`log`, `diff`, `show`, `blame`, `status`, `fetch`) é livre. `commit`, `push`, `pull` e
criar branch só com OK explícito do usuário **na mensagem atual** — "ajuste para subir" **não** é
autorização. `merge` (local ou no GitLab), `rebase`, `reset`, `checkout` que altere a árvore e
reapontar branch só quando o usuário pedir; por padrão são dele. MR pronto: entregue o link para
ele clicar. Mensagem de commit: só a linha de título, sem corpo e sem `Co-Authored-By`.

**Staging nunca entra na branch do card (regra do usuário, 21/09/2026).** NUNCA `git merge
origin/staging` — nem de qualquer branch de integração/homologação — para dentro de branch de
trabalho ou de release, e nenhuma branch de trabalho nasce da staging. A mesma branch costuma
alimentar o MR de release, e o merge arrasta a staging inteira, inflando o MR com código não
promovido (incidente checkout !445). Conflito de um MR contra a `staging` resolve-se numa
**branch separada dedicada ao alvo staging** (`<card>_etapa_N_staging_<desc>`), nunca na branch do
card. Não é questão de ter OK — é não fazer.

**Ordem de branch, em qualquer repositório** (incidente do MR de release, 25/08):
1. `<card>_release` a partir da `master`/`main` atualizada;
2. push da release **sem nenhuma alteração**;
3. branch de trabalho `<card>_<descricao>` a partir da release;
4. commit e push só ao final do trabalho, com OK explícito — e antes, `.cursor/scripts/local.sh
   restore-repo` (nada de patch local em commit ou MR).

## 4. Banco de dados

| Ambiente | Quem executa |
|---|---|
| **Produção** | **O usuário.** Você só monta a query e explica o que ela faz. |
| **Local e homologação** | **Você.** Não pergunte — execute (`SELECT`, DDL de migration, DML). |

## 5. Escopo

- Só o que foi pedido. Nada por iniciativa própria, nada "de brinde".
- Por padrão, só o repositório aberto na IDE. **Ler** outro repo é livre; alterar **código de
  produto** de outro repo exige permissão pedida antes (AGENTS.md § *Regras de escopo*).
- Fluxo do card, gatilho de especialista, collection Postman e destilação **fazem parte do pedido**.
- **Exceção permanente:** alteração no `.cursor/`/`AGENTS.md` é replicada em **todos** os repos
  da máquina sem pedir — `bash .cursor/scripts/propagar.sh` (AGENTS.md § *Propagação do Brain*).
- Não renomear variável, arquivo ou função sem pedido explícito.
- Ambiguidade que muda o resultado → pergunte (subagente: declare no retorno). Se não muda,
  registre no documento. **Não** resolva por suposição.

## 6. Verificação

**Nunca afirme por dedução o que é verificável.** Consulte a fonte — código, banco, endpoint,
documentação oficial — e cite `arquivo:linha` ou a URL. Se não deu para verificar, diga
explicitamente que não deu: risco não avaliado aparece como **não avaliado**, nunca como ausente.

## 7. Conhecimento antes de investigação

`.cursor/scripts/kb.sh buscar <termo>` **primeiro**. Os mapas `dominio-*` são destilação já
conferida; `docs/` é o detalhe. `grep` no código é o **último** recurso, não o primeiro.
Se o mapa divergir do código, **o código manda** — e o mapa precisa ser corrigido no mesmo card.

## 8. Formato de retorno

Sua resposta final **é o valor de retorno** para o orquestrador, não uma mensagem de chat.
**No máximo 15 linhas.** Linha 1 `Artefato: <caminho>`, linha 2 `Veredito: …`, depois o que o
próximo agente precisa saber. Validadores seguem o formato binário próprio. **Nunca cole o conteúdo do artefato** — o orquestrador lê o arquivo se precisar.
Despejar conteúdo infla o contexto dele, que é exatamente o que esta frota existe para evitar.

## 9. Gatilho de especialista — por artefato, não por etapa

Produziu ou alterou SQL, migration, rota, cálculo de dinheiro, credencial, view, container,
pipeline ou dependência? **O especialista da classe entra ANTES de o artefato sair** — entregar,
executar, comitar ou fechar a etapa. Vale em **qualquer** etapa e também fora do fluxo de card.
Caso duro: **consulta SQL não sai sem o `especialista-sql`.**

Você **não abre subagente** (agente de etapa não tem a ferramenta `Agent`): declare no retorno
`gatilho pendente: <classe>` e o orquestrador chama. Registro é **uma linha** —
`<agente> · OK|Ajustar|Bloqueante · ponto · onde foi acatado` — gravada no
`_processo-revisoes.md` interno, **nunca** no documento oficial (§ 11).

Condições de cada agente: [`gatilhos.tsv`](gatilhos.tsv) (`frota.sh gatilhos`). Mecanismo e
limites: [`gatilhos.md`](gatilhos.md). Especialista é insumo da etapa — **não dispensa gate**.

## 10. Limites de ferramenta

- **MCP Playwright** só nas etapas de teste (I7, I10, I13, I14) e só no `testador`/contexto
  principal; o `escritor-evidencias` não tem navegador — embute os prints que os specs gravaram.
- **Postman:** request novo/alterado por `createCollectionRequest`/`updateCollectionRequest`;
  `putCollection` (substitui a collection inteira) é barrado pelo classificador.
- **Validação:** no máximo 3 rodadas por etapa; na 3ª recusa, pare e escale ao usuário
  (`fluxo-completo.md` § *Teto de 3 rodadas*).
- Arquivo entregável vai em `docs/` do projeto — nunca em `/tmp` nem no scratchpad.
- Não reproduzir stdout de Playwright em chat, `.md` ou HTML.
- Se você é somente leitura (sem `Write`/`Edit`), isso é deliberado: proponha, não aplique.

## 11. Documento oficial de card não cita agente da frota

Regra do usuário, 23/09/2026. O que o usuário lê ou o que vai ao ADO — análise `.md`,
`plano.html`, `evidencias.html`/`evidenciashomol.html`, qualquer artefato de card — **nunca**
traz nome de subagente/especialista (`especialista-sql`, `escritor-evidencias`), frase como
"revisado pelo especialista-X" ou "o agente só monta a query", nem a seção/tabela
"Revisões de especialistas". **Exceção:** nome de coluna, tabela ou balde do banco
(`pendente_revisar`, `historico_seguro`) não é menção a agente e permanece.

O registro do gatilho por artefato (§ 9) continua **obrigatório** — só muda de lugar: vive em
`_processo-revisoes.md`, arquivo interno de processo na pasta do card, marcado como
não-entregável (não vai ao ADO, não sustenta leitura de stakeholder). O gate não caiu; o
documento oficial pode, no máximo, carregar um comentário HTML apontando para esse arquivo.
