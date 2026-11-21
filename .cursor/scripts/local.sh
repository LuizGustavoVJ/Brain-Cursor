#!/usr/bin/env bash
# Ambiente local do cit — patches que NUNCA vão para origin.
# Os patches moram FORA do repo (~/patches-locais-cit) porque não podem ser commitados
# nem por acidente. Origem: 2 commits "Ajuste local" (a3a8704b9, d75b323c1) extraídos
# em 31/07/2026 — ver o README da pasta de patches.
#
# Uso: local.sh {status|apply|restore-repo|help}
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PATCH_DIR="${PATCHES_LOCAIS_CIT:-$HOME/patches-locais-cit}"
PATCH="$PATCH_DIR/ajustes-locais-cit.patch"

# Arquivos que o patch toca — derivados do próprio patch, nunca uma lista fixa aqui.
arquivos_do_patch() {
  grep '^diff --git' "$PATCH" | sed 's|^diff --git a/||; s| b/.*||'
}

usage() {
  cat <<EOF
Uso: $(basename "$0") <comando>

  status        Diz se o patch local está aplicado e quais arquivos ele toca
  apply         Aplica o patch local (git apply, sem commit)
  restore-repo  Reverte SÓ o patch local (git apply -R) — preserva as outras alterações
  help          Esta ajuda

Patch: $PATCH
Regra: 'restore-repo' é obrigatório antes de commit/PR (gate do AGENTS.md).
Nunca usa 'git restore'/'git checkout --': isso apagaria também o trabalho do card
nos arquivos que o patch compartilha (ex.: application/hooks/SessionHook.php).
EOF
}

exige_patch() {
  [[ -f "$PATCH" ]] || { echo "ERRO: patch não encontrado em $PATCH"; echo "Defina PATCHES_LOCAIS_CIT se a pasta mudou."; exit 1; }
}

cmd_status() {
  exige_patch
  cd "$ROOT"
  local aplicado="indeterminado"
  if git apply --check "$PATCH" 2>/dev/null; then
    aplicado="NAO aplicado (o patch aplica limpo)"
  elif git apply --check -R "$PATCH" 2>/dev/null; then
    aplicado="APLICADO (reverte limpo)"
  else
    aplicado="PARCIAL ou conflitante — nem aplica nem reverte limpo"
  fi
  echo "patch local: $aplicado"
  echo
  echo "arquivos do patch x árvore de trabalho:"
  local f
  while IFS= read -r f; do
    if git diff --quiet -- "$f" 2>/dev/null; then
      printf '  %-70s igual ao HEAD\n' "$f"
    else
      printf '  %-70s ALTERADO\n' "$f"
    fi
  done < <(arquivos_do_patch)
  echo
  echo "Arquivo ALTERADO pode conter patch local, trabalho de card, ou os dois."
  echo "Antes de commit/PR: $(basename "$0") restore-repo"
}

cmd_apply() {
  exige_patch
  cd "$ROOT"
  if git apply --check -R "$PATCH" 2>/dev/null; then
    echo "Patch já está aplicado — nada a fazer."
    exit 0
  fi
  if ! git apply --check "$PATCH" 2>&1; then
    echo
    echo "ERRO: o patch não aplica limpo. Provável conflito com o trabalho do card."
    echo "Confira o arquivo apontado acima e aplique o trecho à mão."
    exit 1
  fi
  git apply "$PATCH"
  echo "Patch local aplicado (sem commit). Confira: git status"
}

cmd_restore_repo() {
  exige_patch
  cd "$ROOT"
  if git apply --check "$PATCH" 2>/dev/null; then
    echo "Patch local não está aplicado — árvore já limpa dele. Nada a reverter."
    exit 0
  fi
  if ! git apply --check -R "$PATCH" 2>&1; then
    echo
    echo "ERRO: o patch não reverte limpo — um dos arquivos tem patch local e trabalho"
    echo "de card misturados. NÃO force: reverta à mão só as linhas do patch no arquivo"
    echo "apontado acima e rode 'git diff' para confirmar que só o card sobrou."
    exit 1
  fi
  git apply -R "$PATCH"
  echo "Patch local revertido. Confira 'git status' — só o trabalho do card deve sobrar."
}

case "${1:-}" in
  status)       cmd_status ;;
  apply)        cmd_apply ;;
  restore-repo) cmd_restore_repo ;;
  -h|--help|help) usage ;;
  *) usage >&2; exit 1 ;;
esac
