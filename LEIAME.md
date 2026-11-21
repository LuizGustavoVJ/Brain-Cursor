# Brain Cursor — pacote do harness (modelo)

O repositório **LuizGustavoVJ/Brain-Cursor** é a fonte canônica da frota. O diretório `usuario/` espelha personalizações do operador (não versionadas no repo de produto).

## Conteúdo

| Pasta do pacote | Onde vive na máquina | O que é |
| --- | --- | --- |
| `AGENTS.md` | raiz do repo de produto | núcleo: roteamento, regras críticas, gates |
| `.cursor/` | `.cursor/` do repo de produto | frota, comandos, skills transversais, scripts e hooks |
| `usuario/.cursor/settings.json` | `~/.cursor/settings.json` | configuração de usuário (hooks de voz) |
| `usuario/.cursor/hooks/` | `~/.cursor/hooks/` | `falar.sh`, `narrar.sh`, `ganho_audio.py` (voz local via piper) |
| `usuario/.cursor/girias-regionais.md` | `~/.cursor/girias-regionais.md` | gírias usadas só no chat |
| `usuario/.cursor/skills/caveman/` | skill de compressão de resposta | caveman |
| `usuario/memoria/` | memória persistente do projeto Cursor | fatos do operador |
| `usuario/brain-plugin/` | artefato gerado | plugin distribuível |

## Fora do pacote (de propósito)

- `~/.cursor/mcp.json`: credenciais de MCP. Não viaja em pacote.
- `.cursor/cache/`, `*.lock`, `*.bak*`, `__pycache__`: estado de execução.
- Mapas `dominio-*` e perfis `ambiente-local-{repo}.md`: **por repositório de produto**.

## Restaurar harness no produto

```bash
git clone https://github.com/LuizGustavoVJ/Brain-Cursor.git
cd <seu-repo-de-produto>
rsync -a Brain-Cursor/.cursor/ .cursor/ && cp Brain-Cursor/AGENTS.md .
bash .cursor/scripts/propagar.sh --dry-run   # só a partir do clone canônico Brain-Cursor
```

Os itens de `usuario/` voltam para os caminhos da tabela acima.