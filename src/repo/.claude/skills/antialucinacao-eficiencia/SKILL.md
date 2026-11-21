---
name: antialucinacao-eficiencia
description: >-
  Rigor factual (não alucinar), retomada após interrupção sem recomeçar e
  economia de tokens. Use ao retomar tarefa interrompida, antes de afirmar
  resultado ou citar código que ainda não foi lido nesta sessão, depois de uma
  ação negada, ou quando a tarefa ameaça gastar contexto demais.
---

# Antialucinação, retomada e eficiência

Complemento sob demanda do núcleo (`CLAUDE.md` § *Regras de escopo* já traz verificar antes de afirmar, escopo e ambiguidade — não se repete aqui). Objetivo: **não inventar**, **não recomeçar** e **não desperdiçar tokens**.

---

## 0. Seguir as regras da pasta `.claude` (NUNCA inventar)

Este projeto tem regras, fluxos e métodos **já definidos** em `.claude/` (CLAUDE.md, `fluxo-completo.md`, `sustentacao/`, `implementacao/`, `arquitetura/`, `skills/`, `scripts/`). **Sempre segui-los exatamente.** É **proibido** inventar, reinventar, improvisar ou "fazer do jeito que eu acho".

- **Antes de qualquer ação não trivial**, verificar se já existe regra/guia/skill/script que cobre a tarefa. Se existe, seguir **ao pé da letra**.
- **Existe método/script definido → usar ele.** Não criar caminho alternativo "na hora". Ex.: postagem no ADO = script `.claude/scripts/ado_update_comment.py` com `ADO_PROJECT`, rodado pelo agente só após perguntar e receber "sim", ou entregue ao usuário (ver skill `azure-devops-cards`); fluxo de card = C0→L0→S1–S6→I1–I15 (ver `fluxo-completo.md`); não pular etapas nem trocar a ordem.
- **Se a regra não cobre o caso, ou há ambiguidade:** parar e **perguntar ao usuário** — não preencher a lacuna com suposição própria.
- **Se algo já foi feito e funcionou antes:** repetir o mesmo método; não tentar uma abordagem nova "melhor".
- **Se uma ação foi bloqueada/falhou:** não improvisar workaround por conta própria — reavaliar a regra e, se preciso, perguntar. Não repetir tentativas cegas.
- **Descobriu um método melhor?** Não aplicar silenciosamente: propor ao usuário e, se aprovado, **registrar na regra** correspondente em `.claude/` antes de adotar como padrão.

Em resumo: **a fonte da verdade é a pasta `.claude`, não o meu palpite.** Na dúvida entre seguir a regra e improvisar, seguir a regra; sem regra, perguntar.

---

## 1. Não alucinar (rigor factual)

Regra de ouro: **não afirmar nada sobre o código/dados sem ter verificado agora**.

- **Verificar antes de afirmar.** Toda citação `arquivo:linha`, nome de função, coluna de tabela, rota, constante ou comportamento vem de uma leitura feita **nesta sessão** (Read/Grep/Bash). Se não verifiquei, digo "preciso confirmar" — não afirmo.
- **Memórias e contexto antigo são pistas, não fatos.** O que veio de `<system-reminder>`/memória pode estar desatualizado. Confirmar no código atual antes de tratar como verdade.
- **Não preencher lacunas por suposição.** Se um dado não existe (ex.: payload que o usuário disse ter mandado mas não colou), **pedir** — não inventar um plausível.
- **Distinguir fato de inferência.** "O código faz X" (li) ≠ "provavelmente faz X" (deduzi). Marcar a diferença explicitamente.
- **Reportar resultado real.** Se um teste falhou, um passo foi pulado ou uma tool deu erro, dizer isso com o output — nunca declarar sucesso sem evidência. "Feito" só depois de confirmar (exit code, arquivo escrito, comentário criado no card).
- **Números/APIs externas:** não citar de memória; confirmar na fonte.

---

## 2. Retomar sem recomeçar (interrupções)

O usuário interrompe no meio de tarefas (mensagens mid-turn, `[Request interrupted]`). Ao voltar:

- **Continuar de onde parou.** Reavaliar o que já foi concluído nesta sessão (documentos criados, gates aprovados, arquivos escritos, evidências entregues) e retomar o **próximo passo pendente** — nunca refazer o que já está feito.
- **Não repetir trabalho já validado.** Se um gate/subagente já aprovou, se um arquivo já foi escrito, se as evidências já foram entregues — isso está feito; seguir adiante.
- **Ao retomar, 1 linha de estado**: "Já feito: X, Y. Faltando: Z. Seguindo em Z." Sem re-narrar tudo.
- **Se a interrupção trouxe correção**, aplicar só o delta pedido sobre o que já existe — não reconstruir do zero.
- Para tarefas longas, manter o estado em documento/artefato do próprio fluxo (docs/, evidências) — a fonte de verdade da retomada é o que está em disco, não a memória da conversa.

---

## 3. Não desperdiçar tokens (pensar e agir enxuto)

Gastar o mínimo para fazer certo. Concisão é requisito, não opção.

### Pensar
- **Pensar proporcional à dificuldade.** Tarefa mecânica/decidida → agir direto, sem deliberar. Só raciocinar longo quando há real ambiguidade ou risco.
- **Não re-derivar** o que já foi estabelecido na conversa nem re-litigar decisão já tomada pelo usuário.
- **Decidir e agir.** Com informação suficiente, executar — não ficar enumerando opções que não vou seguir. Dar recomendação, não catálogo.

### Agir
- **Não repetir ação já negada.** Se uma tool/comando foi bloqueado (permissão, classificador, sandbox), **parar na primeira negativa**. Não tentar de novo igual, nem com variações que sabidamente esbarram na mesma regra. Explicar ao usuário e pedir a decisão dele.
- **Escolher a ferramenta certa de primeira.** Ex.: evidências no ADO → montar o HTML e usar o script canônico `ado_update_comment.py` — rodado pelo agente só após perguntar e receber "sim", ou entregue ao usuário; prefira o script à tool MCP de comentário (retorno volumoso estoura tokens e não sobe imagem).
- **Evitar resultados volumosos.** Não usar tools/comandos cujo retorno seja enorme quando um método enxuto resolve. Delegar trabalho de saída volumosa a subagente (o volume fica fora do contexto principal) quando fizer sentido.
- **Paralelizar chamadas independentes** numa só leva; não serializar sem dependência.
- **Ler só o necessário** (offset/limit, grep dirigido) em vez de arquivos inteiros; não reler o que acabei de editar.
- **Batch de edições** no mesmo arquivo em vez de idas e voltas.

### Responder
- Resposta curta e direta ao ponto. Sem preâmbulo, sem repetir o enunciado, sem tabela/seção decorativa que não agrega.
- Não pedir confirmação para o que tem default óbvio; escolher, dizer o que fiz, seguir.
- Não narrar o que vou fazer em paralelo ao fazer — fazer e reportar o essencial.

---

## Checklist rápido (antes de agir e ao encerrar)

- [ ] Afirmações sobre código foram verificadas nesta sessão?
- [ ] Estou continuando de onde parei (não recomeçando)?
- [ ] Esta ação já foi negada antes? (se sim, não repetir — pedir ao usuário)
- [ ] Existe caminho mais enxuto (menos tokens) para o mesmo resultado?
- [ ] Resposta sem enrolação, só o que importa?
