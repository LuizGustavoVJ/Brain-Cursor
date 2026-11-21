# Brain Solides — pacote completo (28/09/2026)

Origem: repositório `cit` (`/var/www/html/cit`), fonte única do Brain.

## Conteúdo

| Pasta do pacote | Onde vive na máquina | O que é |
| --- | --- | --- |
| `repo/AGENTS.md` | `/var/www/html/cit/AGENTS.md` | núcleo: roteamento, regras críticas, gates |
| `repo/.cursor/` | `/var/www/html/cit/.cursor/` | frota (agents), comandos, fluxo, regras, skills, scripts e hooks do projeto |
| `usuario/.cursor/settings.json` | `~/.cursor/settings.json` | configuração de usuário (hooks de voz) |
| `usuario/.cursor/hooks/` | `~/.cursor/hooks/` | `falar.sh`, `narrar.sh`, `ganho_audio.py` (voz local via piper) |
| `usuario/.cursor/girias-regionais.md` | `~/.cursor/girias-regionais.md` | gírias usadas só no chat |
| `usuario/.cursor/skills/caveman/` | `~/.agents/skills/caveman` (link em `~/.cursor/skills/caveman`) | skill de compressão |
| `usuario/memoria-cit/` | `~/.cursor/projects/-var-www-html-cit/memory/` | memória persistente do projeto cit |
| `usuario/patches-locais-cit/` | `~/patches-locais-cit/` | patches do ambiente local (usados por `local.sh`) |
| `usuario/solides-brain-plugin/` | `~/solides-brain-plugin/` | plugin gerado por `gerar_plugin.py` |

## Fora do pacote (de propósito)

- `~/.cursor/mcp.json`: guarda o PAT do ADO e credenciais de MCP. Não viaja em pacote.
- `.cursor/cache/`, `*.lock`, `*.bak*`, `__pycache__`: estado de execução, recriado sozinho.
- Piper (`~/.local/opt/piper`): binário e modelo de voz; reinstale à parte.

## Restaurar

```bash
unzip brain-solides-20260928.zip -d /tmp/brain
rsync -a /tmp/brain/repo/.cursor/ /var/www/html/cit/.cursor/ && cp /tmp/brain/repo/AGENTS.md /var/www/html/cit/
cd /var/www/html/cit && bash .cursor/scripts/propagar.sh --dry-run   # depois sem --dry-run
```

Os itens de `usuario/` voltam para os caminhos da tabela acima.
