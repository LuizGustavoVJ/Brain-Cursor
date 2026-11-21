---
name: hubspot-forms-dp-6-ajustes-barreto
description: Projeto HubSpot "Prod forms/Projeto financeiro dp" — ajustes do Wesley Barreto entregues e no ar (build #5, portal 22604900) em 16/09/2026; quem sobe é o Barreto, o agente só altera arquivo
metadata:
  type: project
---

Projeto em `~/Downloads/Hubspot Demandas Barreto/Prod forms/Projeto financeiro dp` (sem git, sem `node_modules`). Em 16/09/2026 os 6 ajustes do Wesley Barreto ficaram implementados e o usuário zipou para o Barreto testar e dar retorno.

Decisões que valem para qualquer retomada:
- **O agente só altera arquivo.** Quem roda `hs project upload` / `hs project dev` é o Barreto; não configurar perfil nem portal.
- **Owner:** `hubspot_owner_id` do Negócio → `sales_owner` do Ticket (ID puro). Nome/sobrenome/e-mail do closer só no texto da `observacao` (deal + ticket) e na nota. Negócio sem owner não bloqueia o envio.
- **CPF não passa por API** — valida só a quantidade de dígitos (a BrasilAPI quebrava e barrava envio). CNPJ mantém os 3 fallbacks (CNPJA → ReceitaWS → BrasilAPI).
- **`nome_do_pagador__pix_` grava só no ticket.**
- **O `required` do `@hubspot/ui-extensions` NÃO barra o envio** — desenha só o asterisco no rótulo, mesmo com `<Form onSubmit>` + `<Button type="submit">`. Toda obrigatoriedade é checada à mão no `handleSubmit` (lista `camposObrigatorios`), e os erros de máscara (`erroEmpregador`, `erroCep`, `erroNumero`) travam o envio junto.
- **Zero é valor válido, vazio não:** campos de dinheiro e de quantidade usam `*` manual no rótulo + `valor != null` / `.trim() !== ''` no submit.
- **`numero__endereco_` é propriedade NUMÉRICA no HubSpot** — letra faz o PATCH do Negócio voltar `INVALID_INTEGER` (caso real: "S/N"). O campo tem máscara que descarta não-dígito; endereço sem número = `0` no Número e "S/N" no Complemento (texto livre).
- **Closer sumindo das observações não é escopo de token** — a causa real foi o proprietário estar desativado na base de usuários do HubSpot. `buscarDadosDoOwner` devolve `{resumo, aviso}` e o motivo aparece na tela como `warning`, em vez de morrer no log.
- `buscaCpf.js` + `busca-cpf-hsmeta.json` ficaram órfãos de propósito — o usuário mandou deixar.
- `.cursor/settings.local.json` desse projeto tem tokens reais (CNPJA e ReceitaWS) em texto claro: nunca copiar nem exibir em entregável.
