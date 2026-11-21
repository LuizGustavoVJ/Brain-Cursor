#!/usr/bin/env python3
"""Hook PreToolUse — narra em voz alta, em uma frase curta, o passo que vai executar.

Objetivo: conversa em vez de silencio ate a resposta final. Regras que evitam
o efeito tagarela:
  - nao enfileira: se ja tem voz tocando, este passo passa calado;
  - intervalo minimo entre narracoes (CLAUDE_NARRA_INTERVALO, padrao 7 s);
  - nao repete a frase anterior;
  - subagente nao narra (senao varias etapas falam ao mesmo tempo).

Para Bash a frase e a propria `description` da chamada — texto que o modelo ja
escreve em portugues. Para as outras ferramentas, um molde por tipo.

Desligar so a narracao:  touch ~/.cursor/voz-narracao-off
Desligar toda a voz:     touch ~/.cursor/voz-off
"""
import json
import os
import random
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
PIPER = os.path.join(HOME, ".local/opt/piper/piper")
MODELO = os.path.join(HOME, ".local/share/piper-voices/pt_BR-cadu-medium.onnx")
GANHO = os.path.join(HOME, ".cursor/hooks/ganho_audio.py")
DESLIGADO = os.path.join(HOME, ".cursor/voz-off")
DESLIGADO_NARRA = os.path.join(HOME, ".cursor/voz-narracao-off")
PIDFILE = os.path.join(HOME, ".cursor/voz.pid")
ESTADO = os.path.join(HOME, ".cursor/voz-narracao.state")

INTERVALO = float(os.environ.get("CLAUDE_NARRA_INTERVALO", "7"))
MAX_CHARS = 110
# Um pouco mais rapida e mais baixa que a resposta final: e comentario, nao conclusao.
LENGTH_SCALE = os.environ.get("CLAUDE_NARRA_LENGTH", "0.82")
GANHO_NARRA = os.environ.get("CLAUDE_NARRA_GANHO", "1.6")
TOM = os.environ.get("CLAUDE_VOZ_TOM", "22400")

# Só interjeição: "vou"/"deixa eu" quebravam a concordância com descrição no
# gerúndio ("vou conferindo os arquivos").
ABERTURAS = ("", "", "", "", "beleza, ", "certo, ")


def base(caminho):
    return os.path.basename(str(caminho).rstrip("/")) or str(caminho)


def frase(tool, inp):
    """Uma linha curta em portugues para o passo que vem — ou None para ficar calado."""
    if tool == "Bash":
        d = (inp.get("description") or "").strip()
        return d if d else None
    if tool == "Read":
        return random.choice(("lendo ", "abrindo ", "dando uma olhada em ")) + base(inp.get("file_path"))
    if tool in ("Edit", "NotebookEdit"):
        return "mexendo em " + base(inp.get("file_path"))
    if tool == "Write":
        return "escrevendo " + base(inp.get("file_path"))
    if tool == "Grep":
        return "procurando " + str(inp.get("pattern", ""))[:40]
    if tool == "Glob":
        return "listando arquivos"
    if tool == "Agent":
        alvo = inp.get("subagent_type") or "especialista"
        return "chamando o agente %s: %s" % (alvo, (inp.get("description") or "").strip())
    if tool == "Skill":
        return "carregando a skill " + str(inp.get("skill", ""))
    if tool == "WebSearch":
        return "pesquisando na web: " + str(inp.get("query", ""))[:60]
    if tool == "WebFetch":
        url = str(inp.get("url", ""))
        return "abrindo " + url.split("//")[-1].split("/")[0]
    if tool == "Workflow":
        return "rodando um workflow"
    if tool.startswith("mcp__azure-devops"):
        return "consultando o card no Azure"
    if tool.startswith("mcp__gitlab"):
        return "olhando o GitLab"
    if tool.startswith("mcp__playwright"):
        return "mexendo no navegador"
    if tool.startswith("mcp__"):
        return "consultando " + tool.split("__")[1].replace("-", " ")
    return None


def tem_voz_tocando():
    """Nao empilhar fala: se o grupo anterior ainda existe, este passo fica calado."""
    try:
        with open(PIDFILE) as f:
            pgid = int(f.read().strip())
        os.killpg(pgid, 0)
        return True
    except (OSError, ValueError):
        return False


def cedo_demais(texto, agora):
    try:
        with open(ESTADO) as f:
            st = json.load(f)
    except (OSError, ValueError):
        return False
    if agora - float(st.get("t", 0)) < INTERVALO:
        return True
    return st.get("frase") == texto


def main():
    if os.path.exists(DESLIGADO) or os.path.exists(DESLIGADO_NARRA):
        return 0
    if not (os.path.exists(PIPER) and os.path.exists(MODELO)):
        return 0
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if evento.get("agent_id") or evento.get("agent_type"):
        return 0

    texto = frase(evento.get("tool_name") or "", evento.get("tool_input") or {})
    if not texto or len(texto.strip()) < 4:
        return 0
    texto = random.choice(ABERTURAS) + texto.strip()
    texto = texto[:MAX_CHARS].rstrip(" ,.;:") + "."

    agora = time.time()
    if tem_voz_tocando() or cedo_demais(texto, agora):
        return 0
    try:
        with open(ESTADO, "w") as f:
            json.dump({"t": agora, "frase": texto}, f)
    except OSError:
        pass

    cano = (
        '"%s" --model "%s" --length_scale %s --noise_w 0.88 --noise_scale 0.70'
        " --sentence_silence 0.12 --output_raw 2>/dev/null"
        ' | CLAUDE_VOZ_GANHO=%s python3 "%s" 2>/dev/null'
        " | aplay -q -r %s -f S16_LE -t raw - >/dev/null 2>&1"
    ) % (PIPER, MODELO, LENGTH_SCALE, GANHO_NARRA, GANHO, TOM)
    fala = subprocess.Popen(
        ["sh", "-c", cano], stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        cwd=os.path.dirname(PIPER), start_new_session=True,
    )
    try:
        with open(PIDFILE, "w") as f:
            f.write(str(os.getpgid(fala.pid)))
    except OSError:
        pass
    try:
        fala.communicate(texto.encode("utf-8"), timeout=30)
    except subprocess.TimeoutExpired:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
