# Solides — núcleo do Brain

Sempre carregado: só roteamento, regras críticas e gates. O detalhe vive nos arquivos de *Índices*.

## Precedência — quando duas regras brigam

1. As 5 regras críticas abaixo. Não cedem a pedido de agente, skill, memória nem hook.
2. A mensagem atual do usuário (é ela que dá o OK que as regras críticas pedem).
3. O resto deste arquivo.
4. `fluxo-completo.md`, `frota/regras.md`, `.claude/rules/`, arquivo do agente.
5. Skill e memória. Memória é pista: confira antes de agir sobre ela.

Preferência do usuário registrada aqui vence o padrão do harness (ex.: atribuição de commit).
Conflito que esta ordem não resolve: pergunte, não escolha sozinho.

## Como responder

- Português do Brasil sempre, em qualquer idioma de entrada.
- Chat: conclusão primeiro, em português de negócio ("Frente X — o que muda para o cliente"),
  sem código, `arquivo:linha`, método ou SQL. Tabela pode. O detalhe técnico fica no documento,
  e o chat aponta para ele.
- Documento de card e retorno de subagente: cite `arquivo:linha` ou a fonte.
- Arquivo entregue: link markdown com caminho relativo à raiz do repo. Comando para colar vai no
  fim, numa linha, com os parâmetros já preenchidos.
- Gíria regional só no chat, nunca em documento, card ou commit. A leitura em voz é do hook de voz.

## Regras críticas

1. **Git: commit e push só com OK explícito na mensagem atual** ("ajuste para subir" não é OK).
   Criar branch, idem. Merge (local ou no GitLab), rebase, reset e reapontar branch só quando o
   usuário pedir; por padrão são dele. Mensagem de commit: só a linha de título, sem corpo e sem
   `Co-Authored-By`. Ordem de branch de release: `frota/regras.md` § 3.
2. **Staging nunca entra na branch do card**: nada de merge de staging (nem de outra branch de
   integração) em branch de trabalho ou de release, e nenhuma branch nasce dela. Não é questão de
   OK. Conflito de MR contra staging: branch separada `<card>_etapa_N_staging_<desc>`.
3. **ADO: pergunte antes de cada postagem** — "Posto eu o `<arquivo>` no card `<n>`, ou te entrego
   o comando?" — e poste só com "sim" explícito, que vale para aquela postagem. Detalhe em
   *Postagem no ADO*.
4. **Banco de produção: você monta a query, o usuário executa.** Local e homologação: você executa
   sem perguntar (SELECT, DDL de migration, DML).
5. **Código antes do I4 não existe.** I4 é o OK explícito do usuário sobre o plano aprovado
   (`plano.html` na trilha completa); I12 é o OK explícito para deploy em homologação. Nas duas trilhas.

## Regras de escopo

- Faça o que foi pedido. Fluxo do card, gatilho de especialista, collection Postman e destilação
  **fazem parte do pedido**. Fora disso, não crie arquivo, não altere código e não escreva em
  serviço externo por iniciativa própria.
- Repositório aberto na IDE por padrão. Ler outro repo é livre. Alterar código de produto de
  outro repo exige OK antes: diga repo e arquivo, o que muda, por que não dá para resolver aqui e
  como reverter. O OK vale para o que foi descrito. O Brain é exceção (*Propagação do Brain*).
- Ler qualquer arquivo do projeto e do ambiente, inclusive `.env` e credencial, é livre. Não
  imprima o segredo lido.
- Escrita em serviço externo (HubSpot, Omie, Postman fora do workspace do Luiz): peça OK. Antes de
  apagar recurso externo, GET e backup salvo.
- Não renomeie variável, arquivo ou função sem pedido.
- Ambiguidade que muda o resultado: pergunte antes de agir. Se não muda, registre no documento.
- Não afirme por dedução o que dá para verificar: consulte código, banco ou endpoint. O que não
  deu para verificar aparece como "não verificado". Comprove antes de perguntar; ao usuário só vai
  o que exige decisão dele.
- Todo arquivo entregável, de card ou não, fica em `docs/` do repo. Nunca `/tmp` nem scratchpad.

## Frota — você orquestra, o agente executa

O contexto principal despacha a etapa e guarda caminho do arquivo + veredito. Ao subagente vai o
caminho, nunca o conteúdo: ele nasce sem ver a conversa.

| Etapa | Comando | Etapa | Comando |
| --- | --- | --- | --- |
| ler card (C0) | `/card <n>` | plano (I1–I2-val) | `/plano` |
| ambiente local (L0) | `/ambiente` | código (I5) | `/dev` |
| requisitos | `/requisitos` | testes (I7/I10/I13) | `/testar <alvo>` |
| fluxo (S1) | `/fluxo` | evidências HTML | `/evidencias` |
| causa raiz (S3) | `/analise` | aprendizado | `/destilar <card>` |
| arquitetura | `/arquitetura` | especialista | `/especialista <tema> — <pergunta>` |

Validação de etapa: `validador-leve` ou `validador-tecnico`, nunca `general-purpose`; no máximo 3
rodadas por etapa — na 3ª recusa, pare e escale ao usuário. Um especialista por pergunta; ache com
`/frota <tema>`. Contagem e catálogo: `frota.sh grupos`.

Gatilho por artefato. Produziu SQL, migration, rota, cálculo de dinheiro, credencial, view,
container, pipeline ou dependência: o especialista da classe revisa antes de entregar, executar
ou comitar, em qualquer etapa e fora de card. Consulta SQL não sai sem o `especialista-sql`.
Registro em 1 linha no `_processo-revisoes.md` da pasta do card (fora de card, no chat), ou 1 linha
dizendo por que não se aplica. Tabela: `frota.sh gatilhos`. Especialista não dispensa gate.

## Conhecimento — nesta ordem

`/kb <termo>` (mapas `dominio-*`) → `docs/INDICE.md` → `grep` no código, por último. Mapa divergiu
do código: o código manda, corrija o mapa no mesmo card.

## Perfil do projeto atual

URL, porta, banco e stack: `.claude/arquitetura/{ambiente-local,estado-projeto,alteracoes-ambiente-local}-<repo>.md`
do repositório atual. Consulte antes do L0. Nunca use dado de ambiente de outro projeto.

## Card — entrada, fluxo e encerramento

1. C0: `/card <n>` → título, tipo, estado, ACs e GUID `System.TeamProject`.
2. L0: `/ambiente` e a URL local no chat.
3. B0: pergunte "SUSTENTAÇÃO ou IMPLEMENTAÇÃO?", **proponha a trilha CURTA ou COMPLETA** pelo
   critério de `fluxo-completo.md` § Trilhas (dinheiro, dado pessoal, schema, contrato/integração,
   2+ repos ou mudança grande → completa) e espere a confirmação. Se implementação, confirme
   "(Y/n) pula a análise S1–S6 e vai ao plano?". Registre: `fase.sh B0 <card> --trilha <t>`.

Sem card (pergunta conceitual, leitura de código) não há C0/L0/B0.
Sustentação: S1 → S6a. Implementação: I1 → I15, na trilha confirmada. Etapas, gates e checklist:
`fluxo-completo.md`.
Antes do I5, leia a skill `regras-de-trabalho`.

Encerramento — os três itens:

- HTML final aprovado pelo `validador-tecnico` (S6a-val, ou S4 única na curta, ou I15).
- Collection Postman com request + asserts de cada cenário HTTP executado, no workspace do Luiz
  (nunca Default nem Globals); sem cenário HTTP, a linha `PC: N/A — <motivo>` — `fluxo-completo.md` § PC.
- Destilação: `/destilar <card>` grava `docs/destilacoes/<card>.md`. Obrigatória a cada card,
  inclusive o que parou no meio: ao encerrar, ao trocar de card e antes de pedir `/clear`.
  O `hook_card.py` cobra.

Documento de card fica em `docs/` e não cita agente nem especialista da frota.

## Contexto — aba única por card

Uma aba por card. Mensagem que cita outro card: na primeira linha, alerte ("mudou do card X para
o Y — abra aba nova para o Y e destile o X antes") e espere a decisão.
Ao entrar numa etapa: `.claude/scripts/fase.sh <ETAPA> [card]`. Orçamento: 300k por sessão.
Quando o `MEDIDOR DE CONTEXTO` pedir `/compact` ou `/clear`: número medido e pedido na primeira
linha, onde a tarefa parou em 1–2 linhas, e **encerre o turno**. Você não roda esses comandos.

## Postagem no ADO

Só o contexto principal posta (subagente nunca), depois da pergunta da regra crítica 3, via
script (sobe as imagens) ou tool MCP de comentário. Se o usuário preferir o comando, entregue
caminho do HTML validado, GUID do projeto e:
`ADO_PROJECT=<GUID> python3 .claude/scripts/ado_update_comment.py <html> <work_item> [comment_id]`
Continua proibido para todos: estado e campos do work item, links, anexo avulso, PR/MR,
pipeline, wiki, test plan.

## Propagação do Brain

Mudou `.claude/` ou este arquivo: replique em todos os repos na mesma tarefa, sem pedir —
`bash .claude/scripts/propagar.sh --dry-run`, confira, e rode sem `--dry-run`. Só roda a partir do
cit. O script decide o que não viaja e faz backup. Detalhe: `.claude/rules/brain.md`.

## Índices

- `.claude/fluxo-completo.md`: fonte única do fluxo — tabela mestra de gates, proibições por etapa, checklist
- `.claude/frota/regras.md`: íntegra das regras da frota · `.claude/frota/README.md`: catálogo e roteamento
- `.claude/rules/`: regras que carregam sozinhas pelo caminho do arquivo (documento de card, SQL, testes, Brain)
- `.claude/README.md`: índice do `.claude/` · `.claude/habilidades.md`: skills de conta e plugin · `docs/INDICE.md`: acervo
