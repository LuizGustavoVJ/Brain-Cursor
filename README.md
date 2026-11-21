# Brain-Cursor

Harness operacional Solides/CIT para **Cursor**: núcleo `AGENTS.md`, frota de subagentes em `.cursor/agents/`, skills, comandos, hooks Python e plugin opcional.

## Instalação rápida

1. Clone este repositório na raiz do seu projeto de produto (ou use como referência).
2. Copie ou merge: `AGENTS.md`, `.cursor/` e `usuario/` conforme necessário.
3. No Cursor: **Settings → Rules** — confirme que `AGENTS.md` e `.cursor/rules/*.mdc` aparecem.
4. **Customize → Hooks** — valide `.cursor/hooks.json` sem erro (hooks `sessionStart` são **desktop only**; Cloud Agents usam `beforeSubmitPrompt` e `stop`).

## Estrutura

| Caminho | Conteúdo |
|---------|----------|
| `AGENTS.md` | Núcleo do harness (roteamento, gates) |
| `.cursor/agents/` | 29 subagentes por etapa |
| `.cursor/skills/` | Skills Agent Skills |
| `.cursor/commands/` | Slash commands |
| `.cursor/hooks.json` | Hooks Cursor (schema v1) |
| `.cursor/scripts/` | `hook_*.py`, `frota.sh`, `propagar.sh` |
| `usuario/memoria/` | Fatos do operador (pista, não fonte de verdade) |
| `usuario/brain-plugin/` | Artefato do `gerar_plugin.py` |

## Comandos úteis

```bash
bash .cursor/scripts/frota.sh lint
bash .cursor/scripts/brain_status.sh
python3 .cursor/scripts/gerar_plugin.py usuario/brain-plugin
```

## Propagação multi-repo

`bash .cursor/scripts/propagar.sh` — rsync do harness para clones locais (legado). Preferência futura: plugin Cursor (`usuario/brain-plugin`).

## Migração Claude → Cursor

Concluído P0+P1 neste branch: paths `.cursor/`, `AGENTS.md`, `hooks.json`, rules `.mdc`, agentes sem campo `tools:`.

**P2 (pendente):** card piloto completo, permissões MCP via hooks `beforeMCPExecution`, commands→skills, Projects/coordinator, limpar refs `mcp__legacy_claude_ai_*`.

## Licença / uso

Repositório operacional interno Solides. Não commitar secrets (`settings.local.json` está no `.gitignore`).
