---
description: Roteia a pergunta para o especialista certo da frota
argument-hint: <tema> — <pergunta>
---

Demanda: $ARGUMENTS

1. `.claude/scripts/frota.sh buscar <tema>` para achar o agente. Nada encontrado → veja o
   roteamento por sintoma em [`.claude/frota/README.md`](../frota/README.md).
2. Acione **um** agente, passando **caminho de arquivo**, nunca conteúdo colado.
3. Repasse no chat o veredito em poucas linhas, com o caminho do que ele produziu.

Especialista não dispensa gate: se estamos numa etapa do fluxo, ele entra **dentro** dela.

Consulta **obrigatória** não passa por aqui: ela é disparada pelo artefato (`frota.sh gatilhos`) e cobrada pelo hook. Este comando é para o que o gatilho não pegou.
