#!/usr/bin/env bash
# frota.sh — catálogo, roteamento e integridade da frota de agentes.
#   listar [grupo]   tabela de agentes (todos ou de um grupo)
#   buscar <termo> [termo2 ...]   qual agente atende o tema (nome, descrição e corpo)
#   grupos           contagem por grupo
#   modelos          distribuição de modelo e política de custo
#   gatilhos [termo] quando cada especialista entra — por ARTEFATO, não por etapa
#   lint             integridade: nome, modelo, rodapé, grupo, comando, gatilho
set -uo pipefail
cd "${CURSOR_PROJECT_DIR:-$(dirname "$0")/../..}" || exit 1
AG=.cursor/agents
TSV=.cursor/frota/grupos.tsv
GAT=.cursor/frota/gatilhos.tsv

titulo() { case "$1" in
  fluxo)       echo "Fluxo do card — etapas com gate";;
  pesquisa)    echo "Pesquisa e conhecimento";;
  ia)          echo "IA, agentes e harness";;
  infra)       echo "Cloud e infraestrutura";;
  entrega)     echo "Entrega e qualidade";;
  dados)       echo "Dados";;
  backend)     echo "Backend e integração";;
  experiencia) echo "Experiência e frontend";;
  produto)     echo "Arquitetura, produto e negócio";;
  documentacao) echo "Documentação — ler, escrever, padronizar";;
  *)           echo "$1";;
esac; }

campo() { grep -m1 "^$2:" "$1" | cut -d: -f2- | sed 's/^ *//'; }

# tira acento para comparar: quem digita num terminal digita "cartao", e a description diz
# "cartão" — sem isso a busca devolve "nenhum agente" e empurra para criar um duplicado.
sem_acento() { sed 's/[áàâãäÁÀÂÃÄ]/a/g; s/[éèêëÉÈÊË]/e/g; s/[íìîïÍÌÎÏ]/i/g; s/[óòôõöÓÒÔÕÖ]/o/g; s/[úùûüÚÙÛÜ]/u/g; s/[çÇ]/c/g'; }

# ordem dos grupos = ordem de aparição no TSV (nunca uma lista fixa aqui, que desatualiza)
grupos_ordem() { awk -F'\t' '!v[$1]++ {print $1}' "$TSV"; }

linha_agente() {
  local f="$AG/$1.md"
  [ -f "$f" ] || { printf "  %-32s %-7s (ARQUIVO AUSENTE)\n" "$1" "-"; return; }
  local m d
  m=$(campo "$f" model); m=${m:-herda}
  d=$(campo "$f" description | cut -d. -f1 | cut -c1-62)
  printf "  %-32s %-7s %s\n" "$1" "$m" "$d"
}

cmd_listar() {
  local filtro="${1:-}"
  for g in $(grupos_ordem); do
    [ -n "$filtro" ] && [ "$g" != "$filtro" ] && continue
    local nomes; nomes=$(awk -F'\t' -v g="$g" '$1==g {print $2}' "$TSV")
    [ -z "$nomes" ] && continue
    echo
    echo "── $(titulo "$g")  [$g]"
    while read -r a; do linha_agente "$a"; done <<< "$nomes"
  done
}

cmd_buscar() {
  local termos="$*" achou=0
  echo "Agentes para \"$termos\":"
  echo
  # OR de TODOS os termos, sem acento — antes só "$2" era usado e o resto sumia calado.
  # Palavra de 1-2 letras vira ruído no OR ("regra de negocio" traria meio catálogo por "de"),
  # então só entra se for a única coisa buscada — é o caso de "ux", "ia", "bd".
  local lista; lista=$(printf '%s' "$termos" | sem_acento | tr -s '[:space:]' '\n' | grep -v '^$')
  local uteis; uteis=$(printf '%s\n' "$lista" | awk 'length($0)>2')
  [ -n "$uteis" ] && lista="$uteis"
  local padrao; padrao=$(printf '%s\n' "$lista" | paste -sd'|' -)
  [ -n "$padrao" ] || { echo "  (termo vazio)"; return; }
  # 1) nome ou descricao — casamento forte
  for f in "$AG"/*.md; do
    local n; n=$(basename "$f" .md)
    if echo "$n $(campo "$f" description)" | sem_acento | grep -qiE -- "$padrao"; then
      echo "  [direto]"; linha_agente "$n"; achou=1
    fi
  done
  # 2) corpo — casamento fraco, so se o forte nao achou
  if [ "$achou" -eq 0 ]; then
    for f in "$AG"/*.md; do
      sem_acento < "$f" | grep -qiE -- "$padrao" || continue
      linha_agente "$(basename "$f" .md)"; achou=1
    done
  fi
  [ "$achou" -eq 0 ] && {
    echo "  nenhum — antes de criar agente, fale com o engenheiro-de-brain (fusão é melhor que duplicata)"
    echo "  antes, confira o conhecimento: .cursor/scripts/kb.sh buscar $termos"; }
  echo
  echo "Chame com: Agent(subagent_type=\"<nome>\") ou pelo comando em .cursor/commands/"
}

cmd_grupos() {
  printf "%-14s %-4s %s\n" GRUPO QTD TEMA
  for g in $(grupos_ordem); do
    printf "%-14s %-4s %s\n" "$g" "$(awk -F'\t' -v g="$g" '$1==g' "$TSV" | wc -l)" "$(titulo "$g")"
  done
  echo "-----"
  printf "%-14s %-4s\n" TOTAL "$(grep -c '' "$TSV")"
}

cmd_modelos() {
  echo "Política de modelo — o modelo é escolhido pelo custo de errar, não pelo prestígio:"
  echo "  haiku   extrair, listar, conferir estrutura, ler e citar — sem julgamento"
  echo "  sonnet  escrever e revisar com padrão conhecido, configurar, diagnosticar com procedimento"
  echo "  opus    porta única: dinheiro, dado pessoal, contrato público, schema, causa raiz, arquitetura"
  echo
  printf "%-8s %-5s %s\n" MODELO QTD AGENTES
  for m in haiku sonnet opus; do
    local nomes qtd
    nomes=$(for f in "$AG"/*.md; do [ "$(campo "$f" model)" = "$m" ] && basename "$f" .md; done | tr '\n' ' ')
    qtd=$(echo "$nomes" | wc -w)
    printf "%-8s %-5s %s\n" "$m" "$qtd" "$(echo "$nomes" | fold -s -w 96 | sed '2,$s/^/                  /')"
  done
  echo "-----"
  printf "%-8s %-5s\n" TOTAL "$(ls "$AG"/*.md | wc -l)"
  echo
  echo "Mistura por grupo (grupo inteiro em opus é sinal de calibragem preguiçosa):"
  printf "  %-14s %s\n" GRUPO "haiku/sonnet/opus"
  for g in $(grupos_ordem); do
    local h=0 so=0 op=0
    while read -r a; do
      case "$(campo "$AG/$a.md" model)" in
        haiku) h=$((h+1));; sonnet) so=$((so+1));; opus) op=$((op+1));;
      esac
    done < <(awk -F'\t' -v g="$g" '$1==g {print $2}' "$TSV")
    printf "  %-14s %s/%s/%s\n" "$g" "$h" "$so" "$op"
  done
}

cmd_gatilhos() {
  local filtro="${*:-}"
  echo "Gatilho por ARTEFATO — vale em QUALQUER etapa do fluxo e em pedido avulso fora de card."
  echo "Produziu ou alterou o artefato, o especialista entra ANTES de ele sair. Insumo da etapa,"
  echo "nunca substituto do gate. Mecanismo e registro: .cursor/frota/gatilhos.md"
  echo
  printf "  %-30s %-18s %-5s %s\n" AGENTE CLASSE COMO CONDICAO
  local linhas
  linhas=$(awk -F'\t' '!/^#/ && NF>=4 {
      como = ($4 == "-") ? "decl" : "hook"
      printf "  %-30s %-18s %-5s %s\n", $1, $2, como, $3 }' "$GAT")
  if [ -n "$filtro" ]; then
    local padrao; padrao=$(printf '%s' "$filtro" | sem_acento | tr -s '[:space:]' '|')
    padrao=${padrao%|}
    linhas=$(printf '%s\n' "$linhas" | sem_acento | grep -iE -- "$padrao" || true)
    [ -z "$linhas" ] && { echo "  nenhum gatilho para \"$filtro\" — veja o catálogo: frota.sh gatilhos"; return; }
  fi
  printf '%s\n' "$linhas"
  echo
  echo "  hook = detectado por .cursor/scripts/hook_gatilhos.py (caminho, conteúdo ou comando)"
  echo "  decl = condição objetiva sem detecção mecânica: quem declara é o agente"
  local tot mec
  tot=$(awk -F'\t' '!/^#/ && NF>=4' "$GAT" | wc -l)
  mec=$(awk -F'\t' '!/^#/ && NF>=4 && $4!="-"' "$GAT" | wc -l)
  echo "-----"
  echo "$tot gatilho(s) · $mec por hook · $((tot-mec)) declarado(s)"
}

cmd_lint() {
  local erros=0 avisos=0
  # 1) agente sem grupo / grupo sem agente
  for f in "$AG"/*.md; do
    local n; n=$(basename "$f" .md)
    grep -qP "\t$n$" "$TSV" || { echo "ERRO  $n: fora de grupos.tsv"; erros=$((erros+1)); }
    [ "$(campo "$f" name)" = "$n" ] || { echo "ERRO  $n: campo name != nome do arquivo"; erros=$((erros+1)); }
    [ -n "$(campo "$f" description)" ] || { echo "ERRO  $n: sem description"; erros=$((erros+1)); }
    [ -n "$(campo "$f" tools)" ] || { echo "AVISO $n: sem tools (herda todas)"; avisos=$((avisos+1)); }
    case "$(campo "$f" model)" in
      haiku|sonnet|opus|fable) ;;
      "") echo "AVISO $n: sem model (herda o da sessão)"; avisos=$((avisos+1));;
      *)  echo "ERRO  $n: model inválido"; erros=$((erros+1));;
    esac
    # rodapé padrão de 3 linhas (Fase 3): aponta regras.md, declara o gatilho e o formato de retorno
    if ! grep -q '^## Regras da frota' "$f"; then
      echo "ERRO  $n: sem rodapé de regras"; erros=$((erros+1))
    else
      local rod; rod=$(awk '/^## Regras da frota/{p=1;next} p' "$f")
      printf '%s\n' "$rod" | grep -q 'frota/regras\.md' || { echo "ERRO  $n: rodapé não aponta frota/regras.md"; erros=$((erros+1)); }
      printf '%s\n' "$rod" | grep -q '^Gatilho:' || { echo "ERRO  $n: rodapé sem a linha Gatilho:"; erros=$((erros+1)); }
      printf '%s\n' "$rod" | grep -q '^Retorno:' || { echo "ERRO  $n: rodapé sem a linha Retorno:"; erros=$((erros+1)); }
      [ "$(printf '%s\n' "$rod" | grep -c .)" -le 3 ] || { echo "AVISO $n: rodapé com mais de 3 linhas (regra copiada volta a divergir)"; avisos=$((avisos+1)); }
    fi
    grep -q '^## Regras invioláveis' "$f" && { echo "ERRO  $n: cópia antiga das regras no corpo — aponte frota/regras.md"; erros=$((erros+1)); }
    local dl; dl=$(campo "$f" description | wc -m)
    [ "$dl" -gt 280 ] && { echo "AVISO $n: description com $dl caracteres (roteia pior e custa em toda sessão)"; avisos=$((avisos+1)); }
  done
  while IFS=$'\t' read -r _ a; do
    [ -f "$AG/$a.md" ] || { echo "ERRO  $a: em grupos.tsv sem arquivo em agents/"; erros=$((erros+1)); }
  done < "$TSV"
  # 2) cobertura de gatilho: especialista sem condicao de disparo e agente que ninguem chama
  while IFS=$'\t' read -r g a; do
    [ "$g" = fluxo ] && continue
    grep -qP "^$a\t" "$GAT" || { echo "ERRO  $a: especialista sem gatilho em frota/gatilhos.tsv"; erros=$((erros+1)); }
  done < "$TSV"
  # (sem pipe para o while: no subshell o contador de erros se perdia e o lint saía 0 com erro)
  local a c
  for a in $(awk -F'\t' '!/^#/ && NF>=4 {print $1}' "$GAT" | sort -u); do
    [ -f "$AG/$a.md" ] || { echo "ERRO  gatilhos.tsv: agente inexistente '$a'"; erros=$((erros+1)); }
  done
  local ruins; ruins=$(awk -F'\t' '!/^#/ && NF && NF!=4 {print "ERRO  gatilhos.tsv linha com " NF " campos: " $1}' "$GAT")
  [ -n "$ruins" ] && { echo "$ruins"; erros=$((erros+$(printf '%s\n' "$ruins" | wc -l))); }

  # 3) comando citando agente inexistente (qualquer nome de agente em crase)
  local nomes_ag; nomes_ag=$(ls "$AG" | sed 's/\.md$//')
  for c in .cursor/commands/*.md; do
    for a in $(grep -oP '`\K(especialista|engenheiro|analista|arquiteto|revisor|validador|leitor|levantador|mapeador|pesquisador|redator|gestor|testador|desenvolvedor|escritor|destilador|ambiente)[a-z0-9-]*(?=`)' "$c" | sort -u); do
      printf '%s\n' "$nomes_ag" | grep -qx "$a" || { echo "ERRO  $(basename "$c"): cita agente inexistente '$a'"; erros=$((erros+1)); }
    done
  done
  echo "-----"
  echo "$(ls "$AG"/*.md | wc -l) agentes · $erros erro(s) · $avisos aviso(s)"
  [ "$erros" -eq 0 ] || return 1
}

case "${1:-listar}" in
  listar) cmd_listar "${2:-}";;
  buscar) [ -n "${2:-}" ] || { echo "uso: frota.sh buscar <termo> [termo2 ...]"; exit 1; }; shift; cmd_buscar "$@";;
  grupos) cmd_grupos;;
  modelos) cmd_modelos;;
  gatilhos) shift || true; cmd_gatilhos "$@";;
  lint)   cmd_lint;;
  *) sed -n '2,8p' "$0" | sed 's/^# \?//'; exit 1;;
esac
