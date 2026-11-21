#!/usr/bin/env python3
"""Verificador de ancoras dos mapas de dominio.

O problema: um mapa de dominio afirma "GanhoMidLib.php:372". O codigo evolui, a
linha 372 passa a ser outra coisa, e o mapa mente sem avisar ninguem.

A solucao, sem LLM: guardar a *linha em si* como assinatura. Na verificacao,
se o numero nao aponta mais para o texto original, procuramos esse texto no
arquivo e corrigimos o numero no mapa.

Cobre ancora de linha (#L123) e de faixa (#L123-L145). Na faixa, o inicio e a
identidade da afirmacao e o fim acompanha: fim de bloco ("});", "}") repete
dezenas de vezes no mesmo arquivo, entao a assinatura sozinha nao decide --
desempata a proximidade da posicao esperada, e o relatorio marca com "?" toda
ancora resolvida assim, para nunca corrigir no escuro.

  lock       grava a assinatura de cada ancora (texto da linha apontada)
  verificar  confere e CORRIGE os numeros que moveram; reporta o resto

Uso:
  ancoras.py lock [mapa...]
  ancoras.py verificar [--dry-run] [mapa...]
"""
import base64
import os
import pathlib
import re
import sys

RAIZ = pathlib.Path(os.environ.get("CURSOR_PROJECT_DIR")
                   or pathlib.Path(__file__).resolve().parents[2]).resolve()
LOCK_DIR = RAIZ / ".cursor/cache/ancoras"
MAPAS_DIR = RAIZ / ".cursor/skills"

# [label](caminho/arquivo.php#L123)  ou  [label](caminho/arquivo.php#L123-L145)
LINK = re.compile(r"\[([^\]]*)\]\((?!https?:)([^)#\s]+)#L(\d+)(?:-L(\d+))?\)")


def norm(s):
    """Assinatura de uma linha: conteudo sem espacamento variavel."""
    return " ".join(s.split())


def enc(s):
    return base64.b64encode(s.encode()).decode()


def dec(s):
    return base64.b64decode(s.encode()).decode()


def resolver(caminho):
    """Resolve o caminho da ancora contra a raiz do repo."""
    p = (RAIZ / caminho.lstrip("./")).resolve()
    try:
        p.relative_to(RAIZ)
    except ValueError:
        return None
    return p if p.is_file() else None


def linhas_de(arq):
    return arq.read_text(errors="replace").splitlines()


def mapas(argv):
    if argv:
        return [pathlib.Path(a).resolve() for a in argv]
    return sorted(MAPAS_DIR.glob("dominio-*/SKILL.md"))


def ancoras_de(mapa):
    """Devolve (nlinha_no_mapa, label, caminho, ini, fim) de cada ancora.

    fim e None quando a ancora aponta uma linha unica.
    """
    for i, linha in enumerate(mapa.read_text().splitlines(), 1):
        for m in LINK.finditer(linha):
            fim = int(m.group(4)) if m.group(4) else None
            yield i, m.group(1), m.group(2), int(m.group(3)), fim


def cmd_lock(argv):
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    for mapa in mapas(argv):
        registros, ausentes, faixas = [], 0, 0
        for _, _, caminho, ini, fim in ancoras_de(mapa):
            arq = resolver(caminho)
            if not arq:
                ausentes += 1
                continue
            ls = linhas_de(arq)
            if not (1 <= ini <= len(ls)):
                ausentes += 1
                continue
            if fim is not None and not (ini <= fim <= len(ls)):
                ausentes += 1
                continue
            sig_f = enc(norm(ls[fim - 1])) if fim is not None else ""
            if fim is not None:
                faixas += 1
            registros.append(
                f"{caminho}\t{ini}\t{fim if fim is not None else ''}\t"
                f"{enc(norm(ls[ini - 1]))}\t{sig_f}")
        lock = LOCK_DIR / (mapa.parent.name + ".tsv")
        lock.write_text("\n".join(sorted(set(registros))) + "\n")
        extra = f" ({faixas} faixas)" if faixas else ""
        print(f"{mapa.parent.name}: {len(set(registros))} ancoras travadas{extra}"
              + (f", {ausentes} sem alvo" if ausentes else ""))


def registros_do_lock(lock):
    """Le o lock. Aceita o formato antigo de 3 campos (so linha unica)."""
    out = []
    for reg in lock.read_text().splitlines():
        if not reg.strip():
            continue
        p = reg.split("\t")
        if len(p) == 3:
            caminho, ini, sig_i = p
            fim, sig_f = "", ""
        elif len(p) == 5:
            caminho, ini, fim, sig_i, sig_f = p
        else:
            continue
        out.append({"caminho": caminho,
                    "ini": int(ini),
                    "fim": int(fim) if fim else None,
                    "sig_i": dec(sig_i),
                    "sig_f": dec(sig_f) if sig_f else None})
    return out


def como_registro(r):
    fim = r["fim"] if r["fim"] is not None else ""
    sig_f = enc(r["sig_f"]) if r["sig_f"] is not None else ""
    return f"{r['caminho']}\t{r['ini']}\t{fim}\t{enc(r['sig_i'])}\t{sig_f}"


def localizar(ls, esperado, alvo, minimo=1):
    """Onde esta hoje a linha cuja assinatura e `esperado`, sabendo que estava em `alvo`.

    Devolve (numero, modo): exato | unico | proximo, ou (None, orfa | ambigua).
    'proximo' = havia varios candidatos identicos e ganhou o mais perto do alvo.
    """
    if minimo <= alvo <= len(ls) and norm(ls[alvo - 1]) == esperado:
        return alvo, "exato"
    cands = [i for i, l in enumerate(ls, 1) if i >= minimo and norm(l) == esperado]
    if not cands:
        return None, "orfa"
    if len(cands) == 1:
        return cands[0], "unico"
    cands.sort(key=lambda i: (abs(i - alvo), i))
    if abs(cands[0] - alvo) == abs(cands[1] - alvo):
        return None, "ambigua"
    return cands[0], "proximo"


def troca_no_label(label, pares):
    """Atualiza os numeros repetidos no texto do link (ex.: 'routes.php:85-103')."""
    for k, (antigo, _) in enumerate(pares):
        label = re.sub(rf"(?<!\d){antigo}(?!\d)", f"\x00{k}\x00", label)
    for k, (_, novo) in enumerate(pares):
        label = label.replace(f"\x00{k}\x00", str(novo))
    return label


def aplica_correcoes(texto, correcoes):
    """Reescreve o mapa numa PASSADA UNICA, cada link a partir do numero original.

    Corrigir uma ancora por vez colide: se A vai de 192 para 195 e B ja estava
    em 195, a substituicao de B pegaria as duas e empurraria A junto. Visitando
    cada link uma unica vez, o numero de origem nunca e o resultado de outra
    correcao.
    """
    def sub(m):
        label, cam = m.group(1), m.group(2)
        a = int(m.group(3))
        b = int(m.group(4)) if m.group(4) else None
        alvo_novo = correcoes.get((cam, a, b))
        if alvo_novo is None:
            return m.group(0)
        ini_n, fim_n = alvo_novo
        pares = [(a, ini_n)] + ([(b, fim_n)] if b is not None else [])
        destino = f"{cam}#L{ini_n}" + (f"-L{fim_n}" if b is not None else "")
        return f"[{troca_no_label(label, pares)}]({destino})"
    return LINK.sub(sub, texto)


def rotulo(r):
    return f"{r['caminho']}#L{r['ini']}" + (f"-L{r['fim']}" if r["fim"] is not None else "")


def sem_trava(mapa, regs):
    """Ancoras que estao no mapa mas nao no lock — ninguem as verifica."""
    chaves = {(r["caminho"], r["ini"], r["fim"]) for r in regs}
    fora = []
    for _, _, caminho, ini, fim in ancoras_de(mapa):
        if (caminho, ini, fim) in chaves:
            continue
        motivo = "arquivo nao existe" if not resolver(caminho) else "fora do lock"
        fora.append((caminho, ini, fim, motivo))
    return sorted(set(fora))


def cmd_verificar(argv):
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    total = ok = movidas = aprox = orfas = destravadas = 0
    sujos = []

    for mapa in mapas(argv):
        lock = LOCK_DIR / (mapa.parent.name + ".tsv")
        if not lock.is_file():
            print(f"{mapa.parent.name}: sem lock — rode 'kb.sh ancorar' primeiro")
            continue

        regs = registros_do_lock(lock)
        texto = mapa.read_text()
        alteracoes, novos_regs, correcoes = [], [], {}

        for (caminho, ini, fim, motivo) in sem_trava(mapa, regs):
            destravadas += 1
            faixa = f"-L{fim}" if fim is not None else ""
            print(f"  S/TRAVA {caminho}#L{ini}{faixa} — {motivo}")

        for r in regs:
            total += 1
            arq = resolver(r["caminho"])
            if not arq:
                orfas += 1
                novos_regs.append(r)
                print(f"  ORFA   {rotulo(r)} — arquivo nao existe mais")
                continue

            ls = linhas_de(arq)
            novo_i, modo_i = localizar(ls, r["sig_i"], r["ini"])
            if novo_i is None:
                orfas += 1
                novos_regs.append(r)
                motivo = ("conteudo sumiu do arquivo" if modo_i == "orfa"
                          else "linhas identicas equidistantes, ambiguo")
                print(f"  ORFA   {rotulo(r)} — {motivo}")
                print(f"         esperava: {r['sig_i'][:76]}")
                continue

            novo_f, modo_f, resign = None, "exato", None
            if r["fim"] is not None:
                alvo_f = novo_i + (r["fim"] - r["ini"])
                novo_f, modo_f = localizar(ls, r["sig_f"], alvo_f, minimo=novo_i)
                if novo_f is None:
                    # o fim da faixa mudou de conteudo: preserva o tamanho e re-assina
                    novo_f, modo_f = min(alvo_f, len(ls)), "comprimento"
                    resign = norm(ls[novo_f - 1])

            if novo_i == r["ini"] and novo_f == r["fim"]:
                ok += 1
                novos_regs.append(r)
                continue

            duvidoso = modo_i == "proximo" or modo_f in ("proximo", "comprimento")
            correcoes[(r["caminho"], r["ini"], r["fim"])] = (novo_i, novo_f)
            alteracoes.append((rotulo(r), novo_i, novo_f, r["sig_i"], duvidoso, modo_f))
            movidas += 1
            if duvidoso:
                aprox += 1
            novo = dict(r, ini=novo_i, fim=novo_f)
            if resign is not None:
                novo["sig_f"] = resign
            novos_regs.append(novo)

        if alteracoes:
            sujos.append(mapa.parent.name)
            if not dry:
                mapa.write_text(aplica_correcoes(texto, correcoes))
                lock.write_text("\n".join(sorted(
                    set(como_registro(r) for r in novos_regs))) + "\n")
            for (antes, ni, nf, sig, duvidoso, modo_f) in alteracoes:
                marca = "MOVEU?" if duvidoso else "MOVEU "
                seta = "->" if not dry else "-> (dry)"
                depois = f"L{ni}" + (f"-L{nf}" if nf is not None else "")
                nota = ""
                if modo_f == "proximo":
                    nota = "  (fim por proximidade)"
                elif modo_f == "comprimento":
                    nota = "  (fim mudou; tamanho preservado)"
                print(f"  {marca} {antes} {seta} {depois}  [{sig[:52]}]{nota}")

    resumo = (f"\n{total} ancoras · {ok} ok · {movidas} corrigidas "
              f"· {orfas} orfas")
    if aprox:
        resumo += f" · {aprox} por proximidade (marcadas com ?)"
    if destravadas:
        resumo += f" · {destravadas} sem trava"
    print(resumo)
    if destravadas:
        print("Sem trava = ancora do mapa que ninguem verifica. Rode 'kb.sh ancorar'.")
    if orfas:
        print("Orfa = precisa de decisao humana ou do destilador-dominio: o codigo\n"
              "mudou de forma que nenhuma linha corresponde mais a afirmacao do mapa.")
    if sujos and not dry:
        print("mapas atualizados: " + ", ".join(sujos))
    return 1 if orfas else 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    resto = sys.argv[2:]
    if cmd == "lock":
        cmd_lock(resto)
    elif cmd == "verificar":
        sys.exit(cmd_verificar(resto))
    else:
        print(__doc__)
        sys.exit(2)
