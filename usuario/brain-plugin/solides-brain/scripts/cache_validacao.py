#!/usr/bin/env python3
"""Cache de validações de subagente (S2, S4, S6a-val, I2-val, I6, I11, I15) e teto de rodadas.

Evita repagar um subagente quando o documento não mudou desde a última aprovação.
A chave é `sha256(etapa + conteúdo do arquivo)`; o TTL padrão é 1 hora.

Uso:
    # antes de disparar o subagente
    python3 .cursor/scripts/cache_validacao.py check I2-val docs/implementacoes/plano/impl-x.md
      -> "HIT Aprovado 2026-08-05T14:02:11"  (exit 0)  -> reaproveitar, não gastar subagente
      -> "MISS"                              (exit 1)  -> disparar o subagente

    # depois que o subagente respondeu
    python3 .cursor/scripts/cache_validacao.py save I2-val docs/.../impl-x.md Aprovado

    python3 .cursor/scripts/cache_validacao.py limpar     # descarta entradas vencidas

Teto de 3 rodadas por etapa e card (fluxo-completo.md § Teto de 3 rodadas):
    cache_validacao.py rodada I6 167697   -> "Rodada 2 de 3" (vai no prompt do validador)
    cache_validacao.py recusa I6 167697   -> registra a recusa; na 3ª sai com código 3 e
                                             "ESCALAR AO USUÁRIO" — a etapa para
    cache_validacao.py save I6 <arquivo> Aprovado --card 167697   -> grava e zera o contador
Contador em `.cursor/cache/rodadas.json` (gitignorado), por card+etapa, validade de 30 dias.

Cache em `.cursor/cache/validacoes.json` (gitignorado). Só `Aprovado` é reaproveitado —
um `Recusado` sempre força nova rodada, porque o documento vai mudar em seguida.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

TTL_PADRAO = 3600  # 1 hora
ETAPAS = {"S2", "S4", "S2-S4", "S6a-val", "I2-val", "I6", "I11", "I15", "I11+I15"}
ALIAS = {"I2": "I2-val"}   # compat: I2 foi fundido no I2-val (Fase 3, 25/09/2026)
TETO = 3
VALIDADE_RODADAS = 30 * 86400


def normaliza(etapa: str) -> str:
    e = ALIAS.get(etapa.upper(), etapa)
    for valida in ETAPAS:
        if valida.upper() == e.upper():
            return valida
    return e


def caminho_rodadas() -> Path:
    return caminho_cache().parent / "rodadas.json"


def le_rodadas() -> dict:
    try:
        d = json.loads(caminho_rodadas().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        d = {}
    agora = time.time()
    return {k: v for k, v in d.items() if agora - v.get("ts", 0) < VALIDADE_RODADAS}


def grava_rodadas(d: dict) -> None:
    p = caminho_rodadas()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_rodadas(acao: str, etapa: str, card: str) -> int:
    if etapa not in ETAPAS:
        print(f"etapa inválida: {etapa} (esperado: {', '.join(sorted(ETAPAS))})", file=sys.stderr)
        return 2
    d = le_rodadas()
    k = f"{card}:{etapa}"
    recusas = d.get(k, {}).get("recusas", 0)
    if acao == "rodada":
        if recusas >= TETO:
            print(f"ESCALAR AO USUÁRIO — {etapa} do card {card} já teve {recusas} recusas "
                  f"(teto {TETO}). Não há nova rodada sem decisão dele.")
            return 3
        print(f"Rodada {recusas + 1} de {TETO}")
        return 0
    recusas += 1
    d[k] = {"recusas": recusas, "ts": time.time()}
    grava_rodadas(d)
    if recusas >= TETO:
        print(f"ESCALAR AO USUÁRIO — {recusas}ª recusa em {etapa} do card {card}. Pare a etapa e "
              f"leve ao usuário a lista de divergências remanescentes, cada uma com a decisão "
              f"que ela exige.")
        return 3
    print(f"Recusa {recusas} de {TETO} registrada — próxima: Rodada {recusas + 1} de {TETO}")
    return 0


def caminho_cache() -> Path:
    return Path(__file__).resolve().parent.parent / "cache" / "validacoes.json"


def carrega() -> dict:
    p = caminho_cache()
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def grava(dados: dict) -> None:
    p = caminho_cache()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")


def chave(etapa: str, arquivo: Path) -> str:
    h = hashlib.sha256()
    h.update(etapa.encode())
    h.update(b"\0")
    h.update(arquivo.read_bytes())
    return h.hexdigest()


def expira(dados: dict, ttl: int) -> dict:
    agora = time.time()
    return {k: v for k, v in dados.items() if agora - v.get("ts", 0) < ttl}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    acao = sys.argv[1]
    ttl = int(sys.argv[sys.argv.index("--ttl") + 1]) if "--ttl" in sys.argv else TTL_PADRAO
    dados = expira(carrega(), ttl)

    if acao == "limpar":
        grava(dados)
        print(f"OK — {len(dados)} entradas válidas mantidas")
        return 0

    if acao in ("rodada", "recusa"):
        if len(sys.argv) < 4:
            print(f"uso: cache_validacao.py {acao} ETAPA CARD", file=sys.stderr)
            return 2
        return cmd_rodadas(acao, normaliza(sys.argv[2]), sys.argv[3].lstrip("#"))

    card = ""
    if "--card" in sys.argv:
        i = sys.argv.index("--card")
        card = sys.argv[i + 1].lstrip("#") if i + 1 < len(sys.argv) else ""
        del sys.argv[i:i + 2]
    if "--ttl" in sys.argv:
        i = sys.argv.index("--ttl")
        del sys.argv[i:i + 2]

    if len(sys.argv) < 4:
        print("uso: cache_validacao.py {check|save} ETAPA ARQUIVO [STATUS] [--card N] "
              "| {rodada|recusa} ETAPA CARD", file=sys.stderr)
        return 2

    etapa, alvo = normaliza(sys.argv[2]), Path(sys.argv[3])
    if etapa not in ETAPAS:
        print(f"etapa inválida: {etapa} (esperado: {', '.join(sorted(ETAPAS))})", file=sys.stderr)
        return 2
    if not alvo.is_file():
        print(f"arquivo inexistente: {alvo}", file=sys.stderr)
        return 2

    k = chave(etapa, alvo)

    if acao == "check":
        entrada = dados.get(k)
        if entrada and entrada.get("status") == "Aprovado":
            print(f"HIT {entrada['status']} {entrada.get('quando', '?')}")
            grava(dados)
            return 0
        print("MISS")
        grava(dados)
        return 1

    if acao == "save":
        status = sys.argv[4] if len(sys.argv) > 4 else "Aprovado"
        dados[k] = {
            "etapa": etapa,
            "arquivo": str(alvo),
            "status": status,
            "ts": time.time(),
            "quando": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        grava(dados)
        if card and status == "Aprovado":
            r = le_rodadas()
            r.pop(f"{card}:{etapa}", None)
            grava_rodadas(r)
        print(f"OK — {etapa} {status} gravado")
        if card and status == "Recusado":
            return cmd_rodadas("recusa", etapa, card)
        return 0

    print(f"ação desconhecida: {acao}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
