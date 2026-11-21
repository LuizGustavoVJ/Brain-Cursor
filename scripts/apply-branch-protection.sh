#!/usr/bin/env bash
# Aplica proteção de branch no GitHub (staging e main) via gh api.
# Uso: GITHUB_REPOSITORY=owner/repo ./scripts/apply-branch-protection.sh
# Requer: gh autenticado com escopo admin (repo / branch protection).
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-LuizGustavoVJ/Brain-Cursor}"
CI_CONTEXT="${CI_STATUS_CONTEXT:-lint-and-test}"

protect_branch() {
  local branch=$1
  local require_reviews=${2:-1}
  echo "Protegendo branch: $branch (repo $REPO)"
  gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    "repos/${REPO}/branches/${branch}/protection" \
    -f required_status_checks='{"strict":true,"contexts":["'"$CI_CONTEXT"'"]}' \
    -f enforce_admins=false \
    -f required_pull_request_reviews='{"required_approving_review_count":'"$require_reviews"',"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
    -f restrictions=null \
    -f required_linear_history=false \
    -f allow_force_pushes=false \
    -f allow_deletions=false \
    -f block_creations=false \
    -f required_conversation_resolution=true
}

protect_branch staging 1
# main: promoção via PR automático staging→main; revisão opcional (0) se Luiz aprova só no staging
protect_branch main 0

gh api --method PATCH "repos/${REPO}" -f delete_branch_on_merge=true >/dev/null
echo "delete_branch_on_merge=true (só main e staging permanecem após merge dos PRs)."

echo "Concluído. Ajuste contexts se o nome do job CI mudar ($CI_CONTEXT)."