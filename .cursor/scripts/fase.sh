#!/usr/bin/env bash
# Declara a etapa (e o card) DESTA sessão. O medidor de contexto (hook_contexto.py) usa isso para
# rotular o orçamento — sem declaração, ele assume o padrão (300k) e diz que a fase não foi declarada.
#
#   .cursor/scripts/fase.sh B0 167697 --trilha curta   # B0: trilha confirmada pelo usuário
#   .cursor/scripts/fase.sh I7 167697   # entrando na etapa I7 do card 167697
#   .cursor/scripts/fase.sh I2-VAL      # mesma sessão, mesmo card
#   .cursor/scripts/fase.sh             # mostra card, etapa e orçamento da sessão
#   .cursor/scripts/fase.sh --limpar
#
# Estado por SESSÃO (CLAUDE_CODE_SESSION_ID), nunca por repo: duas abas não se contaminam.
# Card diferente do ativo na sessão → imprime o alerta de aba única por card (regra obrigatória).
# Etapa de encerramento (S6A-VAL, S6A-PC, S6B, I11, I13-PC, I14, I15) sem docs/destilacoes/<card>.md
# → imprime a cobrança de destilação.
# Mapeamento etapa → bloco/corte: fonte única em hook_card.py (BLOCOS).
# Política: .cursor/otimizacao-custos.md § 4.
set -euo pipefail

SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/hook_card.py"

case "${1:-}" in
  --limpar) exec python3 "$SCRIPT" limpa ;;
  "")       exec python3 "$SCRIPT" mostra ;;
  *)        exec python3 "$SCRIPT" fase "$@" ;;
esac
