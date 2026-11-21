#!/usr/bin/env bash
# Aplica proteção de branch no GitHub (staging e main) via gh api.
# Uso: GITHUB_REPOSITORY=owner/repo ./scripts/apply-branch-protection.sh
# Requer: gh autenticado com escopo admin (repo / branch protection).
#
# Esteira full-auto: 0 revisões obrigatórias; merge quando lint-and-test estiver verde.
# Trade-off: sem gate humano no GitHub — confiamos no CI e nas notificações (e-mail/Slack).
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-LuizGustavoVJ/Brain-Cursor}"
CI_CONTEXT="${CI_STATUS_CONTEXT:-lint-and-test}"

protect_branch() {
  local branch=$1
  local require_reviews=${2:-0}
  echo "Protegendo branch: $branch (repo $REPO, reviews=$require_reviews)"
  gh api --method PUT "repos/${REPO}/branches/${branch}/protection" --input - <<EOF
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["${CI_CONTEXT}"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "required_approving_review_count": ${require_reviews}
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true
}
EOF
}

protect_branch staging 0
protect_branch main 0

gh api --method PATCH "repos/${REPO}" -f delete_branch_on_merge=true >/dev/null
echo "delete_branch_on_merge=true (só main e staging permanecem após merge dos PRs)."

echo "Concluído. Check obrigatório: ${CI_CONTEXT}."