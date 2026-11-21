#!/usr/bin/env python3
"""Empacota o Brain como plugin distribuivel para os outros repositorios Solides.

O que viaja: frota de agentes, comandos, scripts e hooks — a parte *generica*.
O que NAO viaja: mapas `dominio-*` (conhecimento de um repo so) e os perfis de
ambiente. Cada repo tem os seus.

Os agentes do cit carregam fatos especificos deste repositorio (porta, banco,
catch-all de rota, bind mount). Na versao do plugin essas secoes sao removidas e
substituidas por um apontamento ao perfil local — senao o plugin espalha a
configuracao do cit para repos onde ela e falsa.

Uso: gerar_plugin.py [destino]     (default: ~/solides-brain-plugin)

O destino fica FORA de `.cursor/` de proposito: o plugin e artefato gerado, e artefato
gerado dentro da pasta de configuracao passa a parecer uma segunda fonte de verdade.
A fonte e `.cursor/agents`, `.cursor/commands`, `.cursor/scripts` e `.cursor/frota`.
"""
import json
import pathlib
import re
import shutil
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[2]
VERSAO = "1.0.0"

# Secoes inteiras que sao especificas do cit e nao devem viajar
SECOES_LOCAIS = [
    "## Fatos do cit que evitam retrabalho",
    "## Armadilha estrutural deste repositório",
    "## Cuidados que este repositório cobra caro",
]

# Trechos com fato local -> versao generica
SUBSTITUICOES = [
    # (trecho literal do cit, versao generica) — literal, nao regex: markdown escapa mal
    ("Atenção: no cit o banco é **`solides-pipedrive`** e a senha do root é **vazia** "
     "(o perfil ainda diz `homol_cit`, está desatualizado). Confirme com `SHOW TABLES`, não presuma.",
     "Confirme banco, porta e credenciais **no perfil do projeto** e valide com `SHOW TABLES` — "
     "perfis desatualizam, não presuma."),
    ("`.cursor/arquitetura/ambiente-local-cit.md`",
     "`.cursor/arquitetura/ambiente-local-{projeto}.md`"),
    ("**Valide MySQL** — `127.0.0.1:3309`.", "**Valide MySQL** — host e porta do perfil."),
    ("Se o app não subir, verifique os patches locais em `~/patches-locais-cit/` — o patch do "
     "`index.php` (dotenv opcional) é **obrigatório** para o app subir.",
     "Se o app não subir, verifique os patches locais descritos em "
     "`alteracoes-ambiente-local-{projeto}.md`."),
    ("5. Depois de editar: **`docker cp` para o container** — editar no host não reflete. "
     "Sem isso, seu teste valida o código antigo.",
     "5. Confira no perfil se o código é bind mount. Quando **não** é, copie para o container "
     "antes de testar — sem isso o teste valida o código antigo."),
    ("Lembre-o de que o código precisa de `docker cp` para o container antes de qualquer teste.",
     "Lembre-o de conferir no perfil se o código precisa ser copiado para o container antes de testar."),
    ("**Antes de rodar local:** confirme que o código foi copiado para o container "
     "(`docker cp`). Testar o container com código velho é a falha mais comum e a mais "
     "enganosa — passa quando deveria falhar, ou o contrário.",
     "**Antes de rodar local:** confirme que o container tem o código atual. Testar container "
     "com código velho é a falha mais enganosa que existe — passa quando deveria falhar, ou o contrário."),
    ("5. Para dado ao vivo de homol, o MySQL `:3309` **não serve** — é dump congelado. "
     "Use o endpoint `/homologacao/execucao-controlada`.",
     "5. Confirme no perfil qual é a fonte de dado **ao vivo** de homologação — pode não ser o "
     "mesmo banco que você usa localmente."),
    # --- Fase 3 (25/09/2026): fatos do cit que entraram nos agentes fundidos
    ("Dado ao vivo de homol: o endpoint\n   `/homologacao/execucao-controlada` (o MySQL `:3309` é dump congelado).",
     "Dado ao vivo de homol: a fonte\n   que o perfil do projeto indica (pode não ser o banco local)."),
    ("- Título de card não é diagnóstico (\"erro de ganho farmer\" já foi fluxo Mid com `origin = NULL`):\n"
     "  confirme o roteamento pelo registro concreto.",
     "- Título de card não é diagnóstico: confirme o roteamento pelo registro concreto antes de\n"
     "  aceitar a premissa do card."),
    ("O MCP `hubspot` aponta para o portal **sandbox** 23737834 (produção é outro).",
     "Confira no perfil para qual portal o MCP `hubspot` aponta (sandbox ou produção)."),
    ("Rota nova no CodeIgniter: declare antes da catch-all `termo-aceite/{token}`; rota pública passa\n"
     "também pela whitelist do `SessionHook` (`gatilho pendente: exposicao`).",
     "Rota nova: declare antes de qualquer rota catch-all; rota pública passa também pela lista de\n"
     "liberação do hook de sessão, se houver (`gatilho pendente: exposicao`)."),
    ("confira `config/routes.php` **e** a whitelist do `SessionHook` (skill `dominio-superficie-publica`)",
     "confira o arquivo de rotas **e** a lista de liberação do hook de sessão"),
    ("303 para `/` = rota fora da whitelist do `SessionHook`",
     "3xx para `/` = rota barrada pelo hook de sessão"),
    ("O CIT não tem design system: siga o estilo do arquivo vizinho, sem componente novo.",
     "Sem design system no repo, siga o estilo do arquivo vizinho, sem componente novo."),
    ("No CIT a\ndocumentação de API está instalada e desligada (swagger-php 2.x usa `@SWG\\`, spec de fábrica, rota\n"
     "comentada): antes de gerar spec, leve ao usuário as opções da skill `documentacao-api-swagger`.",
     "Antes de gerar\nspec, confira o estado real da documentação de API do repo (ferramental instalado, spec\n"
     "servido, rota da UI) e leve as opções ao usuário."),
    ("- **Rotas** — atenção: `termo-aceite/{token}` é **catch-all**; rota nova vai **antes** "
     "dela em `routes.php`, senão nunca é alcançada.",
     "- **Rotas** — cheque se há rota catch-all no caminho: rota nova precisa ser declarada "
     "**antes** dela, senão nunca é alcançada."),
    ("- Não presuma `status` como filtro de estado — em `termo_aceite` a maioria é `NULL`. "
     "Filtre por `data_aceite IS NOT NULL`.",
     "- Não presuma coluna de `status` como filtro de estado: neste tipo de base a maioria "
     "costuma ser `NULL`. Confirme a distribuição real no banco antes de filtrar."),
    ("- **Código não é bind mount:** o plano tem que prever `docker cp` antes de qualquer teste local.",
     "- Se o código não for bind mount (veja o perfil), o plano precisa prever a cópia para o "
     "container antes de qualquer teste local."),
    ("Crie, no formato do `dominio-termo-aceite`.",
     "Crie um, seguindo o formato dos mapas já existentes no repositório."),
    ("`~/.cursor/projects/-var-www-html-cit/memory/`", "o diretório de memória do projeto"),
    # gatilhos.tsv: o regex de deteccao cita coisa que so existe no cit — homol.sh (script
    # que nao viaja) e CMOVIMENTOS (tabela do CRM). Regex morto nao quebra o hook, mas ensina
    # o repo destino a procurar o artefato errado.
    ("cmd:(\\bmysql\\b|homol\\.sh\\s+(select|update))", "cmd:(\\bmysql\\b|\\bpsql\\b)"),
    ("CMOVIMENTOS|mensalidade|estorno|reembolso", "mensalidade|estorno|reembolso"),
]

MANIFESTO_AGENTES = None  # todos


def limpar(texto):
    """Remove secoes locais e generaliza trechos com fato especifico."""
    tocado = []
    for titulo in SECOES_LOCAIS:
        # da linha do titulo ate o proximo cabecalho de mesmo nivel
        padrao = re.compile(r"\n" + re.escape(titulo) + r"\n.*?(?=\n## )", re.S)
        if padrao.search(texto):
            texto = padrao.sub("\n", texto)
            tocado.append(titulo)
    for antigo, novo in SUBSTITUICOES:
        if antigo in texto:
            texto = texto.replace(antigo, novo)
            tocado.append(antigo[:40].replace("\n", " ") + "…")
    return texto, tocado


def main():
    destino = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path.home() / "solides-brain-plugin"
    if destino.exists():
        shutil.rmtree(destino)
    plug = destino / "solides-brain"
    for sub in ("agents", "commands", "scripts", ".cursor-plugin", "hooks"):
        (plug / sub).mkdir(parents=True, exist_ok=True)
    (destino / ".cursor-plugin").mkdir(parents=True, exist_ok=True)

    # ---- agentes (generalizados)
    print("agentes:")
    for src in sorted((RAIZ / ".cursor/agents").glob("*.md")):
        texto, tocado = limpar(src.read_text())
        (plug / "agents" / src.name).write_text(texto)
        marca = "  generalizado: " + "; ".join(tocado) if tocado else ""
        print(f"  {src.name}{marca}")

    # ---- comandos
    for src in sorted((RAIZ / ".cursor/commands").glob("*.md")):
        texto, tocado = limpar(src.read_text())   # comandos tambem carregam fato local
        (plug / "commands" / src.name).write_text(texto)
        if tocado:
            print(f"  comando {src.name} generalizado: {'; '.join(tocado)}")
    print(f"comandos: {len(list((plug / 'commands').glob('*.md')))}")

    # ---- scripts do Brain
    # homol.sh NAO entra: o endpoint de execucao controlada e do CIT; em outro repo a
    # fonte de dado ao vivo de homologacao e outra, e um script que aponta para o host
    # errado e pior que script ausente.
    SCRIPTS = ["kb.sh", "ancoras.py", "hook_dominio.py", "hook_gatilhos.py",
               "brain_status.sh",
               "fase.sh", "hook_contexto.py", "hook_card.py", "resumo_testes.sh", "cache_validacao.py",
               "frota.sh", "mcp.sh", "propagar.sh"]
    levados = []
    for nome in SCRIPTS:
        src = RAIZ / ".cursor/scripts" / nome
        if src.is_file():
            shutil.copy2(src, plug / "scripts" / nome)
            levados.append(nome)
    print(f"scripts: {', '.join(levados)}")

    # ---- frota: regras compartilhadas + agrupamento (o rodape dos agentes aponta para elas)
    (plug / "frota").mkdir(parents=True, exist_ok=True)
    for nome in ("regras.md", "grupos.tsv", "README.md", "gatilhos.tsv", "gatilhos.md"):
        src = RAIZ / ".cursor/frota" / nome
        if src.is_file():
            texto, _ = limpar(src.read_text())
            (plug / "frota" / nome).write_text(texto)
    print(f"frota: {len(list((plug / 'frota').iterdir()))} arquivos")

    # ---- hooks do plugin (caminhos via CURSOR_PLUGIN_ROOT)
    root = "${CURSOR_PLUGIN_ROOT}"
    hooks = {
        "version": 1,
        "hooks": {
            "beforeSubmitPrompt": [{"command": f'python3 "{root}/scripts/hook_card.py"'}],
            "sessionStart": [{"command": f'python3 "{root}/scripts/hook_dominio.py"'}],
            "postToolUse": [
                {"matcher": "Write", "command": f'python3 "{root}/scripts/hook_dominio.py"'},
                {"matcher": "Write", "command": f'python3 "{root}/scripts/hook_gatilhos.py"'},
                {"matcher": "Shell", "command": f'python3 "{root}/scripts/hook_gatilhos.py"'},
                {"matcher": "Task", "command": f'python3 "{root}/scripts/hook_gatilhos.py"'},
            ],
            "stop": [
                {"command": f'python3 "{root}/scripts/hook_dominio.py"'},
                {"command": f'python3 "{root}/scripts/hook_gatilhos.py"'},
                {"command": f'python3 "{root}/scripts/hook_card.py"'},
            ],
        },
    }
    (plug / "hooks/hooks.json").write_text(json.dumps(hooks, indent=2, ensure_ascii=False) + "\n")

    # ---- manifesto do plugin
    (plug / ".cursor-plugin/plugin.json").write_text(json.dumps({
        "name": "solides-brain",
        "description": ("Brain Solides: frota de agentes de funcao unica (uma etapa do fluxo "
                        "por agente), comandos de despacho, recall do acervo e autocorrecao "
                        "de ancoras arquivo:linha nos mapas de dominio."),
        "version": VERSAO,
        "author": {"name": "Luiz Gustavo Finotello", "email": "luiz.finotello@solides.com.br"},
        "keywords": ["solides", "sustentacao", "agentes", "dominio"],
    }, indent=2, ensure_ascii=False) + "\n")

    # ---- marketplace
    (destino / ".cursor-plugin/marketplace.json").write_text(json.dumps({
        "name": "solides",
        "owner": {"name": "Luiz Gustavo Finotello", "email": "luiz.finotello@solides.com.br"},
        "plugins": [{"name": "solides-brain", "source": "./solides-brain",
                     "description": "Frota de agentes + recall + autocorrecao de ancoras."}],
    }, indent=2, ensure_ascii=False) + "\n")

    # ---- README de instalacao (contagens vindas do disco, nunca escritas a mao)
    n_agentes = len(list((plug / "agents").glob("*.md")))
    n_comandos = len(list((plug / "commands").glob("*.md")))
    n_fluxo = sum(1 for l in (RAIZ / ".cursor/frota/grupos.tsv").read_text().splitlines()
                  if l.startswith("fluxo\t"))
    (destino / "README.md").write_text(f"""# solides-brain — plugin

Frota de agentes de funcao unica, comandos de despacho, recall do acervo e autocorrecao das
ancoras `arquivo:linha` dos mapas de dominio. Versao {VERSAO}.

## Instalar em outro repositorio Solides

```
/plugin marketplace add {destino}
/plugin install solides-brain
```

## O que vem no plugin

| Componente | Conteudo |
|---|---|
| `agents/` | {n_agentes} agentes — {n_fluxo} de etapa do fluxo (com gate) + {n_agentes - n_fluxo} especialistas sob demanda |
| `commands/` | {n_comandos} comandos de despacho — `/card`, `/ambiente`, `/fluxo`, `/analise`, `/plano`, `/dev`, `/testar`, `/evidencias`, `/destilar`, `/brain`, `/kb`... |
| `scripts/` | `kb.sh` (recall), `ancoras.py` (autocorrecao), `hook_dominio.py` (reflexos), `brain_status.sh` (diagnostico) e os scripts de fase/teste/cache |
| `frota/` | `regras.md` (regras invioraveis, fonte unica), `grupos.tsv`, `gatilhos.tsv` + `gatilhos.md` (gatilho por artefato) e o catalogo |
| `hooks/` | `PostToolUse[Edit\\|Write\\|MultiEdit\\|NotebookEdit / Bash / Agent]`, `SessionStart`, `Stop` — marcam e cobram a atualizacao do conhecimento e o **gatilho de especialista por artefato** |

## O que NAO vem (e por que)

- **Mapas `dominio-*`** — conhecimento de um repositorio nao vale em outro. Crie os do repo com
  o `destilador-dominio` e trave as ancoras com `kb.sh ancorar`.
- **Perfis de ambiente** (`ambiente-local-*`, `estado-projeto-*`) — cada repo tem porta, banco e
  URL proprios. Os agentes do plugin **apontam** para o perfil local em vez de embutir valores.
- **AGENTS.md** — o nucleo cita a frota, mas gates e regras de cada repo continuam do repo.

## Depois de instalar

1. `/brain` — confirma frota, hooks e conhecimento.
2. `kb.sh indice` — gera `docs/INDICE.md` do acervo local.
3. Primeiro card do tema: `destilador-dominio` cria o mapa; `kb.sh ancorar` trava as ancoras.

## Regenerar o plugin

Os agentes do cit sao a fonte. Depois de edita-los:

```
python3 .cursor/scripts/gerar_plugin.py
```

O gerador remove as secoes especificas do cit e generaliza os trechos com fato local — a lista
do que foi generalizado sai no stdout, para conferencia.
""")

    n = sum(1 for x in destino.rglob("*") if x.is_file())
    print(f"\nplugin gerado em {destino} ({n} arquivos)")
    print(f"instalar:  /plugin marketplace add {destino}")
    print( "           /plugin install solides-brain")


if __name__ == "__main__":
    main()
