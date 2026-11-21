---
name: comprovar-antes-de-perguntar
description: "Tudo que for comprovável (código, dados, homol) deve ser comprovado ANTES de perguntar ao usuário"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1d174958-0e6f-4587-9207-ab6de3756d17
  modified: 2026-09-02T14:31:13.966Z
---

Antes de fazer uma pergunta ao usuário, comprove tudo o que for comprovável por conta própria — código (`arquivo:linha`), estrutura de tabela, ou consulta a dados de local/homol (o agente executa nesses ambientes). Só leve ao usuário o que **de fato** exige decisão dele (regra de negócio, escopo, prioridade) — nunca o que você mesmo poderia verificar.

**Why:** o Gustavo cobrou explicitamente (02/09/2026): eu perguntei "o que é WL ativo?" e "quer que eu prove nos dados?" quando ambos eram verificáveis por mim (schema + SELECT em homol). Perguntar o verificável desperdiça a rodada dele e empurra pro usuário trabalho que é meu.

**How to apply:** antes de cada pergunta, filtre: "isso eu consigo provar?" Se sim → prove (grep/leitura/SQL em homol/local) e traga a conclusão com evidência. Se não → então pergunte. Vale [[verificar-antes-de-deduzir]] (não afirmar por dedução) elevado a ação: não só evitar deduzir, mas ir atrás da prova antes de envolver o usuário. Dado ao vivo de homol via [[bd-homol-nao-e-o-mysql-3309]] / [[homol-updates-caminho-rapido]]; SQL passa pelo especialista-sql quando embasa decisão ([[gatilho-por-artefato-nao-por-etapa]]).
