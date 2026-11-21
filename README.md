# Brain-Cursor

Harness operacional **Brain Cursor** para o **Cursor**: núcleo `AGENTS.md`, frota de subagentes em `.cursor/agents/`, skills transversais, comandos, hooks Python e plugin opcional.

Repositório **canônico** da frota: alterações em `.cursor/` e `AGENTS.md` partem daqui e propagam para os repositórios de produto via `propagar.sh` ou plugin.

## Instalação rápida

1. Clone este repositório (referência ou base para merge no seu produto).
2. Copie ou merge: `AGENTS.md`, `.cursor/` e `usuario/` conforme necessário.
3. No Cursor: **Settings → Rules** — confirme que `AGENTS.md` e `.cursor/rules/*.mdc` aparecem.
4. **Customize → Hooks** — valide `.cursor/hooks.json` sem erro (hooks `sessionStart` são **desktop only**; Cloud Agents usam `beforeSubmitPrompt` e `stop`).

## Estrutura

| Caminho | Conteúdo |
|---------|----------|
| `AGENTS.md` | Núcleo do harness (roteamento, gates) |
| `.cursor/agents/` | Subagentes por etapa |
| `.cursor/skills/` | Skills Agent Skills (stack e processo; mapas `dominio-*` ficam nos repos de produto) |
| `.cursor/commands/` | Slash commands |
| `.cursor/hooks.json` | Hooks Cursor (schema v1) |
| `.cursor/scripts/` | `hook_*.py`, `frota.sh`, `propagar.sh`, `gerar_plugin.py` |
| `usuario/memoria/` | Fatos do operador (pista, não fonte de verdade) |
| `usuario/brain-plugin/` | Artefato do `gerar_plugin.py` |

## Comandos úteis

```bash
bash .cursor/scripts/frota.sh lint
bash .cursor/scripts/brain_status.sh
python3 .cursor/scripts/gerar_plugin.py usuario/brain-plugin
```

## Propagação multi-repo

`bash .cursor/scripts/propagar.sh` — rsync do harness para clones locais (só a partir deste repositório canônico). Alternativa: plugin Cursor (`usuario/brain-plugin`).

## Licença / uso

Repositório operacional interno Solides. Não commitar secrets (`settings.local.json` está no `.gitignore`).