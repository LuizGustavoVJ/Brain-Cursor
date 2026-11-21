---
description: I5 — implementa o plano aprovado (exige gate I4)
argument-hint: <caminho do plano>
---

Etapa **I5**. Plano: $ARGUMENTS

**Antes de acionar:** confirme que o gate **I4** foi dado — OK explícito do usuário nesta
conversa. Sem isso, não acione o subagente.

Acione `desenvolvedor` informando que o I4 está dado e o caminho do plano.
Lembre-o de conferir no perfil se o código precisa ser copiado para o container antes de testar.

**Trilha curta:** não há I6 separado — siga para `/testar local` (I10); o código é conferido
contra o plano junto com o HTML no I11.

**Trilha completa:** valide com `validador-tecnico` (I6, `Rodada N de 3`): código **vs** plano.

## I6-rev — revisões de especialista sobre o diff (completa)

`fase.sh I6-REV`. Gatilhos contra o **diff**, na mesma mensagem:

| Gatilho no diff | Especialista |
|---|---|
| **houve revisão de segurança em I1-rev** → **obrigatório** | `especialista-seguranca` (o diff cumpre o que o plano decidiu?) |
| tocou view, JS ou CSS, ou arquivo legado > 500 linhas | `especialista-php-legado` |
| diff > 200 linhas ou 5+ arquivos | `revisor-codigo` |
| implementa elegibilidade, cálculo, prazo ou exceção de negócio | `revisor-regra-negocio` |

Retorno fixo `Veredito: Bloqueante|Ajustar|OK` + até 3 pontos com `arquivo:linha`. Registro em
`## Revisões de especialistas (código)` no **`_processo-revisoes.md` interno**; não disparados em
UMA linha. O checklist de conformidade do plano é reconferido contra o diff. `Bloqueante` volta ao
`desenvolvedor` antes de fechar o I6. Na trilha curta, gatilho que disparar no diff segue a mesma
regra de registro — e se for de classe da completa, o card é promovido.
