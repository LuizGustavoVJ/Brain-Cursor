#!/usr/bin/env python3
"""Envia notificação por e-mail (SMTP) e Slack (webhook), ignorando canais não configurados."""
from __future__ import annotations

import json
import os
import smtplib
import ssl
import sys
import urllib.error
import urllib.request
from email.message import EmailMessage


def send_email(subject: str, body: str) -> bool:
    server = os.environ.get("SMTP_SERVER", "").strip()
    port_s = os.environ.get("SMTP_PORT", "587").strip()
    user = os.environ.get("SMTP_USERNAME", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    to_addr = os.environ.get("NOTIFY_EMAIL_TO", "").strip()
    from_addr = os.environ.get("SMTP_FROM", user).strip()

    if not all([server, user, password, to_addr, from_addr]):
        print("E-mail: secrets SMTP incompletos — ignorado.", file=sys.stderr)
        return False

    port = int(port_s)
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(server, port, timeout=60) as smtp:
        smtp.starttls(context=context)
        smtp.login(user, password)
        smtp.send_message(msg)
    print("E-mail enviado para", to_addr)
    return True


def send_slack(subject: str, body: str) -> bool:
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        print("Slack: SLACK_WEBHOOK_URL ausente — ignorado.", file=sys.stderr)
        return False
    text = f"{subject}\n\n{body}"
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        print(f"Slack falhou: HTTP {e.code}", file=sys.stderr)
        return False
    print("Slack notificado.")
    return True


def main() -> int:
    if len(sys.argv) < 3:
        print("Uso: send_notification.py <assunto> <corpo>", file=sys.stderr)
        return 2
    subject = sys.argv[1]
    body = sys.argv[2]
    send_email(subject, body)
    send_slack(subject, body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())