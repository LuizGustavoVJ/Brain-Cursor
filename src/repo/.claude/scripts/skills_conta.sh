#!/usr/bin/env bash
# skills_conta.sh — resolve as habilidades que a conta claude.ai sincroniza para esta máquina.
#
# Três camadas, três destinos diferentes no disco:
#   1. skills da conta   ~/.claude/skills/synced/<bucket>/<nome>/SKILL.md      (invocáveis: Skill)
#   2. skills embutidas  vêm com o CLI, materializadas só ao invocar           (invocáveis: Skill)
#   3. plugins           ~/.claude/plugins/synced/<bucket>/<plugin>/skills/…   (NÃO invocáveis
#      enquanto o plugin estiver "available"; aqui servem como texto de referência para ler)
#
# Por que existe: o caminho real tem um UUID de bucket que MUDA quando o usuário adiciona,
# remove ou re-sincroniza na web. Âncora com UUID cravado quebra sozinha e o agente passa a
# ler um caminho morto. Aqui o nome é a chave; o UUID é detalhe de implementação.
#
# Tudo isso é ESCOPO DE USUÁRIO: vale em todos os repositórios sem propagação. O Brain
# (.claude/) propaga; isto não — quem instala é a conta, em claude.ai.
#
# Uso:
#   skills_conta.sh listar                 # as três camadas
#   skills_conta.sh caminho <nome>         # diretório da skill da conta
#   skills_conta.sh ler <nome>             # imprime o SKILL.md da skill da conta
#   skills_conta.sh tem <nome>             # 0 se existe, 1 se não — para usar em if
#   skills_conta.sh plugins                # plugins sincronizados e se estão habilitados
#   skills_conta.sh plugin <plug>/<skill>  # caminho do SKILL.md dentro de um plugin
#   skills_conta.sh ler-plugin <p>/<s>     # imprime esse SKILL.md
set -uo pipefail

RAIZ="${HOME}/.claude/skills/synced"
RAIZ_PLUG="${HOME}/.claude/plugins/synced"

# as embutidas não têm arquivo antes da primeira invocação; a lista é do catálogo do CLI
EMBUTIDAS="code-review security-review simplify dataviz claude-api update-config \
fewer-permission-prompts run loop schedule workflow-authoring artifact-design \
artifact-diagramming artifact-capabilities keybindings-help init"

_bucket() {
  # o bucket mais recente vence: re-sync cria pasta nova e a antiga pode ficar para trás
  find "${1:-$RAIZ}" -mindepth 1 -maxdepth 1 -type d -name '*_*' -printf '%T@ %p\n' 2>/dev/null \
    | sort -rn | head -1 | cut -d' ' -f2-
}

_dir() {
  local b; b="$(_bucket "$RAIZ")"
  [ -n "$b" ] || return 1
  [ -d "$b/$1" ] || return 1
  printf '%s\n' "$b/$1"
}

_plugin_skill() {          # <plugin>/<skill> -> caminho do SKILL.md
  local b p s
  b="$(_bucket "$RAIZ_PLUG")" || return 1
  [ -n "$b" ] || return 1
  p="${1%%/*}"; s="${1#*/}"
  # ~g2 é a geração nova do mesmo plugin; a sem sufixo é a que o catálogo usa
  for cand in "$b/$p/skills/$s/SKILL.md" "$b/$p/skills/"*"/$s/SKILL.md"; do
    [ -f "$cand" ] && { printf '%s\n' "$cand"; return 0; }
  done
  return 1
}

case "${1:-listar}" in
  listar)
    b="$(_bucket "$RAIZ")"
    echo "1. SKILLS DA CONTA — invocáveis com Skill(...), valem em todo repo, NÃO propagam"
    echo "   encaixe no fluxo: .claude/habilidades.md"
    if [ -z "$b" ]; then
      echo "   (nenhuma sincronizada em $RAIZ)"
    else
      for d in "$b"/*/; do
        [ -f "$d/SKILL.md" ] || continue
        nome="$(basename "$d")"
        desc="$(sed -n 's/^description: *//p' "$d/SKILL.md" | head -1 | cut -c1-72)"
        printf '   %-16s %s\n' "$nome" "$desc"
      done
    fi
    echo
    echo "2. SKILLS EMBUTIDAS NO CLI — invocáveis com Skill(...), sem arquivo até a 1ª invocação"
    printf '   '; echo $EMBUTIDAS | tr ' ' '\n' | paste -sd' ' - | fold -s -w 88 | sed '2,$s/^/   /'
    echo
    echo "3. PLUGINS SINCRONIZADOS — texto de referência; NÃO invocáveis enquanto 'available'"
    "$0" plugins
    ;;
  plugins)
    b="$(_bucket "$RAIZ_PLUG")"
    if [ -z "$b" ] || [ ! -f "$b/manifest.json" ]; then
      echo "   (nenhum plugin sincronizado em $RAIZ_PLUG)"; exit 0
    fi
    python3 - "$b" <<'PY'
import json, sys, os, glob
b = sys.argv[1]
m = json.load(open(os.path.join(b, 'manifest.json')))
for p in sorted(m.get('plugins', []), key=lambda x: x['name']):
    n = p['name']
    qtd = len(glob.glob(os.path.join(b, n, 'skills', '**', 'SKILL.md'), recursive=True))
    print(f"   {n:26} {p.get('installationPreference','?'):10} {qtd:3} skills")
PY
    ;;
  caminho)
    _dir "${2:?uso: skills_conta.sh caminho <nome>}" || {
      echo "skill '${2}' não está sincronizada nesta máquina" >&2; exit 1; }
    ;;
  ler)
    d="$(_dir "${2:?uso: skills_conta.sh ler <nome>}")" || {
      echo "skill '${2}' não está sincronizada nesta máquina" >&2; exit 1; }
    cat "$d/SKILL.md"
    ;;
  tem)
    _dir "${2:?uso: skills_conta.sh tem <nome>}" >/dev/null 2>&1
    ;;
  plugin)
    _plugin_skill "${2:?uso: skills_conta.sh plugin <plugin>/<skill>}" || {
      echo "skill de plugin '${2}' não encontrada — veja: skills_conta.sh plugins" >&2; exit 1; }
    ;;
  ler-plugin)
    f="$(_plugin_skill "${2:?uso: skills_conta.sh ler-plugin <plugin>/<skill>}")" || {
      echo "skill de plugin '${2}' não encontrada — veja: skills_conta.sh plugins" >&2; exit 1; }
    cat "$f"
    ;;
  *)
    sed -n '2,30p' "$0"
    exit 1
    ;;
esac
