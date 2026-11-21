#!/usr/bin/env bash
# brain_status.sh — diagnóstico do Brain: frota, conhecimento, reflexos e pendências.
set -uo pipefail
cd "${CURSOR_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 1

echo "=== FROTA (.cursor/agents) ==="
printf "%-24s %-8s %s\n" AGENTE MODELO "ETAPA COM GATE"
while IFS=$'\t' read -r g n; do
  [ "$g" = fluxo ] || continue
  f=".cursor/agents/$n.md"; [ -f "$f" ] || continue
  m=$(grep -m1 '^model:' "$f" | awk '{print $2}')
  d=$(grep -m1 '^description:' "$f" | cut -c14- | cut -d. -f1 | cut -c1-52)
  printf "%-24s %-8s %s\n" "$n" "${m:-herda}" "$d"
done < .cursor/frota/grupos.tsv
echo
echo "  especialistas sob demanda (catálogo: frota.sh listar):"
for g in $(awk -F'\t' '$1!="fluxo" && !v[$1]++ {print $1}' .cursor/frota/grupos.tsv); do
  q=$(awk -F'\t' -v g="$g" '$1==g' .cursor/frota/grupos.tsv | wc -l)
  printf "  %-14s %2s  %s\n" "$g" "$q" \
    "$(awk -F'\t' -v g="$g" '$1==g {printf "%s ", $2}' .cursor/frota/grupos.tsv | cut -c1-56)"
done
GAT=$(bash .cursor/scripts/frota.sh gatilhos 2>/dev/null | tail -1)
echo "  gatilho por artefato: $GAT  (detalhe: frota.sh gatilhos)"
LINT=$(bash .cursor/scripts/frota.sh lint 2>/dev/null | tail -1)
echo "  ---- $LINT"

echo "=== CONHECIMENTO ==="
for s in .cursor/skills/dominio-*/SKILL.md; do
  [ -e "$s" ] || { echo "(nenhum mapa de domínio)"; break; }
  d=$(dirname "$s"); n=$(basename "$d")
  P='\]\([^)]+#L[0-9]+(-L[0-9]+)?\)'
  a=$(grep -oE "$P" "$s" 2>/dev/null | wc -l)
  u=$(grep -oE "$P" "$s" 2>/dev/null | sort -u | wc -l)
  t=$(grep -c '' ".cursor/cache/ancoras/$n.tsv" 2>/dev/null || echo 0)
  rep=""; [ "$a" -ne "$u" ] && rep=" · $((a - u)) citação repetida"
  printf "  %-28s %4s linhas  %3s âncoras · %s travadas%s\n" \
    "$n" "$(grep -c '' "$s")" "$u" "$t" "$rep"
done
printf "  %-28s %4s docs\n" "acervo docs/" "$(find docs -name '*.md' 2>/dev/null | wc -l)"
MEM="$HOME/.cursor/projects/$(pwd | tr '/' '-')/memory"
printf "  %-28s %4s fatos\n" "memória do projeto" "$(ls "$MEM"/*.md 2>/dev/null | grep -cv MEMORY.md || echo 0)"

echo
echo "=== REFLEXOS (hooks) ==="
python3 - <<'PY'
import json, pathlib, re
d = json.loads(pathlib.Path(".cursor/settings.json").read_text())
for evt, arr in d.get("hooks", {}).items():
    for item in arr:
        for hk in item.get("hooks", []):
            alvo = item.get("matcher", "*")
            # so conta invocacao real de script: nome citado dentro do texto do lembrete
            # (ex.: "frota.sh gatilhos") nao e hook, e aparecia como se fosse
            m = re.search(r"scripts/([\w.-]+\.(?:py|sh))", hk.get("command", ""))
            script = m.group(1) if m else "(inline)"
            print(f"  {evt:<17} [{alvo:<11}] {script}")
PY

echo
echo "=== PENDÊNCIAS ==="
SUJOS=$(cat .cursor/cache/dominios-sujos 2>/dev/null | tr '\n' ' ')
[ -n "$SUJOS" ] && echo "  mapas sujos: $SUJOS  → rode: kb.sh verificar" || echo "  nenhum mapa sujo"
ABERTOS=$(python3 -c "import json,pathlib;ag=set();[ag.update(json.loads(f.read_text()).get('pendentes',{})) for f in pathlib.Path('.cursor/cache/gatilhos').glob('*.json')];print(' '.join(sorted(ag)))" 2>/dev/null)
[ -n "$ABERTOS" ] && echo "  gatilho aberto (especialista nao consultado): $ABERTOS" \
                 || echo "  nenhum gatilho de especialista em aberto"
SAIDA=$(python3 .cursor/scripts/ancoras.py verificar --dry-run 2>/dev/null)
echo "$SAIDA" | grep -E 'S/TRAVA|ORFA' | sed 's/^/  /'
echo "$SAIDA" | grep -E 'ancoras ·' | sed 's/^/  /'
