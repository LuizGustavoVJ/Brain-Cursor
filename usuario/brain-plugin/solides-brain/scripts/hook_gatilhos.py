#!/usr/bin/env python3
"""Reflexo do Brain — cobra o especialista pelo ARTEFATO produzido, não pela etapa.

O problema que este hook resolve: o gatilho de especialista vivia ancorado em quatro janelas do
fluxo (S3-rev, I1-rev, I6-rev, I12). Fora delas — e em pedido avulso, sem card — nada obrigava
nada. Foi por essa fresta que uma consulta SQL saiu para o usuário rodar em producao sem passar
pelo `especialista-sql` e voltou com erro 1064.

Desenho: a condicao passa a ser o artefato. Escreveu SQL, migration, rota, calculo de dinheiro,
credencial, view, container, pipeline ou dependencia? O especialista daquela classe entra ANTES
de o artefato sair. A tabela e dado, nao prosa: `.cursor/frota/gatilhos.tsv`.

Eventos (registrados em .cursor/settings.json):
  PostToolUse[Agent]          registra o subagente chamado — quita a pendencia da classe dele
                              (a ferramenta se chama `Agent`; `Task` fica aceito por compatibilidade)
  PostToolUse[Edit|Write]     classifica caminho + conteudo escrito
  PostToolUse[Bash]           classifica o comando executado
  Stop                        cobra o que ficou pendente ao fim do turno (decision:block, 1x)

So ARTEFATO dispara, nunca palavra solta (correcao de 25/09/2026 — o hook casava "sql",
"dig", "lambda" em documento de analise e cobrava 13 classes sem artefato nenhum):
  texto:  vale so para arquivo de CODIGO do repo (fora de docs/, fora de .md/.txt/.html de doc)
  doc:    vale para documento (docs/, .md, .txt, .html) e arquivo fora do repo — so classes com
          forma inequivoca (SQL no inicio de linha ou bloco ```sql, DDL)
  cmd:    casado contra o INICIO de cada comando da linha (separado por ; && || | e quebra),
          com heredoc removido e sem IGNORECASE — `grep "5-6 dig"` nao e `dig`.

Economia: cada classe fala UMA vez por sessao, no maximo 3 por mensagem, e o hook e silencioso
quando o especialista ja foi consultado. O reflexo nao pode custar mais do que o erro que evita.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time

RAIZ = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR")
                    or pathlib.Path(__file__).resolve().parents[2]).resolve()
TABELA = RAIZ / ".cursor/frota/gatilhos.tsv"
if not TABELA.is_file() and os.environ.get("CLAUDE_PLUGIN_ROOT"):
    # rodando empacotado como plugin: a tabela viaja em <plugin>/frota/
    TABELA = pathlib.Path(os.environ["CLAUDE_PLUGIN_ROOT"]) / "frota/gatilhos.tsv"
CACHE = RAIZ / ".cursor/cache/gatilhos"

MAX_POR_MENSAGEM = 3      # o reflexo avisa, nao despeja catalogo
MAX_CONTEUDO = 200_000    # corta arquivo gigante antes do regex
VALIDADE_CACHE = 7 * 86400


def carrega() -> list[dict]:
    """Le gatilhos.tsv. Linha quebrada e ignorada — hook nunca derruba o turno."""
    regras = []
    try:
        linhas = TABELA.read_text(encoding="utf-8").splitlines()
    except OSError:
        return regras
    for linha in linhas:
        if linha.startswith("#") or not linha.strip():
            continue
        partes = linha.split("\t")
        if len(partes) != 4:
            continue
        agente, classe, condicao, deteccao = partes
        if deteccao.strip() == "-":
            continue  # condicao objetiva, mas declarada pelo agente: nao ha o que detectar
        alvos, minimo = [], 0
        for tok in deteccao.split(";;"):
            tipo, _, rx = tok.partition(":")
            if tipo == "grande":
                try:
                    minimo = int(rx)
                except ValueError:
                    pass
                continue
            if tipo not in ("path", "novo", "texto", "doc", "cmd"):
                continue
            try:
                # comando e case-sensitive (dig != DIG); caminho e conteudo nao
                alvos.append((tipo, re.compile(rx, 0 if tipo == "cmd" else re.I | re.S)))
            except re.error:
                continue
        if alvos:
            regras.append({"agente": agente, "classe": classe, "condicao": condicao,
                           "alvos": alvos, "minimo": minimo})
    return regras


def arquivo_estado(sid: str) -> pathlib.Path:
    seguro = re.sub(r"[^A-Za-z0-9_-]", "", sid or "sem-sessao")[:64] or "sem-sessao"
    return CACHE / f"{seguro}.json"


def le_estado(caminho: pathlib.Path) -> dict:
    try:
        d = json.loads(caminho.read_text(encoding="utf-8"))
        return {"consultados": list(d.get("consultados", [])),
                "pendentes": dict(d.get("pendentes", {})),
                "avisados": list(d.get("avisados", []))}
    except Exception:
        return {"consultados": [], "pendentes": {}, "avisados": []}


def grava_estado(caminho: pathlib.Path, estado: dict) -> None:
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        caminho.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
        agora = time.time()
        for velho in CACHE.glob("*.json"):
            if agora - velho.stat().st_mtime > VALIDADE_CACHE:
                velho.unlink(missing_ok=True)
    except OSError:
        pass


def relativo(caminho: str) -> str:
    if not caminho:
        return ""
    try:
        return str(pathlib.Path(caminho).resolve().relative_to(RAIZ))
    except Exception:
        return caminho


def texto_escrito(entrada: dict) -> str:
    """Conteudo que o Edit/Write acabou de gravar — o que precisa ser classificado."""
    pedacos = [entrada.get("content") or "", entrada.get("new_string") or ""]
    for e in entrada.get("edits") or []:
        if isinstance(e, dict):
            pedacos.append(e.get("new_string") or "")
    return "\n".join(p for p in pedacos if p)[:MAX_CONTEUDO]


def linhas_do_arquivo(rel: str) -> int:
    try:
        with open(RAIZ / rel, "rb") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


DOC_EXT = (".md", ".markdown", ".txt", ".html", ".htm", ".csv", ".log")


def eh_documento(rel: str) -> bool:
    """Documento (ou arquivo fora do repo): so o `doc:` se aplica, nunca o `texto:`."""
    return (not rel or rel.startswith("/") or rel.startswith("docs/")
            or rel.lower().endswith(DOC_EXT))


def comandos(linha: str) -> list[str]:
    """Quebra a linha de comando em comandos simples, respeitando aspas, sem heredoc."""
    # remove corpo de heredoc: <<'EOF' ... EOF
    linha = re.sub(r"<<-?\s*(['\"]?)(\w+)\1(.*?)\n.*?\n\s*\2\s*(\n|$)", r"\3\n", linha,
                   flags=re.S)
    partes, atual, aspa, i = [], [], "", 0
    while i < len(linha):
        c = linha[i]
        if aspa:
            if c == aspa:
                aspa = ""
            atual.append(c)
        elif c in "'\"":
            aspa = c
            atual.append(c)
        elif c in ";|&\n" or linha.startswith("$(", i) or c == "`":
            partes.append("".join(atual))
            atual = []
            if linha.startswith("$(", i):
                i += 1
        else:
            atual.append(c)
        i += 1
    partes.append("".join(atual))
    limpos = []
    for p in partes:
        p = p.strip().lstrip("(").strip()
        # tira prefixo que nao e o comando: VAR=valor, sudo, time, env, timeout N, cd x
        while True:
            novo = re.sub(r"^(\w+=\S*\s+|sudo\s+|time\s+|env\s+|timeout\s+\S+\s+)", "", p)
            if novo == p:
                break
            p = novo
        if p:
            limpos.append(p)
    return limpos


def casa(regra: dict, ferramenta: str, rel: str, conteudo: str, comando: str) -> bool:
    achou = False
    doc = eh_documento(rel)
    cmds = comandos(comando) if comando else []
    for tipo, rx in regra["alvos"]:
        if tipo == "path" and rel and rx.search(rel):
            achou = True
        elif tipo == "novo" and ferramenta == "Write" and rel and rx.search(rel):
            achou = True
        elif tipo == "texto" and conteudo and not doc and rx.search(conteudo):
            achou = True
        elif tipo == "doc" and conteudo and doc and rx.search(conteudo):
            achou = True
        elif tipo == "cmd" and any(rx.match(c) for c in cmds):
            achou = True
        if achou:
            break
    if not achou:
        return False
    if regra["minimo"] and linhas_do_arquivo(rel) <= regra["minimo"]:
        return False
    return True


def diretiva(itens: list[tuple[str, str, str]]) -> str:
    linhas = [f"  {ag} ({cl}): {cond}" for ag, cl, cond in itens]
    return (
        "GATILHO DE ESPECIALISTA — artefato produzido, consulta ainda nao feita:\n"
        + "\n".join(linhas) + "\n"
        "Chame o(s) agente(s) acima ANTES de o artefato sair (entregar, executar ou fechar a "
        "etapa) — fan-out na MESMA mensagem, passando o CAMINHO do arquivo, nunca o conteudo. "
        "O especialista e insumo da etapa: nao dispensa gate nenhum.\n"
        "Registre em UMA linha por especialista: `<agente> · OK|Ajustar|Bloqueante · ponto · "
        "onde foi acatado` — no `_processo-revisoes.md` INTERNO da pasta do card (nunca no "
        "documento oficial: fluxo, analise, plano.html e evidencias.html nao citam agente — "
        "frota/regras.md § 11), ou no chat, se for pedido avulso. Nao se aplica? Uma linha "
        "dizendo por que.\n"
        "Se voce e subagente e nao tem a ferramenta `Agent`, nao tente chamar: declare no seu "
        "retorno de 15 linhas `gatilho pendente: <classe>` e o orquestrador chama.\n"
        "Tabela completa: `.cursor/scripts/frota.sh gatilhos`"
    )


def emite(evento: str, texto: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": evento, "additionalContext": texto}}))
    sys.exit(0)


def main() -> int:
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0

    nome_evento = ev.get("hook_event_name", "")
    caminho_estado = arquivo_estado(ev.get("session_id", ""))
    estado = le_estado(caminho_estado)

    if nome_evento == "Stop":
        # Stop so chega ao modelo por decision:block — additionalContext no Stop e descartado
        # (transcript grava hook_success com content vazio). stop_hook_active evita laco.
        if ev.get("stop_hook_active"):
            return 0
        pendentes = {k: v for k, v in estado["pendentes"].items()
                     if k not in estado["consultados"]}
        if not pendentes:
            return 0
        itens = [(ag, cl, cond) for ag, (cl, cond) in list(pendentes.items())[:MAX_POR_MENSAGEM]]
        # cobra uma vez por turno encerrado, nao a cada Stop: o resto sai do pendente
        estado["pendentes"] = {}
        grava_estado(caminho_estado, estado)
        print(json.dumps({"decision": "block", "reason": diretiva(itens) + "\n(Turno "
                          "encerrando com gatilho aberto — resolva ou registre o motivo em uma "
                          "linha antes de entregar.)"}, ensure_ascii=False))
        return 0

    ferramenta = ev.get("tool_name", "")
    entrada = ev.get("tool_input") or {}

    if ferramenta in ("Agent", "Task"):
        sub = (entrada.get("subagent_type") or "").strip()
        if sub and sub not in estado["consultados"]:
            estado["consultados"].append(sub)
            estado["pendentes"].pop(sub, None)
            grava_estado(caminho_estado, estado)
        return 0

    rel = relativo(entrada.get("file_path", ""))
    conteudo = texto_escrito(entrada) if ferramenta in ("Edit", "Write", "MultiEdit",
                                                        "NotebookEdit") else ""
    comando = entrada.get("command", "") if ferramenta == "Bash" else ""
    if not rel and not conteudo and not comando:
        return 0

    # o proprio Brain nao dispara gatilho de produto: editar .cursor/ e engenharia de harness
    if rel.startswith(".cursor/") or rel == "AGENTS.md":
        conteudo = ""

    novos = []
    for regra in carrega():
        ag = regra["agente"]
        if ag in estado["consultados"] or ag in estado["avisados"] or any(n[0] == ag for n in novos):
            continue  # agente que absorveu várias classes (Fase 3) é cobrado uma vez só
        if casa(regra, ferramenta, rel, conteudo, comando):
            novos.append((ag, regra["classe"], regra["condicao"]))

    if not novos:
        return 0

    novos = novos[:MAX_POR_MENSAGEM]
    for ag, cl, cond in novos:
        estado["avisados"].append(ag)
        estado["pendentes"][ag] = [cl, cond]
    grava_estado(caminho_estado, estado)
    emite("PostToolUse", diretiva(novos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
