#!/usr/bin/env bash
# propagar.sh — replica o Brain deste repositório em TODOS os repos da máquina.
#
# Por que existe: o Brain genérico (frota, comandos, scripts, hooks, regras) tem de ser o
# MESMO em todo repo — versão diferente por repo é a falha de fonte única em forma de pasta:
# o agente obedece uma regra no cit e outra no gestao, e ninguém percebe até dar ruim.
# Regra do usuário (21/08/2026): toda alteração em .cursor/ ou no AGENTS.md é replicada em
# todos os repositórios, sem pedir permissão.
#
# O que NÃO viaja (arquitetura de cada projeto é dela):
#   - .cursor/arquitetura/{ambiente-local,estado-projeto,alteracoes-ambiente-local}-<repo>.md
#   - .cursor/skills/dominio-*        (mapa de domínio é do negócio daquele repo)
#   - .cursor/settings.local.json     (permissões locais da máquina/repo)
#   - .cursor/cache/, *.lock, .mcp.json, __pycache__
#   - scripts/homol.sh                (endpoint de execução controlada é do CIT)
#   - o que o destino declarar em .cursor/proprio.txt (um caminho ou glob por linha,
#     relativo a .cursor/ — ex.: skills/powerbi-relatorios, scripts/relatorio_*.py,
#     agents/meu-agente.md, commands/meu-comando.md, frota/*.local.md). Vale também DENTRO de
#     agents/ commands/ frota/ rules/ sustentacao/ implementacao/ scripts/ e skills/: o rsync recebe
#     --exclude e nem sobrescreve nem apaga o que é do destino.
#
# ORIGEM ÚNICA: só roda a partir do cit. Rodado de outro repo, o "Brain" daquele repo viraria a
# origem e sobrescreveria (e podaria) o cit e todos os outros — a fonte única ao contrário.
#
# PODA (o que o destino perde): o que saiu da origem sai do destino. Sem isso, arquivo ou
# pasta apagada aqui SOBREVIVE nos outros repos e o agente passa a obedecer a versão morta —
# exatamente o defeito que a fonte única existe para matar. Aconteceu em 21/08/2026: a pasta
# .cursor/rules foi apagada no cit e continuou viva em 12 repos, com a regra nova ao lado.
# Antes de escrever ou apagar, backup datado em ~/backups-brain/.
#
# Uso:  bash .cursor/scripts/propagar.sh [--dry-run] [repo ...]
set -uo pipefail

ORIGEM="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ORIGEM_OFICIAL="/var/www/html/cit"   # sem barra final: a troca de caminho abaixo não o reescreve
if [ "$ORIGEM" != "$ORIGEM_OFICIAL" ]; then
  echo "propagar.sh: recusado — a origem do Brain é $ORIGEM_OFICIAL, não $ORIGEM." >&2
  echo "Edite o Brain no cit e rode de lá: bash $ORIGEM_OFICIAL/.cursor/scripts/propagar.sh" >&2
  exit 3
fi
NOME_ORIGEM="$(basename "$ORIGEM")"
RAIZ="$(dirname "$ORIGEM")"
DATA="$(date +%Y%m%d-%H%M%S)"
BACKUP="$HOME/backups-brain/$DATA"

DRY=0
[ "${1:-}" = "--dry-run" ] && { DRY=1; shift; }

DIRS_GEN="agents commands frota rules sustentacao implementacao"
ARQ_GEN="fluxo-completo.md habilidades.md otimizacao-custos.md README.md settings.json hooks.json"
ARQUITETURA_GEN="automacoes.md brain.md estrutura-cursor.md estrutura-docs.md"
PERFIL_GEN="ambiente-local estado-projeto alteracoes-ambiente-local"

alvos=()
if [ $# -gt 0 ]; then
  for r in "$@"; do alvos+=("$r"); done
else
  for d in "$RAIZ"/*/; do
    r="$(basename "$d")"
    [ "$r" = "$NOME_ORIGEM" ] && continue
    [ -d "$d/.git" ] || continue          # só repositório git
    alvos+=("$r")
  done
fi

echo "=== propagar Brain: $NOME_ORIGEM -> ${#alvos[@]} repo(s) ==="
[ $DRY -eq 1 ] && echo "(--dry-run: nada é escrito)"
echo "backup: $BACKUP"
echo

# proprios_em() — lê o proprio.txt do destino e devolve, um por linha, o que ele declara
# dentro do subdiretório $1 (relativo ao subdiretório, pronto para --exclude do rsync).
proprios_em() {
  [ -f "$dest/.cursor/proprio.txt" ] || return 0
  local linha
  while IFS= read -r linha || [ -n "$linha" ]; do
    linha="${linha%%#*}"; linha="${linha//[[:space:]]/}"
    case "$linha" in "$1"/?*) printf '%s\n' "${linha#"$1"/}" ;; esac
  done < "$dest/.cursor/proprio.txt"
}

copia() { # copia() origem destino [subdir-de-.cursor para ler o proprio.txt]
  local excl=() p
  if [ -n "${3:-}" ]; then
    while IFS= read -r p; do [ -n "$p" ] && excl+=("--exclude=/$p"); done < <(proprios_em "$3")
  fi
  if [ $DRY -eq 1 ]; then
    echo "      would: $2${excl[*]:+  (protegido do destino: ${excl[*]#--exclude=})}"; return
  fi
  rsync -a --delete "${excl[@]}" "$1" "$2"
}

# protegido() — o que a poda NUNCA remove. Usa $dest e $repo do laço.
# Caminho recebido é relativo a .cursor/ (ex.: skills/dominio-termo-aceite).
protegido() {
  case "$1" in
    settings.local.json|settings.local.json.bak*|proprio.txt|.mcp.json|cache|*.lock) return 0 ;;
    __pycache__|*/__pycache__|scripts/homol.sh|skills/dominio-*)                      return 0 ;;
  esac
  for p in $PERFIL_GEN; do
    [ "$1" = "arquitetura/$p-$repo.md" ] && return 0
  done
  # o destino declara o que é dele: um caminho ou glob por linha, # comenta
  if [ -f "$dest/.cursor/proprio.txt" ]; then
    while IFS= read -r linha || [ -n "$linha" ]; do
      linha="${linha%%#*}"; linha="${linha//[[:space:]]/}"
      [ -z "$linha" ] && continue
      case "$1" in $linha) return 0 ;; esac      # $linha sem aspas: glob proposital
    done < "$dest/.cursor/proprio.txt"
  fi
  return 1
}

# poda() — remove no destino o que não existe mais na origem e não é protegido.
# Recebe o subdiretório de .cursor (vazio = topo). Não desce recursivamente: os
# diretórios genéricos já vêm espelhados por rsync --delete.
poda() {
  local rel="$1" base a n chave
  base="$dest/.cursor${rel:+/$rel}"
  [ -d "$base" ] || return 0
  for a in "$base"/* "$base"/.[!.]*; do
    [ -e "$a" ] || continue
    n="$(basename "$a")"
    chave="${rel:+$rel/}$n"
    protegido "$chave" && continue
    [ -e "$ORIGEM/.cursor/$chave" ] && continue
    podados=$((podados+1))
    if [ $DRY -eq 1 ]; then echo "      would rm: .cursor/$chave"; else rm -rf "$a"; fi
  done
}

for repo in "${alvos[@]}"; do
  dest="$RAIZ/$repo"
  [ -d "$dest" ] || { echo "  ! $repo: diretório não existe — pulado"; continue; }
  novo=0; [ -d "$dest/.cursor" ] || novo=1

  # ---- backup antes de qualquer escrita (.cursor é gitignored em vários repos: sem git não há volta)
  if [ $DRY -eq 0 ] && [ $novo -eq 0 ]; then
    mkdir -p "$BACKUP/$repo"
    cp -a "$dest/.cursor" "$BACKUP/$repo/.cursor"
    [ -f "$dest/AGENTS.md" ] && cp -a "$dest/AGENTS.md" "$BACKUP/$repo/AGENTS.md"
  fi

  [ $DRY -eq 0 ] && mkdir -p "$dest/.cursor/arquitetura" "$dest/.cursor/skills"

  # ---- diretórios inteiramente genéricos
  for d in $DIRS_GEN; do
    [ -d "$ORIGEM/.cursor/$d" ] || continue
    copia "$ORIGEM/.cursor/$d/" "$dest/.cursor/$d/" "$d"
  done

  # ---- scripts: tudo menos o que é específico da origem
  copia_scripts() {
    local excl=(--exclude 'homol.sh') p
    while IFS= read -r p; do [ -n "$p" ] && excl+=("--exclude=/$p"); done < <(proprios_em scripts)
    if [ $DRY -eq 1 ]; then echo "      would: .cursor/scripts/ (menos: ${excl[*]#--exclude})"; return; fi
    rsync -a "${excl[@]}" "$ORIGEM/.cursor/scripts/" "$dest/.cursor/scripts/"
  }
  copia_scripts

  # ---- skills: uma por uma, com --delete dentro de cada uma (arquivo removido na skill sai
  #      no destino também). Mapa de domínio não viaja e o do destino não é tocado.
  for s in "$ORIGEM/.cursor/skills"/*/; do
    [ -d "$s" ] || continue
    n_sk_i="$(basename "$s")"
    case "$n_sk_i" in dominio-*) continue ;; esac
    protegido "skills/$n_sk_i" && { echo "      protegido (proprio.txt): skills/$n_sk_i"; continue; }
    copia "$s" "$dest/.cursor/skills/$n_sk_i/" "skills/$n_sk_i"
  done

  # ---- arquitetura: só os genéricos; o trio de perfil do destino não é tocado
  for f in $ARQUITETURA_GEN; do
    [ -f "$ORIGEM/.cursor/arquitetura/$f" ] || continue
    [ $DRY -eq 1 ] || cp -a "$ORIGEM/.cursor/arquitetura/$f" "$dest/.cursor/arquitetura/$f"
  done

  # ---- arquivos soltos + AGENTS.md
  for f in $ARQ_GEN; do
    [ -f "$ORIGEM/.cursor/$f" ] || continue
    [ $DRY -eq 1 ] || cp -a "$ORIGEM/.cursor/$f" "$dest/.cursor/$f"
  done
  [ $DRY -eq 1 ] || cp -a "$ORIGEM/AGENTS.md" "$dest/AGENTS.md"

  # ---- caminho absoluto da origem não pode viajar (settings.json cita o script do ADO)
  if [ $DRY -eq 0 ]; then
    grep -rl "/var/www/html/$NOME_ORIGEM/" "$dest/.cursor" "$dest/AGENTS.md" 2>/dev/null \
      | while read -r a; do sed -i "s#/var/www/html/$NOME_ORIGEM/#/var/www/html/$repo/#g" "$a"; done
  fi

  # ---- perfil do projeto: criar esqueleto só se faltar (NUNCA com dado de outro projeto)
  criados=0
  for p in $PERFIL_GEN; do
    alvo="$dest/.cursor/arquitetura/$p-$repo.md"
    [ -f "$alvo" ] && continue
    criados=$((criados+1))
    [ $DRY -eq 1 ] && continue
    case $p in
      ambiente-local) t="Ambiente local — $repo";  q="URLs, portas, Docker, banco, pasta de testes" ;;
      estado-projeto) t="Estado do projeto — $repo"; q="stack, decisões estáveis, particularidades" ;;
      *)              t="Alterações de ambiente local — $repo"; q="patches locais que não vão para o repositório" ;;
    esac
    cat > "$alvo" <<PERFIL
# $t

> **ESQUELETO — PREENCHER.** Criado por \`propagar.sh\` em $DATA porque este repositório não
> tinha o perfil. Conteúdo esperado: $q.
>
> **Não copiar dado de outro projeto aqui.** URL, porta e banco de outro repo levam o agente a
> subir o ambiente errado — é falha conhecida do Brain. Enquanto estiver vazio, o agente deve
> **medir** (docker compose ps, .env do repo) e registrar aqui o que mediu.

## Gate L0

- [ ] app no ar e URL informada no chat
- [ ] banco acessível

## A preencher

- Stack:
- Como sobe:
- URL local:
- Banco (host/porta/schema):
- Testes:
PERFIL
  done

  # ---- perfil de OUTRO projeto não pode morar aqui: URL/porta/banco errados sobem o ambiente
  #      errado. Já aconteceu (perfil do cit em 8 repos, herdado de cópia antiga do .claude).
  intrusos=0
  for a in "$dest/.cursor/arquitetura"/*.md; do
    [ -f "$a" ] || continue
    b="$(basename "$a" .md)"
    dono=""
    for p in $PERFIL_GEN; do
      case "$b" in "$p-"*) dono="${b#"$p-"}"; break ;; esac
    done
    [ -z "$dono" ] && continue           # arquivo genérico, não é perfil
    [ "$dono" = "$repo" ] && continue    # perfil deste repo: fica
    intrusos=$((intrusos+1)); [ $DRY -eq 0 ] && rm -f "$a"
  done

  # ---- poda: o que saiu da origem sai do destino (topo, skills, scripts, arquitetura)
  podados=0
  poda ""
  poda skills
  poda scripts
  poda arquitetura

  # ---- manter o Brain fora do git do produto sem tocar arquivo versionado
  #      (.gitignore é rastreado; .git/info/exclude é local e resolve igual)
  ign="ok"
  if ! git -C "$dest" check-ignore -q .cursor 2>/dev/null; then
    if [ $DRY -eq 0 ]; then
      exc="$dest/.git/info/exclude"
      grep -qx '.cursor/' "$exc" 2>/dev/null || printf '.cursor/\n' >> "$exc"
      grep -qx '/AGENTS.md' "$exc" 2>/dev/null || printf '/AGENTS.md\n' >> "$exc"
    fi
    ign="excluído via .git/info/exclude"
  fi

  n_ag=$(ls -1 "$dest/.cursor/agents"/*.md 2>/dev/null | wc -l)
  n_cm=$(ls -1 "$dest/.cursor/commands"/*.md 2>/dev/null | wc -l)
  n_sk=$(ls -1d "$dest/.cursor/skills"/*/ 2>/dev/null | wc -l)
  n_dom=$(ls -1d "$dest/.cursor/skills"/dominio-*/ 2>/dev/null | wc -l)
  printf "  %-27s %s · agentes=%s comandos=%s skills=%s (dominio próprios=%s) · perfil criado=%s · perfil intruso removido=%s · podado=%s · git=%s\n" \
    "$repo" "$([ $novo -eq 1 ] && echo 'BRAIN NOVO' || echo 'atualizado')" \
    "$n_ag" "$n_cm" "$n_sk" "$n_dom" "$criados" "$intrusos" "$podados" "$ign"
done

echo
if [ $DRY -eq 1 ]; then
  echo "dry-run: nada foi escrito."
else
  echo "backup dos .cursor anteriores: $BACKUP"
  echo "conferir cada repo:  for r in $RAIZ/*/; do (cd \$r && bash .cursor/scripts/frota.sh lint 2>/dev/null | tail -1); done"
fi
