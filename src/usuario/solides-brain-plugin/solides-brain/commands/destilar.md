---
description: Aprendizado — verifica âncoras e registra o que o card ensinou (obrigatório a cada card)
argument-hint: <card> [caminhos dos artefatos do card]
---

Destilação do card. Argumentos: $ARGUMENTS (primeiro = número do card).

**Quando (obrigatório nas duas trilhas, também em card que parou no meio):** no encerramento da
sustentação, após I11 e após I15 (implementação), **ao trocar de card** e **antes de pedir `/clear`**. O `hook_card.py`
cobra nesses pontos enquanto o marcador não existir.

1. Rode `.claude/scripts/kb.sh verificar` — corrige as âncoras que o código moveu.
2. Acione o subagente `destilador-dominio` com o número do card e os caminhos dos artefatos.
3. Confira que ele gravou o marcador **`docs/destilacoes/<card>.md`** (o que entrou em cada mapa
   `dominio-*`/memória, ou `nada novo: <motivo>`). Sem o marcador, o card não está destilado.
4. Ao terminar, rode `.claude/scripts/kb.sh limpar-sujos`.

Isto não é opcional: é o passo que impede o próximo card de redescobrir o que este já provou.
