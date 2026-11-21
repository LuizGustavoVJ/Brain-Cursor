#!/usr/bin/env python3
"""Hook PostToolUse: após I7/I10/I13, lembra de resumir e compactar.

Lê o payload do hook no stdin. Se o Bash executado foi uma suíte de testes
(`test:e2e`, `test:local`, `test:homol`), injeta um lembrete de economia de contexto.
Em qualquer outro caso não emite nada (saída vazia = hook silencioso).

Registrado em .claude/settings.json → hooks.PostToolUse.
Política: .claude/otimizacao-custos.md § Playwright.
"""

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from hook_gatilhos import comandos  # noqa: E402 — mesma quebra de comando do hook de gatilhos

# Precisa ser uma EXECUCAO de suite, nao a mera mencao da string. Casado no INICIO de cada
# comando simples (heredoc removido, aspas respeitadas): `cat > doc.md <<EOF ... resumo_testes.sh
# e2e ... EOF`, `grep "test:e2e"` e `echo 'npm run test:local'` NAO disparam (achado da Fase 2).
ALVOS = re.compile(
    r"(?:npm\s+(?:run\s+)?test:(e2e|local|homol)\b"
    r"|(?:bash\s+|sh\s+)?\S*resumo_testes\.sh\s+(e2e|local|homol)\b"
    r"|(?:npx\s+)?playwright\s+test\b.*--project=(e2e|local|homol)\b)"
)


def execucao(linha: str):
    """Match da suite executada de fato, ou None."""
    for cmd in comandos(linha):
        m = ALVOS.match(cmd)
        if m:
            return m
    return None

LEMBRETE = (
    "ECONOMIA DE CONTEXTO — suíte {alvo} concluída.\n"
    "1. NÃO reproduza o stdout do Playwright no chat nem no documento. Registre apenas: "
    "N/N, tempo total, e a tabela 'Detalhamento dos cenários'.\n"
    "2. Prints: capture apenas o relatório Playwright ({card}-e2e-playwright.png) e os cenários "
    "que a matriz do plano exige — não printe cenário que passou e não está na matriz.\n"
    "3. O medidor de contexto (hook_contexto.py) avisa sozinho se a aba estourou o orçamento — "
    "não repita número de orçamento aqui; se ele pedir /compact, o pedido encerra o turno.\n"
    "Detalhes: .claude/implementacao/testes-resumido.md"
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if payload.get("tool_name", "Bash") != "Bash":
        return 0
    comando = (payload.get("tool_input") or {}).get("command", "")
    m = execucao(comando)
    if not m:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": LEMBRETE.format(
                alvo=next(g for g in m.groups() if g), card="{card-id}"),
        }
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
