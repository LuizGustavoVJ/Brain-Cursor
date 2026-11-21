#!/usr/bin/env bash
# Inventário e saúde dos MCPs do Brain.
#
# Por que existe: MCP declarado e MCP *funcionando* são coisas diferentes. Um servidor
# quebrado é pior que um ausente — ele injeta o nome das tools na sessão, o agente confia
# que existe e só descobre o contrário no meio da etapa. Este script confere as duas coisas
# de fora, sem gastar contexto chamando tool.
#
# Uso: .claude/scripts/mcp.sh [listar|checar|agentes]   (sem argumento = checar tudo)
#
# Escopos que o Claude Code lê, na ordem em que o projeto vence:
#   projeto  → ./.mcp.json               (gitignored; vale só neste repo)
#   usuário  → ~/.claude.json mcpServers (vale em todos os repos)
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1

listar() {
python3 - <<'PY'
import json, os
OK, ERR, AV = "✓", "✗", "!"
proj = json.load(open(".mcp.json")).get("mcpServers", {}) if os.path.isfile(".mcp.json") else {}
g = os.path.expanduser("~/.claude.json")
glob = json.load(open(g)).get("mcpServers", {}) if os.path.isfile(g) else {}

print("=== MCPs declarados ===")
for escopo, servidores in (("projeto", proj), ("usuário", glob)):
    for nome, cfg in sorted(servidores.items()):
        alvo = os.path.basename(cfg.get("command") or cfg.get("url") or "?")
        args = " ".join(cfg.get("args") or [])[:42]
        envs = ",".join((cfg.get("env") or {}).keys()) or "-"
        print(f"  {nome:16s} {escopo:8s} {alvo:12s} {args:42s} env={envs}")

dup = sorted(set(proj) & set(glob))
if dup:
    print(f"\n  {AV} declarado nos DOIS escopos: {', '.join(dup)}")
    print("    o de projeto vence; o de usuário fica morto e só confunde auditoria.")
print(f"\n  total: {len(set(proj) | set(glob))} servidores")
PY
}

checar() {
python3 - <<'PY'
import json, os
OK, ERR, AV = "✓", "✗", "!"
proj = json.load(open(".mcp.json")).get("mcpServers", {}) if os.path.isfile(".mcp.json") else {}
g = os.path.expanduser("~/.claude.json")
glob = json.load(open(g)).get("mcpServers", {}) if os.path.isfile(g) else {}

print("=== Saúde dos MCPs ===")
if not proj:
    print(f"  {AV} sem .mcp.json neste repo — só os MCPs de escopo de usuário estão de pé")

ado = proj.get("azure-devops") or glob.get("azure-devops")
if ado:
    env = ado.get("env") or {}
    vazio = [k for k, v in env.items() if not v or "SEU_PAT" in str(v)]
    if vazio:
        print(f"  {ERR} azure-devops: credencial ausente em {vazio} — C0 (ler card) vai falhar")
    else:
        print(f"  {OK} azure-devops: PAT presente — leitura de card em C0")
else:
    print(f"  {ERR} azure-devops: não declarado — C0 não lê card por MCP")

if proj.get("playwright") or glob.get("playwright"):
    print(f"  {OK} playwright: declarado — captura de evidência em I7/I10/I13/I14 (proibido fora disso)")
else:
    print(f"  {AV} playwright: não declarado — I9/I11/I14 perdem o print automático")

gl = glob.get("gitlab") or proj.get("gitlab")
if not gl:
    print(f"  {AV} gitlab: não declarado — especialista-git e revisor-codigo perdem pipeline e MR reais")
else:
    env = gl.get("env") or {}
    tok = bool(env.get("GITLAB_PERSONAL_ACCESS_TOKEN"))
    ro = str(env.get("GITLAB_READ_ONLY_MODE", "")).lower() == "true"
    marca = OK if tok else ERR
    print(f"  {marca} gitlab: token {'presente' if tok else 'AUSENTE'} · "
          f"url={env.get('GITLAB_API_URL', '?')} · somente-leitura={ro}")
    if not ro:
        print(f"    {AV} sem GITLAB_READ_ONLY_MODE=true o agente consegue ESCREVER no GitLab")

# Zendesk: descontinuado em 21/08/2026 por decisão do usuário — não é para subir.
# Se voltar a aparecer declarado em algum escopo, é config esquecida, não recurso novo.
for esc, d in (("projeto", proj), ("usuário", glob)):
    if "zendesk" in d:
        print(f"  {AV} zendesk declarado no escopo de {esc} — DESCONTINUADO, remover a declaração")
PY
  local n
  n=$(ls -1 /var/www/html/*/.mcp.json 2>/dev/null | wc -l)
  if [ "$n" -gt 1 ]; then
    echo
    echo "  ! o mesmo PAT do ADO está copiado em $n arquivos .mcp.json (um por repositório)."
    echo "    Rotação de PAT = editar $n arquivos; esquecer um quebra o C0 só naquele repo."
    echo "    Consolidar em ~/.claude.json resolve, mas apaga declaração em outros repos:"
    echo "    proponha e PEÇA PERMISSÃO antes (CLAUDE.md § Regras de escopo)."
  fi
}

agentes() {
  echo "=== Quem da frota alcança cada MCP ==="
  for srv in azure-devops playwright gitlab; do
    printf "  %-14s " "$srv"
    achados=$(grep -l "mcp__${srv}__" .claude/agents/*.md 2>/dev/null \
              | xargs -r -n1 basename | sed 's/\.md$//' | tr '\n' ' ')
    if [ -z "$achados" ]; then
      echo "! nenhum agente declara tool — só o contexto principal alcança"
    else
      echo "$achados"
    fi
  done
  echo
  echo "  Tool não declarada no frontmatter NÃO chega ao subagente, mesmo com o servidor de pé."
  echo "  Permissões (allow/deny) das tools MCP vivem em .claude/settings.json."
}

case "${1:-checar}" in
  listar)  listar ;;
  checar)  listar; echo; checar; echo; agentes ;;
  agentes) agentes ;;
  *) echo "uso: mcp.sh [listar|checar|agentes]"; exit 1 ;;
esac
