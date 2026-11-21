#!/usr/bin/env python3
"""Medidor de contexto — obriga o agente a pedir /compact ou /clear na hora certa.

Lê o payload do hook no stdin, abre o `transcript_path` da sessão, calcula o tamanho REAL
do contexto (input + cache_read + cache_creation da última resposta do modelo) e compara com
o orçamento da fase do fluxo. Se estourou, injeta uma diretiva explícita para o agente
sinalizar ao usuário.

Silencioso abaixo do limiar — o monitor não pode virar custo. Não emite nada quando o
contexto está dentro do orçamento.

Registrado em .cursor/settings.json → hooks.UserPromptSubmit e hooks.PostToolUse.
Política: .cursor/otimizacao-custos.md § 4. Aba única por card (obrigatória).

Limite conhecido: nem o hook nem o agente conseguem EXECUTAR /compact ou /clear — são comandos
do cliente. O que este script garante é que o pedido apareça no momento certo, com o número
medido, em vez de depender da memória do agente.

Regra dura a partir de 130%: pedir /compact ENCERRA o turno do agente. Continuar a tarefa na
mesma resposta anula o efeito — o comando demora do lado do usuário e o agente segue queimando
contexto enquanto ele roda.
"""

from __future__ import annotations

import json
import os
import re
import sys

# Orçamento (tokens) — 300k em TODAS as etapas (modelo opus[1m]): o card inteiro cabe em UMA aba.
# Espelha .cursor/otimizacao-custos.md § 4. A etapa muda só o RÓTULO (bloco + corte de exceção),
# nunca o número. Etapa e card são DECLARADOS por sessão via scripts/fase.sh e lidos do estado
# da SESSÃO (.cursor/cache/sessao/<session_id>.json) — nunca de arquivo único por repo, que
# mostrava a fase de outro card aberto em outra aba. Mapeamento etapa→bloco: hook_card.py.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_card  # noqa: E402

ORCAMENTO_PADRAO = hook_card.ORCAMENTO
FASE_PADRAO = "não declarada (padrão)"

# faixas: 0 dentro · 1 amarelo (≥85%) · 2 laranja (≥130%, corte de exceção) · 3 vermelho (≥200%)
def faixa(contexto: int, limite: int) -> int:
    r = contexto / limite
    return 3 if r >= 2.0 else 2 if r >= 1.3 else 1 if r >= 0.85 else 0


def le_fase(sessao: dict) -> tuple[int, str]:
    etapa = sessao.get("fase", "")
    if etapa in hook_card.BLOCOS:
        card = sessao.get("card") or "não declarado"
        return ORCAMENTO_PADRAO, f"{hook_card.rotulo(etapa)} · card {card} · etapa {etapa}"
    return ORCAMENTO_PADRAO, FASE_PADRAO

# lê só a cauda do transcript — arquivos chegam a 10 MB
CAUDA_BYTES = 400_000


def le_cauda(caminho: str) -> list[str]:
    try:
        tamanho = os.path.getsize(caminho)
        with open(caminho, "rb") as fh:
            if tamanho > CAUDA_BYTES:
                fh.seek(tamanho - CAUDA_BYTES)
                fh.readline()  # descarta a linha truncada
            return fh.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return []


def mede(linhas: list[str]) -> int:
    """Tokens de contexto da última resposta do modelo APÓS a última compactação.

    O /compact grava no transcript um marcador {"type":"system",
    "subtype":"compact_boundary"}, mas NÃO grava usage novo: até o modelo responder
    outra vez, a última linha com usage ainda é a de ANTES da compactação. Medir sem
    cortar nessa fronteira faz o hook repetir o número pré-compact e exigir /compact
    de novo — o usuário compacta, a diretiva reaparece com o mesmo número, e o turno
    nunca destrava. Foi o que ocorreu em 18/08/2026: 202k exigidos com 62k reais.

    Sem nenhum usage depois da fronteira, o contexto novo é DESCONHECIDO: retorna 0
    (hook silencioso), em vez de chutar o valor velho. Usage de subagente
    (isSidechain) também não conta — é outro contexto, não o desta sessão.
    """
    corte = 0
    for i, linha in enumerate(linhas):
        try:
            d = json.loads(linha)
        except (json.JSONDecodeError, ValueError):
            continue
        if d.get("type") == "system" and d.get("subtype") == "compact_boundary":
            corte = i + 1

    for linha in reversed(linhas[corte:]):
        try:
            d = json.loads(linha)
        except (json.JSONDecodeError, ValueError):
            continue
        if d.get("isSidechain"):
            continue
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        u = m.get("usage")
        if u and m.get("model") and m.get("model") != "<synthetic>":
            return (
                u.get("input_tokens", 0)
                + u.get("cache_read_input_tokens", 0)
                + u.get("cache_creation_input_tokens", 0)
            )
    return 0


def diretiva(contexto: int, limite: int, fase: str, pos_teste: bool, card: str = "") -> str:
    k = f"{contexto / 1000:.0f}k"
    lim = f"{limite / 1000:.0f}k"
    excesso = contexto / limite

    if excesso >= 2.0:
        nivel = "🔴 CRÍTICO"
        acao = (
            f"PARE e diga ao usuário, como PRIMEIRA linha da sua resposta:\n"
            f"    ⚠️ Contexto em {k} (orçamento {lim} — {excesso:.1f}× acima). "
            f"Rode `/clear` no corte de exceção deste bloco antes de continuarmos.\n"
            f"Antes disso, entregue em 3–5 linhas o estado atual (etapa concluída, "
            f"arquivos tocados, próximo passo) — é o que sobrevive ao `/clear`. "
            f"Aba única por card é obrigatória: este corte é exceção, não rotina."
        )
        if card and not hook_card.destilado(card):
            acao += "\nANTES de pedir o `/clear`: " + hook_card.cobranca_destilacao(card)
    elif excesso >= 1.3:
        nivel = "🟠 ACIMA DO ORÇAMENTO"
        acao = (
            f"PARE e diga ao usuário, como PRIMEIRA linha da sua resposta:\n"
            f"    ⚠️ Contexto em {k} (orçamento {lim}). Rode `/compact` — aguardo aqui.\n"
            f"ENCERRE O TURNO em seguida: não inicie, não continue e não retome nenhuma "
            f"tarefa nesta resposta. O /compact demora e roda do lado do usuário; seguir "
            f"trabalhando enquanto isso só inflaciona o contexto que se quer reduzir. "
            f"Deixe registrado em 1–2 linhas onde a tarefa parou, para retomar depois."
        )
    else:
        nivel = "🟡 PRÓXIMO DO LIMITE"
        acao = (
            f"Ao concluir a etapa atual, avise em uma linha: "
            f"“contexto em {k} — vale rodar `/compact` antes da próxima etapa”. "
            f"Não interrompa a tarefa em andamento por isso."
        )

    extra = ""
    if pos_teste:
        extra = (
            "\nA suíte de testes acabou de rodar: este é o melhor momento para compactar. "
            "Preserve no resumo: resultado N/N, caminhos dos prints, tabela de cenários. "
            "Descarte: logs, stdout, saída por assertion."
        )

    return (
        f"MEDIDOR DE CONTEXTO — {nivel}\n"
        f"Contexto atual: {k} tokens · Fase: {fase} · Orçamento: {lim}\n"
        f"{acao}{extra}\n"
        f"(Você não consegue executar /compact ou /clear — quem roda é o usuário. "
        f"Sua obrigação é pedir, com o número acima, e AGUARDAR: pedido de /compact ou "
        f"/clear encerra o turno, nunca acompanha trabalho na mesma resposta.)"
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    caminho = payload.get("transcript_path")
    if not caminho:
        return 0

    contexto = mede(le_cauda(caminho))
    if not contexto:
        return 0

    sid = payload.get("session_id", "")
    sessao = hook_card.le(sid)
    limite, fase = le_fase(sessao)

    comando = (payload.get("tool_input") or {}).get("command", "")
    pos_teste = bool(re.search(r"\btest:(e2e|local|homol)\b", comando))

    # Avisa só quando a FAIXA sobe (a cada Bash era ruído: 5.063 avisos, 99% amarelos).
    # Faixa que desce (pós-/compact) é gravada em silêncio, e a próxima subida volta a avisar.
    # Exceção: logo após uma suíte de testes, a partir de 60%, compactar cedo vale a pena.
    atual, anterior = faixa(contexto, limite), int(sessao.get("faixa", 0) or 0)
    if atual != anterior:
        sessao["faixa"] = atual
        hook_card.grava(sid, sessao)
    avisa = atual > anterior or (pos_teste and contexto >= limite * 0.6)
    if not avisa:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": payload.get("hook_event_name", "UserPromptSubmit"),
            "additionalContext": diretiva(contexto, limite, fase, pos_teste, sessao.get("card", "")),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
