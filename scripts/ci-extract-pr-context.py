#!/usr/bin/env python3
"""Extrai card ADO, título e links a partir de branch e corpo do PR (stdout JSON)."""
from __future__ import annotations

import json
import re
import sys

ADO_URL_RE = re.compile(
    r"https://dev\.azure\.com/[^\s)>]+/_workitems/edit/(?P<id>\d+)", re.I
)
ADO_FIELD_RE = re.compile(
    r"(?im)card\s*ado\s*url[^:\n]*:\s*\**\s*(?P<url>https://\S+)"
)
TITLE_FIELD_RE = re.compile(
    r"(?im)(?:t[ií]tulo|title)\s*(?:do\s*card)?[^:\n]*:\s*\**\s*(?P<t>.+?)\s*$"
)
CARD_BRANCH_RE = re.compile(
    r"(?i)(?:^|/)(?P<bcge>bcge-\d+)(?:[-_/]|$)|(?:^|/)(?P<num>\d{5,})_"
)


def main() -> int:
    branch = sys.argv[1] if len(sys.argv) > 1 else ""
    body = sys.stdin.read() if not sys.stdin.isatty() else (sys.argv[2] if len(sys.argv) > 2 else "")
    pr_number = sys.argv[3] if len(sys.argv) > 3 else ""
    pr_title = sys.argv[4] if len(sys.argv) > 4 else ""
    pr_url = sys.argv[5] if len(sys.argv) > 5 else ""

    card = ""
    m = CARD_BRANCH_RE.search(branch)
    if m:
        card = (m.group("bcge") or m.group("num") or "").upper()

    ado_url = ""
    fm = ADO_FIELD_RE.search(body)
    if fm:
        ado_url = fm.group("url").strip()
    if not ado_url:
        for m in ADO_URL_RE.finditer(body):
            ado_url = m.group(0)
            if not card:
                card = m.group("id")
            break

    title = pr_title
    tm = TITLE_FIELD_RE.search(body)
    if tm:
        title = tm.group("t").strip()

    out = {
        "card": card or "(não identificado na branch — preencha o template do PR)",
        "ado_url": ado_url or "(preencha a URL do card no corpo do PR)",
        "pr_number": pr_number,
        "pr_url": pr_url,
        "pr_title": title,
        "branch": branch,
    }
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())