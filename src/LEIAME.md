# Brain Solides — pacote completo (28/09/2026)

Origem: repositório `cit` (`/var/www/html/cit`), fonte única do Brain.

## Conteúdo

| Pasta do pacote | Onde vive na máquina | O que é |
| --- | --- | --- |
| `repo/CLAUDE.md` | `/var/www/html/cit/CLAUDE.md` | núcleo: roteamento, regras críticas, gates |
| `repo/.claude/` | `/var/www/html/cit/.claude/` | frota (agents), comandos, fluxo, regras, skills, scripts e hooks do projeto |
| `usuario/.claude/settings.json` | `~/.claude/settings.json` | configuração de usuário (hooks de voz) |
| `usuario/.claude/hooks/` | `~/.claude/hooks/` | `falar.sh`, `narrar.sh`, `ganho_audio.py` (voz local via piper) |
| `usuario/.claude/girias-regionais.md` | `~/.claude/girias-regionais.md` | gírias usadas só no chat |
| `usuario/.claude/skills/caveman/` | `~/.agents/skills/caveman` (link em `~/.claude/skills/caveman`) | skill de compressão |
| `usuario/memoria-cit/` | `~/.claude/projects/-var-www-html-cit/memory/` | memória persistente do projeto cit |
| `usuario/patches-locais-cit/` | `~/patches-locais-cit/` | patches do ambiente local (usados por `local.sh`) |
| `usuario/solides-brain-plugin/` | `~/solides-brain-plugin/` | plugin gerado por `gerar_plugin.py` |

## Fora do pacote (de propósito)

- `~/.claude.json`: guarda o PAT do ADO e credenciais de MCP. Não viaja em pacote.
- `.claude/cache/`, `*.lock`, `*.bak*`, `__pycache__`: estado de execução, recriado sozinho.
- Piper (`~/.local/opt/piper`): binário e modelo de voz; reinstale à parte.

## Restaurar

```bash
unzip brain-solides-20260928.zip -d /tmp/brain
rsync -a /tmp/brain/repo/.claude/ /var/www/html/cit/.claude/ && cp /tmp/brain/repo/CLAUDE.md /var/www/html/cit/
cd /var/www/html/cit && bash .claude/scripts/propagar.sh --dry-run   # depois sem --dry-run
```

Os itens de `usuario/` voltam para os caminhos da tabela acima.
