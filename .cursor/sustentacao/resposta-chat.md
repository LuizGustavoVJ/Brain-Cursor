# Resposta no chat

## L0 — Ambiente local (antes de B0)

1. Subir app + BD conforme o perfil `arquitetura/ambiente-local-{projeto}.md` (§ Gate L0).
2. Confirmar MySQL (`127.0.0.1:3309`) e HTTP (`curl`).
3. **Informar no chat a URL de acesso local** (obrigatório).
4. Só então iniciar **B0**.

## B0 — Bifurcação (antes de S1)

1. Perguntar no chat: **“Qual é o tipo de tarefa: SUSTENTAÇÃO ou IMPLEMENTAÇÃO?”**
2. **Aguardar a resposta explícita** — não presumir o tipo de tarefa.
3. Se **“implementação”**: perguntar **“Confirma que pula S1–S6 e vai direto para I1–I15? (Y/n)”** e aguardar o sim.
4. Sinalizar no chat o fluxo escolhido e iniciar **S1** (ou **I1**) na **mesma aba** — aba única por card.

## Transições (o que sinalizar) — aba única por card

| Momento | Mensagem no chat |
|---------|------------------|
| Fim do bloco C0+L0 | Fluxo escolhido em B0 e início de **S1**/**I1** — **mesma aba** |
| Medidor de contexto pedindo `/compact` | Repetir o pedido na **primeira linha** e **parar** — pedido de `/compact` encerra o turno |
| Medidor em ≥ 200% | Resumo de 3–5 linhas + pedido de `/clear` **no corte de exceção do bloco** — e parar |
| **S6b** (handoff S→I) | *“Análise completa → implementação necessária (S6b)”* + início de **I1** na mesma aba |
| **S6a** (encerramento) | Após Pós-S6a entregue, o card está fechado |

Após cada documento (fluxo, análise ou implementação):

1. Resumir o conteúdo
2. Indicar o **caminho do arquivo** para revisão (na análise: `.md`, `.html` e pasta de anexos/imagens)
3. Informar o **resultado da validação** do subagente (aprovado ou motivos de recusa)
4. Na análise aprovada, informar a **decisão de implementação** (necessária ou análise suficiente)
5. Se **implementação necessária**, informar handoff para [`.cursor/implementacao/resposta-chat.md`](../implementacao/resposta-chat.md)
