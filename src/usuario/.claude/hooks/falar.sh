#!/usr/bin/env python3
"""Hook Stop — fala em voz alta a resposta final do Claude Code.

100% local: piper (binario em ~/.local/opt/piper, voz pt_BR-cadu) -> ganho_audio.py -> aplay.
Nada de audio ou texto sai da maquina por este caminho.

Desligar sem mexer em configuracao:  touch ~/.claude/voz-off
Religar:                             rm ~/.claude/voz-off
Falar mais/menos texto:              export CLAUDE_VOZ_MAX_CHARS=2400 (padrão 1600)
Mais devagar / mais rapido:          export CLAUDE_VOZ_LENGTH=0.95 (padrão 0.86)
Voz mais grave / mais aguda:         export CLAUDE_VOZ_TOM=21600 (padrão 22400, 22050 = tom do modelo)
Voz mais alta / mais baixa:          export CLAUDE_VOZ_GANHO=2.6 (padrão 2.0, 1.0 desliga)
Fala mais firme / mais variada:      export CLAUDE_VOZ_NOISE_W=0.75 (padrão 0.88)

Registrado em ~/.claude/settings.json como hook Stop com "async": true —
nao bloqueia a conversa e nao consome token.
"""
import json
import os
import re
import subprocess
import sys

HOME = os.path.expanduser("~")
PIPER = os.path.join(HOME, ".local/opt/piper/piper")
MODELO = os.path.join(HOME, ".local/share/piper-voices/pt_BR-cadu-medium.onnx")
DESLIGADO = os.path.join(HOME, ".claude/voz-off")
PIDFILE = os.path.join(HOME, ".claude/voz.pid")
MAX_CHARS = int(os.environ.get("CLAUDE_VOZ_MAX_CHARS", "1600"))
GANHO = os.path.join(HOME, ".claude/hooks/ganho_audio.py")

# O modelo gera a 22050 Hz. Reproduzir um pouco abaixo baixa o tom (voz mais grave)
# e alonga o audio na mesma proporcao — length_scale abaixo de 1 devolve o tempo.
# 22400 fica 1,6% ACIMA dos 22050 do modelo: tom levemente mais fino e fala mais rapida.
SAMPLE_RATE = os.environ.get("CLAUDE_VOZ_TOM", "22400")

# Cadencia e prosodia. length_scale > 1 fala mais devagar; noise_w e noise_scale
# baixos deixam a fala mais firme (menos tremida), altos mais variada.
# Nenhum deles muda o sotaque — sotaque e do dataset do modelo.
LENGTH_SCALE = os.environ.get("CLAUDE_VOZ_LENGTH", "0.86")
NOISE_W = os.environ.get("CLAUDE_VOZ_NOISE_W", "0.88")
NOISE_SCALE = os.environ.get("CLAUDE_VOZ_NOISE", "0.70")
SILENCIO_FRASE = os.environ.get("CLAUDE_VOZ_PAUSA", "0.18")


def limpar(texto):
    """Tira do texto o que nao se le em voz alta."""
    t = texto
    t = re.sub(r"```.*?```", " ", t, flags=re.S)          # bloco de codigo
    t = re.sub(r"^\s*\|.*$", "", t, flags=re.M)           # linha de tabela
    t = re.sub(r"^\s*[-=*_]{3,}\s*$", "", t, flags=re.M)  # regua horizontal
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)           # imagem
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)        # link -> texto
    t = re.sub(r"`([^`]*)`", r"\1", t)                    # codigo inline
    t = re.sub(r"^\s{0,3}#{1,6}\s*", "", t, flags=re.M)   # titulo
    t = re.sub(r"^\s*>\s?", "", t, flags=re.M)            # citacao
    t = re.sub(r"^\s*[-*+]\s+", "", t, flags=re.M)        # marcador de lista
    t = re.sub(r"(\*\*|__|~~|\*|_)", "", t)               # enfase
    t = re.sub(r"[─-╿▀-▟]", " ", t)   # box drawing
    t = re.sub(r"\s+[—–]\s+", ", ", t)              # travessao -> pausa curta de aposto
    t = re.sub(r"[^\S\n]+", " ", t)
    t = re.sub(r"\n{2,}", ". ", t)
    t = t.replace("\n", ". ")
    t = re.sub(r"(\. ){2,}", ". ", t)
    return t.strip()


def cortar(texto, limite):
    """Corta no fim de frase mais proximo do limite."""
    if len(texto) <= limite:
        return texto
    corte = texto[:limite]
    fim = max(corte.rfind(". "), corte.rfind("! "), corte.rfind("? "))
    return (corte[: fim + 1] if fim > limite // 3 else corte).strip()


def matar_fala_anterior():
    """Resposta nova cala a anterior — senao duas vozes falam juntas."""
    try:
        with open(PIDFILE) as f:
            pgid = int(f.read().strip())
        os.killpg(pgid, 15)
    except (OSError, ValueError):
        pass


def main():
    if os.path.exists(DESLIGADO):
        return 0
    if not (os.path.exists(PIPER) and os.path.exists(MODELO)):
        return 0

    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    # Subagente nao narra: quem fala e a resposta do contexto principal.
    if evento.get("agent_id") or evento.get("agent_type"):
        return 0

    texto = cortar(limpar(evento.get("last_assistant_message") or ""), MAX_CHARS)
    if len(texto) < 3:
        return 0

    matar_fala_anterior()
    # Um unico grupo de processos (piper | ganho | aplay) para poder calar depois.
    cano = (
        '"%s" --model "%s" --length_scale %s --noise_w %s --noise_scale %s'
        " --sentence_silence %s --output_raw 2>/dev/null"
        ' | python3 "%s" 2>/dev/null'
        " | aplay -q -r %s -f S16_LE -t raw - >/dev/null 2>&1"
    ) % (PIPER, MODELO, LENGTH_SCALE, NOISE_W, NOISE_SCALE, SILENCIO_FRASE,
         GANHO, SAMPLE_RATE)
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
        fala.communicate(texto.encode("utf-8"), timeout=180)
    except subprocess.TimeoutExpired:
        matar_fala_anterior()
    return 0


if __name__ == "__main__":
    sys.exit(main())
