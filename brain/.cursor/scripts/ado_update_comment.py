#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inlina o CSS de um evidencias.html e atualiza/cria um comentário no card ADO.

Uso:
  python3 ado_update_comment.py <html_path> <work_item_id> [comment_id]

- comment_id informado -> PATCH (atualiza o comentário existente).
- comment_id omitido   -> POST  (cria um novo comentário) e imprime o id.
PAT (AZURE_DEVOPS_EXT_PAT) procurado nesta ordem: variavel de ambiente,
~/.claude.json (escopo de usuario) e, por compatibilidade, .mcp.json do repo.
"""
import re, json, base64, sys, os, time, urllib.request, urllib.error, urllib.parse
from html.parser import HTMLParser

ORG = os.environ.get("ADO_ORG", "solidestech")
# Projeto ADO (env ADO_PROJECT): SEMPRE OBRIGATÓRIO. O endpoint de comentários
# (.../<PROJECT>/_apis/wit/workItems/<id>/comments) só existe com o projeto no path;
# sem ele o ADO devolve HTTP 404 ("controller ... was not found"). O embed de <img>
# também exige o GUID na URL. Não há caso "só-texto sem projeto" — é sempre com projeto.
PROJECT = os.environ.get("ADO_PROJECT")
# Onde o PAT pode estar, em ordem de precedência. O escopo de usuário (~/.claude.json)
# é a fonte viva desde 21/08/2026, quando os .mcp.json por repositório foram removidos
# para não repetir o mesmo segredo em nove lugares. Os caminhos de repositório ficam
# na lista só por compatibilidade — se um deles voltar a existir, continua funcionando.
_AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES_PAT = [
    os.path.expanduser("~/.claude.json"),
    os.path.normpath(os.path.join(_AQUI, "..", ".mcp.json")),        # <repo>/.claude/.mcp.json
    os.path.normpath(os.path.join(_AQUI, "..", "..", ".mcp.json")),  # <repo>/.mcp.json
]

# Rede: a saída para dev.azure.com penda conexões novas de vez em quando (SYN
# descartado). Sem timeout o urlopen fica parado indefinidamente e o script morre
# só com Ctrl+C. Timeout + retry com espera crescente resolvem.
NET_TIMEOUT = int(os.environ.get("ADO_TIMEOUT", "45"))
NET_TENTATIVAS = int(os.environ.get("ADO_TENTATIVAS", "4"))

def _open(req):
    """urlopen com timeout e retry. Devolve (status, corpo). HTTPError sobe direto."""
    ultimo = None
    for i in range(NET_TENTATIVAS):
        try:
            with urllib.request.urlopen(req, timeout=NET_TIMEOUT) as r:
                return r.status, r.read()
        except urllib.error.HTTPError:
            raise
        except Exception as e:
            ultimo = e
            if i + 1 < NET_TENTATIVAS:
                espera = 2 * (i + 1)
                sys.stderr.write(f"... rede instável ({type(e).__name__}) em {req.get_method()} "
                                 f"{req.full_url.split('?')[0][-60:]} — nova tentativa em {espera}s "
                                 f"({i + 2}/{NET_TENTATIVAS})\n")
                time.sleep(espera)
    raise ultimo

def _busca_pat(no):
    """Varre o JSON inteiro atrás de AZURE_DEVOPS_EXT_PAT.

    Buscar pela chave, e não pelo caminho fixo mcpServers/azure-devops/env, evita
    que o script quebre de novo se o servidor for renomeado ou aninhado diferente.
    """
    if isinstance(no, dict):
        v = no.get("AZURE_DEVOPS_EXT_PAT")
        if isinstance(v, str) and v.strip():
            return v.strip()
        for filho in no.values():
            achado = _busca_pat(filho)
            if achado:
                return achado
    elif isinstance(no, list):
        for filho in no:
            achado = _busca_pat(filho)
            if achado:
                return achado
    return None


def get_pat():
    for var in ("AZURE_DEVOPS_EXT_PAT", "ADO_PAT"):
        v = os.environ.get(var, "").strip()
        if v:
            return v

    for caminho in FONTES_PAT:
        if not os.path.isfile(caminho):
            continue
        try:
            with open(caminho, encoding="utf-8") as fh:
                dados = json.load(fh)
        except (ValueError, OSError) as e:
            sys.stderr.write(f"... {caminho} existe mas não pôde ser lido ({type(e).__name__}); seguindo\n")
            continue
        pat = _busca_pat(dados)
        if pat:
            return pat

    procurados = "\n  - ".join(FONTES_PAT)
    raise SystemExit(
        "ERRO: PAT do Azure DevOps não encontrado.\n"
        "Defina AZURE_DEVOPS_EXT_PAT no ambiente:\n"
        "  AZURE_DEVOPS_EXT_PAT=<pat> ADO_PROJECT=<guid> python3 " + os.path.basename(__file__) + " <html> <id>\n"
        "ou deixe-o em mcpServers.azure-devops.env.AZURE_DEVOPS_EXT_PAT de um destes arquivos:\n  - "
        + procurados
    )

def inline(html_path):
    src = open(html_path, encoding="utf-8").read()
    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    body = re.search(r"<body>(.*?)</body>", src, re.S).group(1)
    rootm = re.search(r":root\s*\{(.*?)\}", css, re.S)
    vars_ = {}
    if rootm:
        for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", rootm.group(1)):
            vars_[k.strip()] = v.strip()
    def resolve(val):
        def rep(m):
            return vars_.get(m.group(1).strip(), (m.group(2).strip() if m.group(2) else m.group(1)))
        prev = None
        while prev != val:
            prev = val
            val = re.sub(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^\)]+))?\)", rep, val)
        return val
    rules, order = [], 0
    css_clean = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for block in re.finditer(r"([^{}]+)\{([^{}]+)\}", css_clean):
        selectors, props = block.group(1).strip(), block.group(2).strip()
        if selectors.startswith(":root"):
            continue
        props = resolve("; ".join(p.strip() for p in props.split(";") if p.strip()))
        for sel in selectors.split(","):
            sel = sel.strip()
            if not sel or "*" in sel:
                continue
            parts = sel.replace(">", " ").split()
            parsed = []
            for part in parts:
                m = re.match(r"([a-zA-Z0-9]+)?((?:\.[\w-]+)*)$", part)
                if not m:
                    parsed = None
                    break
                parsed.append((m.group(1).lower() if m.group(1) else None,
                               set(re.findall(r"\.([\w-]+)", part))))
            if not parsed:
                continue
            spec = sum(len(c) for _, c in parsed) * 10 + len(parsed)
            rules.append((parsed, props, spec, order)); order += 1
    def mt(part, tag, classes):
        pt, pc = part
        if pt and pt != tag:
            return False
        if pc and not pc.issubset(classes):
            return False
        return True
    def compute(tag, classes, stack):
        app = []
        for parsed, props, spec, ordm in rules:
            if not mt(parsed[-1], tag, classes):
                continue
            anc = parsed[:-1]
            if anc:
                idx = len(stack) - 2; ok = True
                for cond in reversed(anc):
                    found = False
                    while idx >= 0:
                        atag, acls = stack[idx]; idx -= 1
                        if mt(cond, atag, acls):
                            found = True; break
                    if not found:
                        ok = False; break
                if not ok:
                    continue
            app.append((spec, ordm, props))
        app.sort(key=lambda x: (x[0], x[1]))
        return "; ".join(p for _, _, p in app if p)
    VOID = {"br", "img", "hr", "meta", "input"}
    class Inl(HTMLParser):
        def __init__(s):
            super().__init__(convert_charrefs=False); s.out = []; s.stack = []
        def handle_starttag(s, tag, attrs):
            attrs = dict(attrs); classes = set((attrs.get("class") or "").split())
            s.stack.append((tag, classes)); base = compute(tag, classes, s.stack)
            comb = "; ".join(x.strip().rstrip(";") for x in [base, attrs.get("style", "")] if x.strip())
            na = [f'{k}="{v}"' for k, v in attrs.items() if k not in ("class", "style")]
            if comb:
                na.append(f'style="{comb};"')
            s.out.append(f"<{tag}{(' ' + ' '.join(na)) if na else ''}>")
            if tag in VOID:
                s.stack.pop()
        def handle_startendtag(s, tag, attrs):
            s.handle_starttag(tag, attrs)
            if tag not in VOID and s.stack:
                s.stack.pop()
        def handle_endtag(s, tag):
            if tag in VOID:
                return
            if s.stack and s.stack[-1][0] == tag:
                s.stack.pop()
            s.out.append(f"</{tag}>")
        def handle_data(s, d): s.out.append(d)
        def handle_entityref(s, n): s.out.append(f"&{n};")
        def handle_charref(s, n): s.out.append(f"&#{n};")
    p = Inl(); p.feed(body)
    inner = "".join(p.out).strip()
    return ('<div style="font-family:\'Segoe UI\',Calibri,Arial,sans-serif;'
            'font-size:11pt;color:#1a1a1a;line-height:1.45;">' + inner + "</div>")

def _upload_attachment(caminho, auth):
    nome = os.path.basename(caminho)
    with open(caminho, "rb") as f:
        data = f.read()
    url = f"https://dev.azure.com/{ORG}/_apis/wit/attachments?fileName={urllib.parse.quote(nome)}&api-version=7.1"
    req = urllib.request.Request(url, data=data, method="POST",
        headers={"Content-Type": "application/octet-stream", "Authorization": "Basic " + auth})
    return json.loads(_open(req)[1].decode("utf-8"))["url"]

def _vincula_attachment(wid, att_url, nome, auth):
    proj = f"/{PROJECT}" if PROJECT else ""
    url = f"https://dev.azure.com/{ORG}{proj}/_apis/wit/workItems/{wid}?api-version=7.1"
    body = json.dumps([{"op": "add", "path": "/relations/-", "value": {
        "rel": "AttachedFile", "url": att_url, "attributes": {"comment": nome}}}]).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PATCH",
        headers={"Content-Type": "application/json-patch+json", "Authorization": "Basic " + auth})
    _open(req)

def _anexos_do_card(wid, auth):
    """Anexos já vinculados ao work item: {nome: url}. Evita subir de novo o mesmo
    PNG quando o script é reexecutado (cada retentativa duplicava os anexos)."""
    proj = f"/{PROJECT}" if PROJECT else ""
    url = f"https://dev.azure.com/{ORG}{proj}/_apis/wit/workItems/{wid}?$expand=relations&api-version=7.1"
    req = urllib.request.Request(url, headers={"Authorization": "Basic " + auth})
    mapa = {}
    try:
        wi = json.loads(_open(req)[1].decode("utf-8"))
    except Exception as e:
        sys.stderr.write(f"WARN não foi possível listar anexos do card ({e}); todos serão reenviados\n")
        return mapa
    for rel in wi.get("relations") or []:
        if rel.get("rel") != "AttachedFile":
            continue
        at = rel.get("attributes") or {}
        nome = at.get("name") or at.get("comment")
        if nome and nome not in mapa:
            mapa[nome] = rel.get("url", "")
    return mapa

def _processa_imagens(text, html_path, wid, auth):
    """Sobe cada PNG como anexo, vincula ao work item e (com ADO_EMBED != "0",
    padrão) embute a <img> no comentário reescrevendo o src para a URL COM o GUID
    do projeto (.../<PROJECT>/_apis/wit/attachments/<guid>?fileName=...). URL
    org-level (sem GUID do projeto) dá HTTP 400. Flags: ADO_ATTACH=0 não (re)anexa;
    ADO_EMBED=0 anexa mas não embute (imagem só na aba "Anexos" do card)."""
    attach = os.environ.get("ADO_ATTACH", "1") != "0"
    embed = os.environ.get("ADO_EMBED", "1") != "0"
    base = os.path.dirname(os.path.abspath(html_path))
    proj = f"/{PROJECT}" if PROJECT else ""
    existentes = _anexos_do_card(wid, auth) if attach else {}
    if existentes:
        sys.stderr.write(f"... {len(existentes)} anexo(s) já no card serão reaproveitados\n")
    def url_embed(att, nome):
        g = re.search(r"/attachments/([0-9a-fA-F-]{36})", att)
        if PROJECT and g:
            return (f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/attachments/{g.group(1)}"
                    f"?fileName={urllib.parse.quote(nome)}")
        return att
    def rep(m):
        tag = m.group(0)
        ms = re.search(r'src="([^"]+)"', tag)
        if not ms or ms.group(1).startswith("http"):
            return tag if (ms and ms.group(1).startswith("http")) else ""
        src = ms.group(1)
        caminho = os.path.normpath(os.path.join(base, src))
        if not os.path.isfile(caminho):
            return ""
        if not attach:
            return ""
        nome = os.path.basename(caminho)
        try:
            att = existentes.get(nome)
            if not att:
                att = _upload_attachment(caminho, auth)  # url org-level
                _vincula_attachment(wid, att, nome, auth)
                existentes[nome] = att
            if not embed:
                return ""
            # URL com o projeto (formato que o comentário do ADO reconhece p/ renderizar)
            return tag.replace('src="' + src + '"', 'src="' + url_embed(att, nome) + '"')
        except urllib.error.HTTPError as e:
            sys.stderr.write(f"WARN anexo {os.path.basename(caminho)}: HTTP {e.code} {e.read().decode('utf-8')[:200]}\n")
            return ""
        except Exception as e:
            sys.stderr.write(f"WARN anexo {os.path.basename(caminho)}: {e}\n")
            return ""
    return re.sub(r'<img\b[^>]*>', rep, text)

def main():
    if len(sys.argv) < 3:
        print("uso: ado_update_comment.py <html_path> <work_item_id> [comment_id]"); sys.exit(2)
    html_path, wid = sys.argv[1], sys.argv[2]
    cid = sys.argv[3] if len(sys.argv) > 3 else None
    if not PROJECT:
        sys.stderr.write(
            "ERRO: ADO_PROJECT (GUID do projeto) é obrigatório — o endpoint de comentários\n"
            "não existe em nível de organização e o ADO devolve 404 sem ele.\n"
            "Uso correto:\n"
            "  ADO_PROJECT=<guid> python3 " + os.path.basename(__file__) + " <html> <work_item_id> [comment_id]\n")
        sys.exit(2)
    text = inline(html_path)
    auth = base64.b64encode(b":" + get_pat().encode()).decode()
    text = _processa_imagens(text, html_path, wid, auth)
    headers = {"Content-Type": "application/json", "Authorization": "Basic " + auth}
    proj = f"/{PROJECT}"
    apiver = os.environ.get("ADO_APIVER", "7.0-preview.3")
    base = f"https://dev.azure.com/{ORG}{proj}/_apis/wit/workItems/{wid}/comments"
    if cid:
        url = f"{base}/{cid}?api-version={apiver}"; method = "PATCH"
    else:
        url = f"{base}?api-version={apiver}"; method = "POST"
    req = urllib.request.Request(url, data=json.dumps({"text": text}).encode("utf-8"),
                                 method=method, headers=headers)
    try:
        status, body = _open(req)
        resp = json.loads(body.decode("utf-8"))
        print(f"OK HTTP {status} | id={resp.get('id')} version={resp.get('version')} modifiedDate={resp.get('modifiedDate')} format={resp.get('format')} | inline={len(text)} chars")
    except urllib.error.HTTPError as e:
        print("ERRO HTTP", e.code); print(e.read().decode("utf-8")[:600]); sys.exit(1)

if __name__ == "__main__":
    main()
