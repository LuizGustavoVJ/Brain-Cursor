---
name: entrega-de-artefatos
description: "Onde e como entregar arquivo/comando/texto ao usuário: sempre em docs/ do projeto (nunca /tmp), nomeado por {card-id}={número}-{Descrição-Kebab} idêntico nas 4 localizações, entregue como link markdown clicável; comando pronto para colar com segredo inline; texto de área sem link (caminho local no chat + 'segue abaixo')"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:04:23.455Z
---

Consolida `arquivos-sempre-em-docs-do-projeto`, `nomenclatura-docs-card-id`,
`entregar-arquivo-como-link-ide` e `entrega-comando-e-textos-prontos` (destilação de 25/09/2026).
Layout do `evidencias.html` tem arquivo próprio (`padrao-html-evidencias`, carga alta de detalhe,
não fundido aqui).

**Onde criar:** sempre dentro do repositório, em `docs/<área>/<tema>/` — nunca em `/tmp` nem no
scratchpad da sessão (scratchpad é só para intermediário: script gerador, dump bruto).

**Nomenclatura de card:** `{card-id} = {número}-{Descrição-Kebab}` derivado do título do card
(ex.: 156057 "Cliente sem Base" → `156057-Cliente-sem-Base`) — **nunca só o número**.
Idêntico, mesmo casing, nas 4 localizações: `docs/fluxos/{tipo}/{card-id}.md`,
`docs/analises/{tipo}/{card-id}.md`, `docs/evidencias/html/{tipo}/{card-id}/evidencias.html` e
`docs/evidencias/assets/{tipo}/{card-id}/`.

**Como entregar no chat:** link markdown clicável com caminho **relativo à raiz do workspace** —
`[texto](caminho/relativo)`, nunca caminho absoluto em texto puro (a IDE renderiza o relativo como
clicável; o absoluto não).

**Comando pronto:** entregar já pronto para colar e rodar, com chave/segredo/parâmetro **inline**
num `cd ... && ...` único — nunca a versão que abre prompt interativo ou depende de flag decorada.
Se a ferramenta exige flag para não quebrar/duplicar, consertar a ferramenta (idempotente) em vez
de repassar a pegadinha. **Se eu tenho acesso para executar** (credencial à mão, ação local/homol/
API do próprio usuário), executo direto — só entrego comando quando a execução depende de algo que
só o usuário tem/faz.

**Texto para área externa (SENSE, Dados, Identidade...):** pronto para colar no e-mail/chat da
área, um por área, autossuficiente. Aqui a regra é o oposto do link: **sem** link do arquivo (vive
na máquina do usuário, não em lugar compartilhado) — escrever "segue abaixo/segue em anexo" no
corpo (ele anexa via Google Drive) e dar, **separado no chat**, o caminho local do arquivo.
