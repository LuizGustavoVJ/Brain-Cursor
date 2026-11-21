---
name: fonte-unica-nunca-duplicar-tabela
description: Tabela ou número repetido em dois arquivos do Brain vira contradição; centralizar em fonte única e apontar
metadata:
  type: feedback
---

O usuário revisou o Brain e apontou duplicação: "veja se está realmente duplicado, e se estiver
centralize em uma única fonte de verdade".

**Why:** a duplicação não é só desperdício — ela **mente**. O orçamento de contexto ficou com duas
versões (150k no `hook_contexto.py`/`fase.sh` e 30–80k em 4 documentos, um deles a skill carregada
`solides-sustentacao`), e a contagem de especialistas exigiu edição manual em 4 arquivos ao mudar
de 45 para 49. Quem lê o arquivo errado obedece a regra revogada.

**How to apply:** antes de escrever tabela/contagem/orçamento em `.cursor/`, pergunte de onde o
dado sai do disco — `frota.sh listar|grupos|modelos` (de `agents/*.md` + `grupos.tsv`),
`hook_contexto.py`/`fase.sh` (orçamento), `fluxo-completo.md` (fluxo), `frota/regras.md` (regras).
No segundo arquivo escreva **ponteiro**, nunca cópia. Artefato gerado (plugin) mora fora de
`.cursor/`. Ver [[brain-frota-delegar-por-etapa]] e [[modelo-por-custo-de-errar]].

**Complemento (21/08/2026) — mudou o Brain, revise quem o descreve.** O usuário cobrou:
"terá que revisar os documentos criados dentro da pasta cursor para refletir as alterações atuais",
citando `arquitetura/brain.md` § *A frota* ainda escrito "Treze agentes" depois de a frota ir a 62.
Descrição desatualizada é o mesmo defeito da duplicação: quem lê obedece o que já não vale. Achados
do mesmo tipo na varredura: `automacoes.md` com o orçamento revogado (30k/50k/75k) e sem o
`hook_dominio.py`; `estrutura-cursor.md` com árvore que enumerava arquivos e ignorava
`agents/`, `commands/`, `frota/`, `scripts/`; `skills/README.md` sem 2 das 16 skills; e o próprio
`hook_pos_testes.py` repetindo "~50k". **Ao encerrar mudança estrutural no Brain, varra
`.cursor/**/*.md` + os hooks pelos números e contagens que a mudança invalidou.**
