---
description: I1 → I2-val — plano (curto ou completo), revisões de especialista, plano.html e o gate do I4
argument-hint: <caminho da análise ou requisitos>
---

Etapa **I1**. Base: $ARGUMENTS

Rode `.cursor/scripts/fase.sh I1` (o `fase.sh` mostra a trilha do card, declarada no B0) e conduza
a sequência da trilha sem pular etapa. Handoff sempre **por caminho de arquivo**.

## Trilha curta

1. **I1** — `arquiteto-plano` com `trilha: curta` no prompt: plano curto em
   `docs/implementacoes/plano/impl-{nome}.md`. Se ele devolver `trilha: promover para completa`,
   avise o usuário na primeira linha e siga a trilha completa.
2. **I2-val** — `validador-leve` sobre o plano curto (`cache_validacao.py rodada I2-val <card>` →
   `Rodada N de 3` no prompt; 3ª recusa escala ao usuário).
3. **I4** — apresente o plano no chat e pare: código só com **OK explícito** do usuário.

## Trilha completa

1. **I1** — `arquiteto-plano`: antes/depois marcado, decisões com alternativa e custo de reverter,
   `## Conformidade e segurança` (8 itens, nada em branco).
2. **I1-rev** — `fase.sh I1-REV`. Acione na **mesma mensagem** todo especialista cujo gatilho o
   plano bate:

| Gatilho no plano | Especialista |
|---|---|
| dinheiro, cartão, token, credencial, dado pessoal, rota pública, segredo, PCI | `especialista-seguranca` |
| 2+ sistemas, contrato entre serviços, ou altera fluxo de pagamento/ganho/integração | `revisor-arquitetura` |
| tabela, coluna, índice ou migration com dado existente | `especialista-sql` |
| efeito financeiro, webhook consumido ou job repetível | `especialista-financeiro-cobranca` |
| terceiro (Pagar.me, HubSpot, Omie) ou rota/contrato HTTP | `especialista-integracao` |
| passo irreversível ou deploy coordenado | `gestor-de-risco` |

   Retorno fixo: `Veredito: Bloqueante|Ajustar|OK` + até 3 pontos com `arquivo:linha`. Registro em
   `## Revisões de especialistas` no **`_processo-revisoes.md` interno** (nunca no plano nem no
   `plano.html` — regras.md § 11); não disparados em UMA linha. `Bloqueante` volta ao `arquiteto-plano`.
3. **I2-html** — `fase.sh I2-HTML`. `escritor-evidencias` monta
   `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html` nas 13 seções de
   `.cursor/implementacao/documento-plano-html.md` — sem PNG.
4. **I2-val** — `fase.sh I2-VAL`. **Uma** validação: `validador-tecnico` sobre plano `.md` +
   `plano.html` (o antigo I2 foi fundido aqui), com `Rodada N de 3`. Recusado volta a I2-html (ou a
   I1, se o motivo for de conteúdo).
5. **Pós-I2-val** — caminho do `plano.html` + GUID do `System.TeamProject` e a pergunta *"Posto eu o
   `plano.html` no card `<n>`, ou te entrego o comando?"*. Só com "sim"; subagente nunca posta:
   `ADO_PROJECT=<GUID> python3 .cursor/scripts/ado_update_comment.py <html_path> <work_item_id> [comment_id]`
6. **I3 → I4** — apresente o plano e **pare no gate I4**: OK explícito sobre o `plano.html` aprovado.
