# Gatilho de especialista — por artefato, não por etapa

> **A tabela não está aqui.** Ela é dado: [`gatilhos.tsv`](gatilhos.tsv), renderizada por
> `.claude/scripts/frota.sh gatilhos [tema]`. Este arquivo explica o mecanismo, o registro e os
> limites. Tabela copiada em prosa desatualiza na primeira mudança e passa a mentir.

## A regra

**Produziu ou alterou o artefato → o especialista da classe entra ANTES de o artefato sair.**

"Sair" é o momento em que o artefato deixa de ser rascunho: entregar ao usuário, executar,
comitar, colar no documento da etapa, ou fechar a etapa. Não é o fim do card — é o fim do
rascunho.

Isso vale **em qualquer etapa** do fluxo (C0 a I15) **e fora dele**: pedido avulso, pergunta no
chat, manutenção, exploração. Não existe janela em que o gatilho descansa.

**Caso duro, que originou a regra:** toda consulta SQL que vá ser executada ou entregue ao usuário
passa pelo [`especialista-sql`](../agents/especialista-sql.md) **antes** de sair. Em 24/08/2026
duas consultas foram entregues para rodar em produção e voltaram com erro 1064 — o especialista só
foi chamado *depois*. O gatilho existia, mas estava preso à etapa S3 e ainda por cima na lista
discricionária. Essa lista não existe mais.

## Por que por artefato, e não por etapa

Gatilho por etapa depende de duas coisas darem certo ao mesmo tempo: estar na janela e lembrar.
Gatilho por artefato depende de uma condição que já está na tela — o arquivo que acabou de ser
escrito, o comando que acabou de rodar. É verificável, então dá para automatizar; e o que dá para
automatizar não se esquece.

## Como cada gatilho é cobrado

| Coluna `COMO` | O que significa |
|---|---|
| `hook` | [`hook_gatilhos.py`](../scripts/hook_gatilhos.py) casa caminho, conteúdo escrito ou comando Bash e injeta a cobrança na hora — **34 dos 49** |
| `decl` | condição objetiva que máquina nenhuma vê (tamanho de diff, ambiguidade de card, decisão entre alternativas) — quem declara é o agente — **15 dos 49** |

`decl` **não** é "opcional": é gatilho cuja verificação é do agente. A diferença é quem detecta,
não se obriga.

O hook lê o TSV a cada disparo, então **acrescentar gatilho é editar uma linha** — não há código
para mudar. Grafia dos tokens de detecção: cabeçalho do próprio [`gatilhos.tsv`](gatilhos.tsv).

## O que o hook faz (e o que ele deliberadamente não faz)

- Fala **uma vez por especialista, por sessão**, no máximo **3 por mensagem**. Reflexo que repete vira custo, e custo vira ruído ignorado.
- Fica **em silêncio** se aquele especialista já foi chamado na sessão (ele observa as chamadas
  `Agent` e quita a pendência sozinho).
- Cobra de novo no `Stop` o que ficou aberto — por `decision:block`, uma vez (o `additionalContext` no Stop não chega ao modelo).
- **Só artefato dispara, nunca palavra solta:** `texto:` vale para arquivo de código; documento (`docs/`, `.md`, `.html`) só pelo `doc:` (SQL no início de linha/bloco ```sql, DDL); `cmd:` casa o **início** de cada comando, sem heredoc — `grep "5-6 dig"` não é `dig`.
- **Não bloqueia** ferramenta. O reflexo cobra; quem decide é o agente, que responde por escrito.
- Ignora conteúdo de arquivos do próprio Brain (`.claude/`, `CLAUDE.md`) — engenharia de harness
  não é artefato de produto. O caminho ainda dispara os gatilhos de `ia` (agente, prompt, skill).

## Registro — barato, porque é linha, não relatório

Um gatilho disparado vira **uma linha**. Ela vive num arquivo **interno de processo**,
`_processo-revisoes.md`, na pasta do card — **nunca** no documento oficial. Documento de card
(análise `.md`, `plano.html`, `evidencias.html`) não cita agente da frota ([`regras.md`](regras.md)
§ 11); no documento oficial cabe, no máximo, um comentário HTML apontando para o `_processo-revisoes.md`.

| Contexto | Onde a linha vai |
|---|---|
| S3-rev · I1-rev · I6-rev · qualquer etapa | `## Revisões de especialistas` no `_processo-revisoes.md` da pasta do card |
| Fora de card | **uma linha no chat**, ao fim da resposta |

Formato da linha (tabela `Especialista · Veredito · Ponto · Onde foi acatado`, ou texto corrido):

```
`<agente>` · OK | Ajustar | Bloqueante · <ponto em até 12 palavras> · <onde foi acatado>
```

Gatilhos que **não** dispararam entram em **uma linha só**, ao fim da mesma seção:

```
Gatilhos avaliados e não disparados: <classe> (motivo curto) · <classe> (motivo curto)
```

Nada de tabela por especialista, nada de colar o retorno dele. O retorno do especialista já é de
15 linhas ([`regras.md`](regras.md) § 8); no documento sobra **uma**.

## Formato fixo do retorno do especialista

Especialista que fugir do formato é rechamado:

```
Veredito: Bloqueante | Ajustar | OK
- até 3 pontos, cada um com `arquivo:linha`
- o que muda no artefato
```

## Limites — o que o gatilho não autoriza

1. **Especialista é insumo da etapa, nunca substituto.** Nenhum gate cai porque um especialista
   opinou. Quem aprova I2-val (completa), I6, I11 e I15 continua sendo o `validador-tecnico`.
2. **Um assunto, um agente.** Dois especialistas na mesma mensagem só quando são **assuntos
   diferentes** sobre o mesmo artefato (segurança e frontend no mesmo diff, por exemplo). Três
   agentes para a *mesma* pergunta continua proibido ([`README.md`](README.md) § *Regras de uso*).
3. **Fan-out na mesma mensagem.** Todos os gatilhos abertos vão em paralelo, num único turno —
   nunca em série.
4. **Handoff por caminho.** Passe o caminho do arquivo, jamais o conteúdo colado.
5. **Quem chama é o contexto principal.** Agente de etapa não tem a ferramenta `Agent`; ao bater
   um gatilho ele declara no retorno `gatilho pendente: <classe>` e o orquestrador chama.
6. **Gatilho não cria trabalho novo.** O especialista revisa o artefato que já existe; ele não
   expande escopo (CLAUDE.md § *Regras de escopo*).

## Manutenção

```bash
.claude/scripts/frota.sh gatilhos          # tabela inteira
.claude/scripts/frota.sh gatilhos dinheiro # quem entra neste tema
.claude/scripts/frota.sh lint              # especialista sem gatilho = ERRO
```

O `lint` trata **especialista sem gatilho como erro**: ou falta a condição, ou o agente não se
justifica. Agente novo sem linha em `gatilhos.tsv` não passa.
