#!/usr/bin/env python3
"""Card da SESSAO — aba unica por card e destilacao obrigatoria, sem depender de memoria.

Duas regras do usuario (25/09/2026) viram reflexo deterministico aqui:

  A. ABA UNICA POR CARD e obrigatoria. Quando a mensagem do usuario (ou `fase.sh <etapa> <card>`)
     cita um card diferente do card ativo DESTA sessao, o agente recebe a ordem de alertar e
     aguardar decisao. A mensagem nao e bloqueada.
  B. DESTILACAO A CADA CARD. Card sem registro de destilacao e cobrado: ao trocar de card, ao
     chegar em etapa de encerramento (S6A-VAL, S6A-PC, I11, I13-PC, I14, I15) e antes de pedir
     /clear (este ultimo pelo hook_contexto.py, que importa daqui).

Marcador de destilacao (fonte unica): `docs/destilacoes/<card>.md` — criado pelo `/destilar`
com o que foi para os mapas `dominio-*`, ou "nada novo: <motivo>". Existe = destilado.

Estado por sessao (nunca por repo — duas abas abertas nao se contaminam):
  .cursor/cache/sessao/<session_id>.json  {card, fase, faixa, cards, cobrados}
A sessao vem do `session_id` do payload do hook; no Bash (fase.sh), de CLAUDE_CODE_SESSION_ID.

Heuristica de numero de card (6 digitos) — so conta se vier em forma de card, para nao
confundir CNPJ parcial, id de banco ou valor:
  "card 167697" · "card #167697" · "cards 167697" · "#167697" · "/card 167697" ·
  ".../_workitems/edit/167697" · numero isolado ABRINDO a mensagem ("167697 ta travado").
Nao conta: 6 digitos soltos no meio do texto, digitos colados em ponto/barra/hifen
(CNPJ, data, versao), numero dentro de <task-notification>. Primeiro digito 1-9.

Eventos (.cursor/settings.json): UserPromptSubmit e Stop.
CLI (usado por fase.sh):  hook_card.py fase <ETAPA> [card] [--trilha curta|completa] · mostra · limpa
Trilha (Fase 3): declarada no B0 e guardada por card na sessao; sem declaracao vale "completa".
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
CACHE = RAIZ / ".cursor/cache/sessao"
DESTILACOES = RAIZ / "docs/destilacoes"
VALIDADE_CACHE = 30 * 86400

# Orcamento unico da aba do card (modelo opus[1m]). Corte de excecao = 130% do orcamento.
ORCAMENTO = 300_000

# etapa -> (bloco, corte de excecao). FONTE UNICA: fase.sh e hook_contexto.py leem daqui.
_B = {
    "c0l0": ("C0+L0", "pós-L0"),
    "sus": ("sustentação S1–S6", "pós-S4"),
    "plano": ("plano I1–I4", "pós-I2-val"),
    "cod": ("código I5–I9", "pós-I7"),
    "local": ("local I10–I11", "pós-I10"),
    "homol": ("homol I12–I15", "pós-I13"),
}
BLOCOS = {e: _B["c0l0"] for e in ("C0", "L0", "B0")}
BLOCOS.update({e: _B["sus"] for e in ("S1", "S2", "S3", "S3-REV", "S4", "S5", "S6", "S6A",
                                       "S6A-VAL", "S6A-PC", "S6B")})
BLOCOS.update({e: _B["plano"] for e in ("PRE-I1", "I1", "I1-REV", "I2", "I2-HTML", "I2-VAL",
                                         "I3", "I4")})
BLOCOS.update({e: _B["cod"] for e in ("I5", "I6", "I6-REV", "I7", "I8", "I9")})
BLOCOS.update({e: _B["local"] for e in ("I10", "I11")})
BLOCOS.update({e: _B["homol"] for e in ("I12", "I13", "I13-PC", "I14", "I15")})

# etapas em que o card pode encerrar — destilacao passa a ser cobrada no Stop
ENCERRAMENTO = {"S6A-VAL", "S6A-PC", "S6B", "I11", "I13-PC", "I14", "I15"}

_CARD_RX = [
    re.compile(r"\bcards?\s*(?:n[ºo°.]?\s*)?#?\s*([1-9]\d{5})(?![\d./-])", re.I),
    re.compile(r"(?<![\w&])#([1-9]\d{5})(?![\d./-])"),
    re.compile(r"_workitems/edit/([1-9]\d{5})\b"),
    re.compile(r"^\s*([1-9]\d{5})(?![\d./-])"),
]


TRILHAS = ("curta", "completa")


def trilha_de(d: dict) -> str:
    return d.get("trilhas", {}).get(d.get("card", ""), "") or "completa (não declarada)"


def rotulo(etapa: str) -> str:
    bloco, corte = BLOCOS.get(etapa, ("não declarado", "—"))
    return (f"{ORCAMENTO // 1000}k · aba única do card · bloco {bloco} "
            f"(corte de exceção: {corte})")


def card_citado(texto: str) -> str:
    """Primeiro numero de card citado em forma de card, ou ''."""
    if not texto:
        return ""
    texto = re.sub(r"<task-notification>.*?</task-notification>", " ", texto, flags=re.S)
    melhor = None
    for rx in _CARD_RX:
        m = rx.search(texto)
        if m and (melhor is None or m.start() < melhor[0]):
            melhor = (m.start(), m.group(1))
    return melhor[1] if melhor else ""


def destilado(card: str) -> bool:
    return bool(card) and (DESTILACOES / f"{card}.md").is_file()


def _arquivo(sid: str) -> pathlib.Path:
    seguro = re.sub(r"[^A-Za-z0-9_-]", "", sid or "")[:64] or "sem-sessao"
    return CACHE / f"{seguro}.json"


def le(sid: str) -> dict:
    try:
        d = json.loads(_arquivo(sid).read_text(encoding="utf-8"))
    except Exception:
        d = {}
    d.setdefault("card", "")
    d.setdefault("fase", "")
    d.setdefault("faixa", 0)
    d.setdefault("cards", [])
    d.setdefault("cobrados", [])
    d.setdefault("trilhas", {})   # card -> "curta" | "completa" (declarada no B0)
    return d


def grava(sid: str, d: dict) -> None:
    try:
        CACHE.mkdir(parents=True, exist_ok=True)
        d["atualizado"] = int(time.time())
        _arquivo(sid).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        agora = time.time()
        for velho in CACHE.glob("*.json"):
            if agora - velho.stat().st_mtime > VALIDADE_CACHE:
                velho.unlink(missing_ok=True)
    except OSError:
        pass


def cobranca_destilacao(card: str) -> str:
    return (f"DESTILAÇÃO PENDENTE do card {card}: rode `/destilar {card}` (kb.sh verificar + "
            f"destilador-dominio) — ele grava `docs/destilacoes/{card}.md` com o que foi para os "
            "mapas dominio-* ou 'nada novo: <motivo>'. Card que para no meio também destila.")


def troca(d: dict, novo: str) -> str:
    """Registra o card novo na sessao e devolve o alerta, se houve troca."""
    antigo = d.get("card", "")
    if novo in d["cards"]:
        d["cards"].remove(novo)
    d["cards"].append(novo)
    d["card"] = novo
    if not antigo or antigo == novo:
        return ""
    d["fase"] = ""
    alerta = (f"TROCA DE CARD NA MESMA ABA: a sessão estava no card {antigo} e agora cita o "
              f"{novo}. Regra obrigatória: ABA ÚNICA POR CARD. Na PRIMEIRA linha da resposta, "
              f"alerte o usuário: \"Você mudou do card {antigo} para o {novo} nesta aba — a "
              f"regra é aba única por card; abra uma aba nova para o {novo}"
              + ("" if destilado(antigo) else f" (e destile o {antigo} antes)")
              + ".\" Depois AGUARDE a decisão dele; não comece trabalho do "
              f"{novo} nesta resposta.")
    if not destilado(antigo):
        alerta += "\n" + cobranca_destilacao(antigo)
    return alerta


def emite(evento: str, texto: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": evento, "additionalContext": texto}}, ensure_ascii=False))


def hook() -> int:
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    sid = ev.get("session_id", "")
    nome = ev.get("hook_event_name", "")
    d = le(sid)

    if nome == "UserPromptSubmit":
        novo = card_citado(ev.get("prompt", ""))
        if not novo:
            return 0
        alerta = troca(d, novo)
        grava(sid, d)
        if alerta:
            emite("UserPromptSubmit", alerta)
        return 0

    if nome == "Stop":
        # Stop so chega ao modelo por decision:block (additionalContext e descartado no Stop).
        # stop_hook_active = ja estamos continuando por causa de um Stop: nunca em laco.
        if ev.get("stop_hook_active"):
            return 0
        card, fase = d.get("card", ""), d.get("fase", "")
        chave = f"{card}:{fase}"
        if not card or fase not in ENCERRAMENTO or destilado(card) or chave in d["cobrados"]:
            return 0
        d["cobrados"].append(chave)
        grava(sid, d)
        print(json.dumps({"decision": "block", "reason": (
            f"Card {card} chegou à etapa de encerramento {fase} sem destilação registrada. "
            + cobranca_destilacao(card)
            + " Se o usuário já decidiu adiar, registre isso em uma linha e encerre.")},
            ensure_ascii=False))
        return 0
    return 0


def cli(args: list[str]) -> int:
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or ""
    d = le(sid)
    acao = args[0] if args else "mostra"
    if acao == "limpa":
        d["fase"] = ""
        grava(sid, d)
        print(f"Fase limpa nesta sessão — medidor no padrão de {ORCAMENTO // 1000}k.")
        return 0
    if acao == "mostra":
        if d["fase"]:
            print(f"Card {d['card'] or '(não declarado)'} · trilha {trilha_de(d)} · fase "
                  f"{d['fase']} — orçamento {rotulo(d['fase'])}")
        else:
            print(f"Nenhuma fase declarada nesta sessão — padrão de {ORCAMENTO // 1000}k.")
        return 0
    if acao == "fase" and len(args) >= 2:
        trilha = ""
        if "--trilha" in args:
            i = args.index("--trilha")
            trilha = (args[i + 1] if i + 1 < len(args) else "").lower()
            args = args[:i] + args[i + 2:]
            if trilha not in TRILHAS:
                print(f"trilha inválida: {trilha or '(vazia)'} (válidas: curta, completa)",
                      file=sys.stderr)
                return 2
        etapa = args[1].upper()
        if etapa not in BLOCOS:
            print(f"etapa inválida: {etapa} (válidas: {' '.join(BLOCOS)})", file=sys.stderr)
            return 2
        alerta = ""
        if len(args) >= 3:
            card = args[2].lstrip("#")
            if not re.fullmatch(r"[1-9]\d{5}", card):
                print(f"card inválido: {card} (6 dígitos)", file=sys.stderr)
                return 2
            alerta = troca(d, card)
        d["fase"] = etapa
        if trilha:
            if not d["card"]:
                print("--trilha exige o card: fase.sh B0 <card> --trilha <t>", file=sys.stderr)
                return 2
            d["trilhas"][d["card"]] = trilha
        grava(sid, d)
        print(f"Card {d['card'] or '(não declarado)'} · trilha {trilha_de(d)} · fase {etapa} — "
              f"orçamento {rotulo(etapa)}")
        if not sid:
            print("aviso: sem CLAUDE_CODE_SESSION_ID — fase gravada fora de sessão", file=sys.stderr)
        if alerta:
            print("\n" + alerta)
        if etapa in ENCERRAMENTO and d["card"] and not destilado(d["card"]):
            print("\n" + cobranca_destilacao(d["card"]))
        return 0
    print("uso: hook_card.py fase <ETAPA> [card] [--trilha curta|completa] | mostra | limpa",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(cli(sys.argv[1:]) if len(sys.argv) > 1 else hook())
