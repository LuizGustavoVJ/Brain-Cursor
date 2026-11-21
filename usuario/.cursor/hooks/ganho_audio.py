#!/usr/bin/env python3
"""Ganho com saturacao suave para a fala do piper (stdin -> stdout, S16_LE mono).

O piper entrega picos no limite da escala e corpo de fala fraco (RMS medido em
~10% do fundo de escala). Ganho linear so distorceria os picos; aqui a curva
tanh multiplica o corpo e comprime o pico, deixando a voz mais alta e firme
sem estalo. Sem numpy nem sox — a maquina nao tem nenhum dos dois.

Ganho:  export cursor_VOZ_GANHO=2.6   (padrao 2.0; 1.0 desliga)
"""
import array
import math
import os
import sys

LIMITE = 32767
GANHO = float(os.environ.get("cursor_VOZ_GANHO", "2.0"))
PASSO = 8  # tabela de 4096 entradas cobre a escala inteira


def tabela(ganho):
    """Curva de transferencia pre-calculada — tanh por amostra seria lento em Python."""
    escala = LIMITE / math.tanh(ganho) if ganho > 0 else 1.0
    return [
        int(escala * math.tanh(ganho * (i * PASSO) / LIMITE))
        for i in range(LIMITE // PASSO + 2)
    ]


def main():
    entrada, saida = sys.stdin.buffer, sys.stdout.buffer
    if GANHO == 1.0:
        while True:
            bloco = entrada.read(8192)
            if not bloco:
                return 0
            saida.write(bloco)
            saida.flush()

    curva = tabela(GANHO)
    resto = b""
    while True:
        bloco = entrada.read(8192)
        if not bloco:
            break
        dados = resto + bloco
        corte = len(dados) - (len(dados) % 2)
        resto = dados[corte:]
        amostras = array.array("h")
        amostras.frombytes(dados[:corte])
        if sys.byteorder == "big":
            amostras.byteswap()
        for i, v in enumerate(amostras):
            if v >= 0:
                amostras[i] = curva[v // PASSO]
            else:
                amostras[i] = -curva[(-v) // PASSO]
        if sys.byteorder == "big":
            amostras.byteswap()
        saida.write(amostras.tobytes())
        saida.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
