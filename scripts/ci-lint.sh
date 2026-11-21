#!/usr/bin/env bash
# CI mínimo do Brain-Cursor — integridade estrutural (não roda frota.sh lint de modelos).
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD

echo "== hooks.json =="
python3 - <<'PY'
import json, pathlib, sys
p = pathlib.Path(".cursor/hooks.json")
data = json.loads(p.read_text())
assert data.get("version") == 1, "hooks.json: version deve ser 1"
hooks = data.get("hooks") or {}
for evt, items in hooks.items():
    for item in items:
        cmd = item.get("command", "")
        if "hook_" in cmd and ".py" in cmd:
            # extrai caminho relativo ao script python
            import re
            m = re.search(r'/([^/]+\.py)"', cmd) or re.search(r'hook_[^"]+\.py', cmd)
            if m:
                name = m.group(1) if m.lastindex else m.group(0).strip('"')
                if not name.endswith(".py"):
                    name = pathlib.Path(name).name
                path = pathlib.Path(".cursor/scripts") / pathlib.Path(name).name
                if not path.is_file():
                    print(f"ERRO: {evt} referencia {path} inexistente")
                    sys.exit(1)
print("OK hooks.json")
PY

echo "== frota TSV =="
awk -F'\t' '!/^#/ && NF && NF!=2 {print "ERRO linha grupos.tsv:", $0; bad=1} END {exit bad+0}' .cursor/frota/grupos.tsv
awk -F'\t' '!/^#/ && NF && NF!=4 {print "ERRO linha gatilhos.tsv:", $0; bad=1} END {exit bad+0}' .cursor/frota/gatilhos.tsv

echo "== agentes vs grupos.tsv =="
while IFS=$'\t' read -r _ a; do
  [ -f ".cursor/agents/$a.md" ] || { echo "ERRO: agente ausente .cursor/agents/$a.md"; exit 1; }
done < .cursor/frota/grupos.tsv

echo "== AGENTS.md =="
test -f AGENTS.md
grep -q "Staging nunca entra" AGENTS.md

echo "ci-lint: OK"