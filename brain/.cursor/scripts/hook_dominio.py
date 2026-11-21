#!/usr/bin/env python3
"""Reflexos do Brain — mantem os mapas de dominio honestos sem depender da
memoria do agente.

Tres eventos, tres funcoes:

  PostToolUse[Edit|Write]  editou arquivo que algum mapa cita? marca o mapa como sujo
  SessionStart             existe mapa sujo? avisa antes da primeira palavra do agente
  Stop                     card encerrado com mapa sujo? cobra a destilacao

O ponto do desenho: o agente nao precisa *lembrar* de atualizar o conhecimento.
O gatilho e deterministico, entao o esquecimento deixa de ser possivel.
"""
import json
import os
import pathlib
import sys

RAIZ = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR")
                   or pathlib.Path(__file__).resolve().parents[2]).resolve()
LOCK_DIR = RAIZ / ".claude/cache/ancoras"
SUJOS = RAIZ / ".claude/cache/dominios-sujos"


def saida(evento, texto):
    if texto:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": evento, "additionalContext": texto}}))
    sys.exit(0)


def mapas_que_citam(rel):
    """Quais mapas de dominio dependem deste arquivo."""
    achados = []
    for lock in LOCK_DIR.glob("*.tsv"):
        for linha in lock.read_text().splitlines():
            if linha.startswith(("#", "")) and rel in linha.split("\t")[0]:
                achados.append(lock.stem)
                break
    return achados


def ler_sujos():
    if not SUJOS.is_file():
        return []
    return [l for l in SUJOS.read_text().splitlines() if l.strip()]


def marcar(nomes):
    atuais = set(ler_sujos())
    novos = atuais | set(nomes)
    if novos != atuais:
        SUJOS.parent.mkdir(parents=True, exist_ok=True)
        SUJOS.write_text("\n".join(sorted(novos)) + "\n")


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    nome = ev.get("hook_event_name", "")

    if nome == "PostToolUse":
        caminho = (ev.get("tool_input") or {}).get("file_path", "")
        if not caminho:
            sys.exit(0)
        try:
            rel = str(pathlib.Path(caminho).resolve().relative_to(RAIZ))
        except Exception:
            sys.exit(0)
        # editar o proprio mapa nao o suja
        if rel.startswith(".claude/"):
            sys.exit(0)
        afetados = mapas_que_citam(rel)
        if not afetados:
            sys.exit(0)
        marcar(afetados)
        saida("PostToolUse",
              f"MAPA DE DOMINIO AFETADO: {rel} e citado por {', '.join(afetados)}. "
              "Ao encerrar o card, rode `.claude/scripts/kb.sh verificar` (corrige as "
              "ancoras que moveram) e acione o subagente `destilador-dominio` para "
              "registrar o que mudou. Nao encerre deixando o mapa mentindo.")

    if nome == "SessionStart":
        sujos = ler_sujos()
        if not sujos:
            sys.exit(0)
        saida("SessionStart",
              f"BRAIN: mapa(s) de dominio pendente(s) de reverificacao: {', '.join(sujos)}. "
              "Antes de confiar em qualquer ancora `arquivo:linha` deles, rode "
              "`.claude/scripts/kb.sh verificar`.")

    if nome == "Stop":
        sujos = ler_sujos()
        if not sujos:
            sys.exit(0)
        saida("Stop",
              f"BRAIN: {', '.join(sujos)} continua(m) sujo(s). Se o card acabou, a "
              "destilacao faz parte do encerramento: `kb.sh verificar` + subagente "
              "`destilador-dominio`. Depois limpe com `kb.sh limpar-sujos`.")

    sys.exit(0)


if __name__ == "__main__":
    main()
