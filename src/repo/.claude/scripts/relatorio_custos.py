#!/usr/bin/env python3
"""Relatório de custos das sessões Claude Code do projeto atual.

Lê os transcripts JSONL em ~/.claude/projects/{slug}/ e apura, por período:

  * custo estimado por modelo (input, output, cache read, cache write)
  * fatia gasta em subagentes (sidechains) vs agente principal
  * fatia associada ao MCP Playwright e a execuções de teste
  * uso de /compact e /clear
  * revalidações (quantas vezes cada etapa de validação repetiu na mesma sessão)

Uso:
    python3 .claude/scripts/relatorio_custos.py            # últimos 30 dias
    python3 .claude/scripts/relatorio_custos.py --dias 7
    python3 .claude/scripts/relatorio_custos.py --dias 30 --formato json

Preços: USD por milhão de tokens (Anthropic API, 1ª parte).
Cache read = 0,1x input · cache write 5min = 1,25x input · cache write 1h = 2x input.
Atualize PRECOS quando a tabela oficial mudar.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# input USD/MTok por modelo; output derivado da coluna correspondente
PRECOS = {
    "claude-fable-5":   (10.0, 50.0),
    "claude-mythos-5":  (10.0, 50.0),
    "claude-opus-5":    (5.0, 25.0),
    "claude-opus-4-8":  (5.0, 25.0),
    "claude-opus-4-7":  (5.0, 25.0),
    "claude-opus-4-6":  (5.0, 25.0),
    "claude-opus-4-5":  (5.0, 25.0),
    "claude-sonnet-5":  (3.0, 15.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
PRECO_PADRAO = (5.0, 25.0)  # fallback: tarifa Opus

MULT_CACHE_READ = 0.10
MULT_CACHE_WRITE_5M = 1.25
MULT_CACHE_WRITE_1H = 2.00

RE_VALIDACAO = re.compile(
    r"\b(S2|S4|S6a-val|I2|I6|I11|I15)\b.{0,60}?"
    r"(valida|revalida|rodada)", re.IGNORECASE | re.DOTALL
)


def normaliza_modelo(model: str) -> str:
    """`claude-opus-5[1m]` e `claude-haiku-4-5-20251001` -> chave da tabela."""
    m = model.split("[")[0]
    if m in PRECOS:
        return m
    for chave in PRECOS:
        if m.startswith(chave):
            return chave
    return m


def custo(model: str, u: dict) -> float:
    entrada, saida = PRECOS.get(normaliza_modelo(model), PRECO_PADRAO)
    cc = u.get("cache_creation") or {}
    w5 = cc.get("ephemeral_5m_input_tokens", 0)
    w1h = cc.get("ephemeral_1h_input_tokens", 0)
    if not (w5 or w1h):  # transcripts antigos só têm o agregado
        w5 = u.get("cache_creation_input_tokens", 0)
    return (
        u.get("input_tokens", 0) * entrada
        + u.get("output_tokens", 0) * saida
        + u.get("cache_read_input_tokens", 0) * entrada * MULT_CACHE_READ
        + w5 * entrada * MULT_CACHE_WRITE_5M
        + w1h * entrada * MULT_CACHE_WRITE_1H
    ) / 1_000_000


def dir_transcripts(projeto: Path) -> Path:
    slug = str(projeto).replace("/", "-")
    return Path.home() / ".claude" / "projects" / slug


def tipo_subagente(arquivo: Path) -> str:
    """Lê agent-*.meta.json ao lado do transcript para saber qual subagente rodou."""
    meta = arquivo.with_suffix("").with_suffix(".meta.json")
    if not meta.is_file():
        meta = arquivo.parent / (arquivo.stem + ".meta.json")
    try:
        d = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "(desconhecido)"
    for chave in ("subagent_type", "subagentType", "agentType", "type", "name"):
        if d.get(chave):
            return str(d[chave])
    return "(desconhecido)"


def coleta(base: Path, desde: datetime) -> dict:
    r = {
        "por_modelo": defaultdict(lambda: defaultdict(float)),
        "custo_total": 0.0,
        "custo_sidechain": 0.0,
        "custo_principal": 0.0,
        "por_subagente": defaultdict(lambda: defaultdict(float)),
        "ferramentas": defaultdict(int),
        "tokens_playwright": 0,
        "compacts": 0,
        "clears": 0,
        "sessoes": 0,
        "mensagens": 0,
        "validacoes_por_sessao": defaultdict(lambda: defaultdict(int)),
        "arquivos": [],
    }
    if not base.is_dir():
        return r

    # transcripts da sessão principal + transcripts de subagente ({sessao}/subagents/*.jsonl)
    arquivos = sorted(base.glob("*.jsonl")) + sorted(base.glob("*/subagents/*.jsonl"))

    for arquivo in arquivos:
        if datetime.fromtimestamp(arquivo.stat().st_mtime, timezone.utc) < desde:
            continue
        eh_subagente = arquivo.parent.name == "subagents"
        rotulo_sub = tipo_subagente(arquivo) if eh_subagente else None
        if not eh_subagente:
            r["sessoes"] += 1
        r["arquivos"].append(arquivo.name)
        sessao = arquivo.parent.parent.stem if eh_subagente else arquivo.stem
        anterior_playwright = False

        with arquivo.open(encoding="utf-8", errors="replace") as fh:
            for linha in fh:
                try:
                    d = json.loads(linha)
                except json.JSONDecodeError:
                    continue

                ts = d.get("timestamp")
                if ts:
                    try:
                        if datetime.fromisoformat(ts.replace("Z", "+00:00")) < desde:
                            continue
                    except ValueError:
                        pass

                msg = d.get("message")
                if not isinstance(msg, dict):
                    continue

                conteudo = msg.get("content")
                texto = conteudo if isinstance(conteudo, str) else ""
                blocos = conteudo if isinstance(conteudo, list) else []

                if "<command-name>/compact" in texto or d.get("isCompactSummary"):
                    r["compacts"] += 1
                if "<command-name>/clear" in texto:
                    r["clears"] += 1
                for etapa in RE_VALIDACAO.findall(texto):
                    r["validacoes_por_sessao"][sessao][etapa[0].upper()] += 1

                uso = msg.get("usage")
                modelo = msg.get("model")
                if uso and modelo and modelo != "<synthetic>":
                    c = custo(modelo, uso)
                    chave = normaliza_modelo(modelo)
                    m = r["por_modelo"][chave]
                    m["custo"] += c
                    m["input"] += uso.get("input_tokens", 0)
                    m["output"] += uso.get("output_tokens", 0)
                    m["cache_read"] += uso.get("cache_read_input_tokens", 0)
                    m["cache_write"] += uso.get("cache_creation_input_tokens", 0)
                    m["chamadas"] += 1
                    r["custo_total"] += c
                    r["mensagens"] += 1
                    if eh_subagente or d.get("isSidechain"):
                        r["custo_sidechain"] += c
                        s = r["por_subagente"][rotulo_sub or "(sidechain inline)"]
                        s["custo"] += c
                        s["chamadas"] += 1
                        s["modelo_" + chave] = 1
                    else:
                        r["custo_principal"] += c
                    # turno que consumiu resultado de Playwright: atribui o custo
                    if anterior_playwright:
                        r["tokens_playwright"] += uso.get("input_tokens", 0) + \
                            uso.get("cache_creation_input_tokens", 0)
                    anterior_playwright = False

                for b in blocos:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        nome = b.get("name", "?")
                        r["ferramentas"][nome] += 1
                        if nome.startswith("mcp__playwright__"):
                            anterior_playwright = True
    return r


def pct(parte: float, total: float) -> str:
    return f"{(parte / total * 100):.1f}%" if total else "—"


def relatorio_md(r: dict, dias: int) -> str:
    hoje = datetime.now().strftime("%Y-%m-%d")
    total = r["custo_total"]
    L = [
        f"# Relatório de custos — Claude Code · projeto `cit`",
        "",
        f"**Gerado em:** {hoje} · **Janela:** últimos {dias} dias · "
        f"**Sessões:** {r['sessoes']} · **Respostas do modelo:** {r['mensagens']}",
        "",
        f"## 1. Custo estimado total: **US$ {total:.2f}**",
        "",
        "| Modelo | Chamadas | Input | Output | Cache read | Cache write | Custo | % |",
        "|--------|---------:|------:|-------:|-----------:|------------:|------:|--:|",
    ]
    for modelo, m in sorted(r["por_modelo"].items(), key=lambda kv: -kv[1]["custo"]):
        L.append(
            f"| `{modelo}` | {int(m['chamadas'])} | {int(m['input']):,} | "
            f"{int(m['output']):,} | {int(m['cache_read']):,} | {int(m['cache_write']):,} | "
            f"US$ {m['custo']:.2f} | {pct(m['custo'], total)} |"
        )

    L += [
        "",
        "## 2. Onde está o gargalo",
        "",
        "| Origem | Custo | % do total |",
        "|--------|------:|-----------:|",
        f"| Agente principal | US$ {r['custo_principal']:.2f} | {pct(r['custo_principal'], total)} |",
        f"| Subagentes (validações) | US$ {r['custo_sidechain']:.2f} | {pct(r['custo_sidechain'], total)} |",
        "",
    ]
    if r["por_subagente"]:
        L += [
            "### Por tipo de subagente",
            "",
            "| Subagente | Respostas | Modelos | Custo | % do total |",
            "|-----------|----------:|---------|------:|-----------:|",
        ]
        for nome, s in sorted(r["por_subagente"].items(), key=lambda kv: -kv[1]["custo"]):
            modelos = ", ".join(
                f"`{k[7:]}`" for k in sorted(s) if k.startswith("modelo_")
            ) or "—"
            L.append(
                f"| `{nome}` | {int(s['chamadas'])} | {modelos} | "
                f"US$ {s['custo']:.2f} | {pct(s['custo'], total)} |"
            )
        L.append("")

    L += [
        f"Tokens de entrada em turnos logo após chamadas do MCP Playwright: "
        f"**{r['tokens_playwright']:,}**",
        "",
        "## 3. Ferramentas mais usadas",
        "",
        "| Ferramenta | Chamadas |",
        "|------------|---------:|",
    ]
    for nome, n in sorted(r["ferramentas"].items(), key=lambda kv: -kv[1])[:12]:
        L.append(f"| `{nome}` | {n} |")

    playwright = sum(n for f, n in r["ferramentas"].items() if f.startswith("mcp__playwright__"))
    subagentes = r["ferramentas"].get("Agent", 0) + r["ferramentas"].get("Task", 0)

    revalidacoes = {
        s: {e: n for e, n in etapas.items() if n > 1}
        for s, etapas in r["validacoes_por_sessao"].items()
    }
    revalidacoes = {s: e for s, e in revalidacoes.items() if e}

    L += [
        "",
        "## 4. Higiene de contexto",
        "",
        "| Métrica | Valor |",
        "|---------|------:|",
        f"| `/compact` executados | {r['compacts']} |",
        f"| `/clear` executados | {r['clears']} |",
        f"| Subagentes disparados | {subagentes} |",
        f"| Chamadas MCP Playwright | {playwright} |",
        f"| Sessões com revalidação (mesma etapa >1x) | {len(revalidacoes)} |",
        "",
    ]
    if revalidacoes:
        L += ["Etapas revalidadas:", ""]
        for s, etapas in list(revalidacoes.items())[:10]:
            det = ", ".join(f"{e}×{n}" for e, n in sorted(etapas.items()))
            L.append(f"- `{s[:8]}`: {det}")
        L.append("")

    L += [
        "## 5. Leitura e próximo ajuste",
        "",
        "Compare com o alvo da política em [`.claude/otimizacao-custos.md`]"
        "(.claude/otimizacao-custos.md):",
        "",
        f"- **Subagentes** — alvo ≤ 30% do total. Hoje: {pct(r['custo_sidechain'], total)}. "
        "Acima disso: conferir se S2 e o I2-val da trilha curta estão indo para `validador-leve` (Haiku) e se as "
        "validações consolidadas S2-S4 estão sendo usadas.",
        f"- **Playwright** — alvo ≤ 15% do total. {playwright} chamadas MCP na janela. "
        "Acima disso: conferir se I7/I10/I13 estão usando `resumo_testes.sh` e se o MCP está "
        "sendo evitado em C0/L0/S1–S6/I1–I4.",
        f"- **Higiene de contexto** — {r['compacts']} `/compact` e {r['clears']} `/clear` em "
        f"{r['sessoes']} sessões. Menos de 1 `/clear` por sessão indica abas acumulando contexto.",
        f"- **Revalidações** — {len(revalidacoes)} sessões repetiram a mesma etapa de validação. "
        "Muitas repetições: usar o cache (`cache_validacao.py`) e revisar por que o documento "
        "está sendo recusado na primeira rodada.",
        "",
        "---",
        "",
        "> Custos são **estimativas** calculadas a partir dos `usage` gravados nos transcripts "
        "locais, com a tabela de preços em `PRECOS` no topo do script. Não substituem a fatura "
        "do Console. Sessões de outros projetos não entram nesta contagem.",
    ]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="Relatório de custos Claude Code")
    ap.add_argument("--dias", type=int, default=30, help="janela em dias (padrão 30)")
    ap.add_argument("--formato", choices=["md", "json"], default="md")
    ap.add_argument("--projeto", default=os.getcwd(), help="diretório do projeto")
    args = ap.parse_args()

    base = dir_transcripts(Path(args.projeto).resolve())
    desde = datetime.now(timezone.utc) - timedelta(days=args.dias)
    r = coleta(base, desde)

    if not r["sessoes"]:
        print(f"Nenhuma sessão nos últimos {args.dias} dias em {base}", file=sys.stderr)
        return 1

    if args.formato == "json":
        r.pop("validacoes_por_sessao", None)
        print(json.dumps(r, indent=2, default=lambda o: dict(o) if hasattr(o, "keys") else str(o)))
    else:
        print(relatorio_md(r, args.dias))
    return 0


if __name__ == "__main__":
    sys.exit(main())
