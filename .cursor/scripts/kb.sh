#!/usr/bin/env bash
# kb.sh — busca no acervo de conhecimento do projeto (Brain).
#
# Uso:
#   .cursor/scripts/kb.sh buscar <termo> [termo2 ...]   # ranqueia arquivos por nº de ocorrências
#   .cursor/scripts/kb.sh indice                        # (re)gera docs/INDICE.md
#   .cursor/scripts/kb.sh dominios                      # lista os mapas de domínio disponíveis
#   .cursor/scripts/kb.sh ancorar                       # trava a assinatura de cada âncora arquivo:linha
#   .cursor/scripts/kb.sh verificar [--dry-run]         # corrige as âncoras que moveram; reporta as órfãs
#   .cursor/scripts/kb.sh sujos                         # lista mapas afetados por edições recentes
#   .cursor/scripts/kb.sh limpar-sujos                  # zera a lista (só após destilar)
#
# Fontes varridas, na ordem de prioridade:
#   1. .cursor/skills/dominio-*/SKILL.md  — mapas destilados (leia estes primeiro)
#   2. memória do projeto                 — fatos persistentes
#   3. docs/analises, docs/fluxos, docs/implementacoes — acervo bruto por card
set -uo pipefail

RAIZ="${CURSOR_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$RAIZ" || exit 1
MEM="$HOME/.cursor/projects/$(echo "$RAIZ" | tr '/' '-')/memory"

fontes() {
    find .cursor/skills -maxdepth 2 -name 'SKILL.md' -path '*dominio-*' 2>/dev/null
    [ -d "$MEM" ] && find "$MEM" -maxdepth 1 -name '*.md' 2>/dev/null
    find docs/analises docs/fluxos docs/implementacoes -name '*.md' 2>/dev/null
}

rotulo() {
    case "$1" in
        .cursor/skills/*) echo "DOMINIO " ;;
        "$MEM"/*)         echo "MEMORIA " ;;
        docs/analises/*)  echo "ANALISE " ;;
        docs/fluxos/*)    echo "FLUXO   " ;;
        *)                echo "IMPL    " ;;
    esac
}

cmd_buscar() {
    [ $# -eq 0 ] && { echo "uso: kb.sh buscar <termo> [termo2 ...]" >&2; exit 2; }
    local padrao; padrao=$(printf '%s\\|' "$@"); padrao="${padrao%\\|}"
    local encontrou=0
    while IFS= read -r arq; do
        [ -f "$arq" ] || continue
        local n; n=$(grep -ic "$padrao" "$arq" 2>/dev/null) || n=0
        [ "$n" -eq 0 ] && continue
        local r; r=$(rotulo "$arq")
        local prio=3
        case "$r" in DOMINIO*) prio=1 ;; MEMORIA*) prio=2 ;; esac
        printf '%s\t%s\t%s%s\n' "$prio" "$n" "$r" "$arq"; encontrou=1
    done < <(fontes) | sort -t$'\t' -k1,1n -k2,2nr | head -25 | awk -F'\t' '{printf "%4s hits  %s\n", $2, $3}'
    [ "$encontrou" -eq 0 ] && echo "(nada no acervo para: $*)"
    echo
    echo "Leia primeiro os DOMINIO — já são a destilação. Acervo bruto só se o mapa não responder."
}

cmd_dominios() {
    for s in .cursor/skills/dominio-*/SKILL.md; do
        [ -f "$s" ] || { echo "(nenhum mapa de domínio ainda)"; return; }
        printf '%-34s %s\n' "$(basename "$(dirname "$s")")" \
            "$(awk '/^description:/{f=1;next} f&&/^[a-z_]+:/{exit} f{gsub(/^[ ]+/,"");printf "%s ",$0}' "$s" | cut -c1-110)"
    done
}

cmd_indice() {
    local out=docs/INDICE.md
    {
        echo "# Índice do acervo"
        echo
        echo "> Gerado por \`.cursor/scripts/kb.sh indice\`. Não editar à mão."
        echo
        echo "## Mapas de domínio (leia primeiro)"
        echo
        echo "| Mapa | Escopo |"
        echo "|---|---|"
        for s in .cursor/skills/dominio-*/SKILL.md; do
            [ -f "$s" ] || continue
            local nome; nome=$(basename "$(dirname "$s")")
            local desc; desc=$(awk '/^description:/{f=1;next} f&&/^[a-z_]+:/{exit} f{gsub(/^[ ]+/,"");printf "%s ",$0}' "$s" | cut -c1-160)
            echo "| [$nome](../$s) | $desc |"
        done
        echo
        echo "## Acervo por tema"
        echo
        echo "| Tema | Análises | Fluxos | Implementações |"
        echo "|---|---|---|---|"
        for tema in $(ls docs/analises 2>/dev/null); do
            local a f i
            a=$(find "docs/analises/$tema" -name '*.md' 2>/dev/null | wc -l)
            f=$(find "docs/fluxos/$tema" -name '*.md' 2>/dev/null | wc -l)
            i=$(find docs/implementacoes -name "*${tema}*" 2>/dev/null | wc -l)
            echo "| \`$tema\` | $a | $f | $i |"
        done
        echo
        echo "## Cards documentados"
        echo
        grep -rhoE '\b1[45678][0-9]{4}\b' docs/analises docs/fluxos docs/implementacoes --include='*.md' 2>/dev/null \
            | sort -u | tr '\n' ' ' | fold -s -w 100
        echo
    } > "$out"
    echo "gerado: $out ($(wc -l < "$out") linhas)"
}

case "${1:-}" in
    buscar)   shift; cmd_buscar "$@" ;;
    indice)   cmd_indice ;;
    dominios) cmd_dominios ;;
    ancorar)  shift; python3 "$(dirname "$0")/ancoras.py" lock "$@" ;;
    verificar) shift; python3 "$(dirname "$0")/ancoras.py" verificar "$@" ;;
    sujos)    cat "$(dirname "$0")/../cache/dominios-sujos" 2>/dev/null || echo "(nenhum mapa sujo)" ;;
    limpar-sujos) rm -f "$(dirname "$0")/../cache/dominios-sujos" && echo "lista de mapas sujos zerada" ;;
    *) sed -n '2,12p' "$0" | sed 's/^# \?//'; exit 2 ;;
esac
