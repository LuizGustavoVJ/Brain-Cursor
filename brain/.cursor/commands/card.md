---
description: C0 — busca o card no ADO e resume número, título, ACs e GUID do projeto
argument-hint: <numero-do-card>
---

Etapa **C0** para o card `$ARGUMENTS`.

Acione o subagente `leitor-card` passando o número do card. Ele devolve número, título, tipo,
estado, ACs, o GUID de `System.TeamProject` e as ambiguidades.

Repasse o resumo no chat e **guarde o GUID** — ele é necessário no fim, para montar o comando
de postagem das evidências.

Depois de C0, o próximo passo é **L0** (`/ambiente`). Não inicie S1 nem I1 antes.
