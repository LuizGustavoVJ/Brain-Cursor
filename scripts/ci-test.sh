#!/usr/bin/env bash
# CI mínimo — compilação e smoke dos hooks Python do Brain.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== py_compile hooks =="
for f in .cursor/scripts/hook_*.py .cursor/scripts/ancoras.py .cursor/scripts/cache_validacao.py; do
  [ -f "$f" ] || continue
  python3 -m py_compile "$f"
done

echo "== hook_card.py mostra (sem sessão) =="
export CURSOR_PROJECT_DIR="$PWD"
python3 .cursor/scripts/hook_card.py mostra </dev/null >/dev/null

echo "== frota.sh grupos (smoke) =="
bash .cursor/scripts/frota.sh grupos >/dev/null

echo "ci-test: OK"