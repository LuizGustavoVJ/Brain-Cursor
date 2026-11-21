#!/usr/bin/env bash
# Roda uma suíte Playwright e devolve APENAS o resumo — o stdout completo vai para um log.
#
# Uso (a partir da raiz do repositório):
#   .cursor/scripts/resumo_testes.sh e2e
#   .cursor/scripts/resumo_testes.sh local
#   .cursor/scripts/resumo_testes.sh homol
#
# Por que existe: o output cru do Playwright entra inteiro no contexto (centenas de linhas por
# execução) e é o segundo maior custo do fluxo. Aqui o log completo fica em disco e só a tabela
# de cenários + as falhas voltam para o chat. Ver .cursor/implementacao/testes-resumido.md.
#
# Saída: tabela compacta + caminho do log. Código de saída = o do npm (0 = 100% pass).

set -uo pipefail

ALVO="${1:-}"
case "$ALVO" in
  e2e|local|homol) ;;
  *) echo "uso: $0 {e2e|local|homol}" >&2; exit 2 ;;
esac

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIR_TESTES="$RAIZ/testes"
[ -d "$DIR_TESTES" ] || { echo "diretório de testes não encontrado: $DIR_TESTES" >&2; exit 2; }

DIR_LOG="$RAIZ/.cursor/cache/logs-testes"
mkdir -p "$DIR_LOG"
LOG="$DIR_LOG/${ALVO}-$(date +%Y%m%d-%H%M%S).log"

echo "▶ npm run test:$ALVO  (log completo: ${LOG#$RAIZ/})"
( cd "$DIR_TESTES" && npm run "test:$ALVO" ) > "$LOG" 2>&1
CODIGO=$?

echo
echo "── Cenários ────────────────────────────────────────────"
# Linhas de resultado do reporter list/line do Playwright
grep -E '^\s*(✓|✘|✗|×|-)\s' "$LOG" \
  | sed -E 's/\s+/ /g; s/^ //' \
  | cut -c1-140 \
  || echo "(reporter não emitiu linhas por cenário — ver log)"

echo
echo "── Resultado ───────────────────────────────────────────"
grep -E '[0-9]+ (passed|failed|skipped|flaky)' "$LOG" | tail -5 \
  || echo "(sem linha de sumário — ver log)"

if [ "$CODIGO" -ne 0 ]; then
  echo
  echo "── Falhas (primeiras 40 linhas) ────────────────────────"
  awk '/^\s*[0-9]+\) /,0' "$LOG" | head -40
fi

echo
if [ "$CODIGO" -eq 0 ]; then
  echo "✅ test:$ALVO — 100% pass. Log: ${LOG#$RAIZ/}"
else
  echo "❌ test:$ALVO — FALHOU (exit $CODIGO). Log completo: ${LOG#$RAIZ/}"
  echo "   Só abra o log inteiro se o trecho acima não bastar para diagnosticar."
fi

exit "$CODIGO"
