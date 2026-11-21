#!/usr/bin/env bash
# Acesso ao dado AO VIVO de homologação, via API do próprio CIT.
#
# Por que existe: o MySQL em 127.0.0.1:3309 tem nome enganoso — é dump congelado, serve
# para conferir schema, não dado real. O caminho para o dado ao vivo é o endpoint de
# execução controlada, exposto pelo CIT fora de produção e sem autenticação. Sem este
# script a informação vivia só na memória da sessão, e a frase "não tenho acesso ao banco
# de homol" voltava a cada aba nova — errada.
#
# Uso:
#   homol.sh select  <conexao> <tabela> <campos-csv> [coluna=valor ...]
#   homol.sh update  <conexao> <tabela> <col=val,col=val> <coluna=valor ...>
#   homol.sh limpar  <cnpj> <email> [otp]
#   homol.sh ping
#
#   conexao: crm (banco do CRM) | db (banco do CIT)
#   Só igualdade no where, uma tabela por chamada, sem JOIN e sem LIMIT.
#   No update, o valor NULL (maiúsculo) grava null de verdade: col=NULL.
#   Não faz INSERT nem DELETE — para isso, pedir execução ou acesso direto ao MySQL.
#
# Base URL override: HOMOL_BASE=https://outro.host homol.sh ...
# Específico do CIT: em outro repositório, confira no perfil qual é a fonte de homol.
set -uo pipefail

BASE="${HOMOL_BASE:-https://homol.cit.solides.adm.br}"
EP="$BASE/homologacao/execucao-controlada"

_post() {  # $1 = json
  curl -s -m 40 -X POST "$1" -H "Content-Type: application/json" -d "$2" \
    | python3 -c '
import json, sys
bruto = sys.stdin.read()
try:
    d = json.loads(bruto)
except json.JSONDecodeError:
    # o endpoint devolve HTML de erro do CodeIgniter quando a query nao cola
    import re
    # tira <style>/<script> antes das tags: senao o erro do CI despeja CSS no contexto
    txt = re.sub(r"(?is)<(style|script).*?</\1>", " ", bruto)
    txt = " ".join(re.sub(r"<[^>]+>", " ", txt).split())
    print("ERRO — resposta não-JSON (tabela/coluna inexistente na conexão?):")
    print(" ", txt[:300] or "(vazio)")
    raise SystemExit(1)
if not d.get("success"):
    print("ERRO:", d.get("msg") or d)
    raise SystemExit(1)
dd = d.get("data", {})
op, con, tab = dd.get("operation"), dd.get("connection"), dd.get("table")
print(op, " ", con, ".", tab, " — ", dd.get("affected_rows"), " linha(s)", sep="")
print("query:", " ".join(str(dd.get("last_query", "")).split()))
for r in (dd.get("rows") or []):
    print("  ", json.dumps(r, ensure_ascii=False))
'
}

_where_json() {  # coluna=valor ... -> {"col":"val",...}
  python3 -c '
import json, sys
d = {}
for a in sys.argv[1:]:
    if "=" not in a:
        print(f"argumento sem = : {a}", file=sys.stderr); raise SystemExit(2)
    k, v = a.split("=", 1)
    d[k] = v
print(json.dumps(d, ensure_ascii=False))
' "$@"
}

case "${1:-}" in
  select)
    [ $# -ge 4 ] || { echo "uso: homol.sh select <conexao> <tabela> <campos-csv> [col=val ...]"; exit 1; }
    conexao=$2; tabela=$3; campos=$4; shift 4
    where=$(_where_json "$@") || exit 2
    payload=$(python3 -c '
import json, sys
print(json.dumps({"operacao": "select", "conexao": sys.argv[1], "tabela": sys.argv[2],
                  "campos": [c.strip() for c in sys.argv[3].split(",") if c.strip()],
                  "where": json.loads(sys.argv[4])}, ensure_ascii=False))
' "$conexao" "$tabela" "$campos" "$where")
    _post "$EP" "$payload"
    ;;
  update)
    [ $# -ge 5 ] || { echo "uso: homol.sh update <conexao> <tabela> <col=val,col=val> <col=val ...>"; exit 1; }
    conexao=$2; tabela=$3; sets=$4; shift 4
    where=$(_where_json "$@") || exit 2
    payload=$(python3 -c '
import json, sys
# Homologacao_rest.php:242-246 le payload["dados"] no update (so o select usa "campos").
# NULL (maiusculo) na CLI vira null JSON — sem isso nao ha como zerar coluna DATE/DATETIME.
dados = {}
for p in sys.argv[3].split(","):
    if "=" not in p:
        continue
    k, v = p.split("=", 1)
    dados[k] = None if v == "NULL" else v
print(json.dumps({"operacao": "update", "conexao": sys.argv[1], "tabela": sys.argv[2],
                  "dados": dados, "where": json.loads(sys.argv[4])}, ensure_ascii=False))
' "$conexao" "$tabela" "$sets" "$where")
    echo "UPDATE em homologação — payload:"; echo "  $payload"
    _post "$EP" "$payload"
    ;;
  limpar)
    [ $# -ge 3 ] || { echo "uso: homol.sh limpar <cnpj> <email> [otp]"; exit 1; }
    payload=$(python3 -c '
import json, sys
d = {"cnpj": sys.argv[1], "email": sys.argv[2]}
if len(sys.argv) > 3: d["limpar_otp"] = sys.argv[3]
print(json.dumps(d, ensure_ascii=False))
' "$2" "$3" ${4:+"$4"})
    echo "Zera assinatura + formulário + termo + OTP do CNPJ em homologação:"; echo "  $payload"
    curl -s -m 40 -X POST "$BASE/homologacao/limpar-cancelamento-testes" \
      -H "Content-Type: application/json" -d "$payload" | head -c 800; echo
    ;;
  ping)
    printf "%s -> " "$EP"
    curl -s -o /dev/null -m 20 -w "%{http_code}\n" -X POST "$EP" \
      -H "Content-Type: application/json" \
      -d '{"operacao":"select","conexao":"crm","tabela":"CCLIFOR","campos":["ID"],"where":{"ID":"1"}}'
    ;;
  *)
    sed -n '10,22p' "$0" | sed 's/^# \{0,1\}//'
    exit 1 ;;
esac
