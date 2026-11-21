# solides-brain — plugin

Frota de agentes de funcao unica, comandos de despacho, recall do acervo e autocorrecao das
ancoras `arquivo:linha` dos mapas de dominio. Versao 1.0.0.

## Instalar em outro repositorio Solides

```
/plugin marketplace add usuario/brain-plugin
/plugin install solides-brain
```

## O que vem no plugin

| Componente | Conteudo |
|---|---|
| `agents/` | 29 agentes — 13 de etapa do fluxo (com gate) + 16 especialistas sob demanda |
| `commands/` | 16 comandos de despacho — `/card`, `/ambiente`, `/fluxo`, `/analise`, `/plano`, `/dev`, `/testar`, `/evidencias`, `/destilar`, `/brain`, `/kb`... |
| `scripts/` | `kb.sh` (recall), `ancoras.py` (autocorrecao), `hook_dominio.py` (reflexos), `brain_status.sh` (diagnostico) e os scripts de fase/teste/cache |
| `frota/` | `regras.md` (regras invioraveis, fonte unica), `grupos.tsv`, `gatilhos.tsv` + `gatilhos.md` (gatilho por artefato) e o catalogo |
| `hooks/` | `PostToolUse[Edit\|Write\|MultiEdit\|NotebookEdit / Bash / Agent]`, `SessionStart`, `Stop` — marcam e cobram a atualizacao do conhecimento e o **gatilho de especialista por artefato** |

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

Os agentes em `.cursor/agents/` sao a fonte. Depois de edita-los:

```
python3 .cursor/scripts/gerar_plugin.py
```

O gerador remove secoes especificas de produto e generaliza trechos com fato local — a lista
do que foi generalizado sai no stdout, para conferencia.
