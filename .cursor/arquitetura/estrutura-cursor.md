# Estrutura da pasta `.cursor/`

Documentação de contexto do projeto para o Cursor. Separada de **`docs/`** (entregáveis de sustentação por card): aqui fica **como** trabalhar, lá **o que** foi produzido.

## Árvore de diretórios

Só **pastas e papéis** — a lista de arquivos de cada pasta vive num lugar só, apontado na coluna
da direita. Árvore que enumera arquivo desatualiza no primeiro arquivo novo e passa a mentir.

```
.cursor/
├── settings.json             # permissões (allow/deny) + hooks  → arquitetura/automacoes.md
├── settings.local.json       # overrides pessoais (MCP, additionalDirectories) — não padronizado
├── README.md                 # índice secundário (AGENTS.md na raiz é o principal)
├── fluxo-completo.md         # C0 + L0 + B0 + S1–S6 + I1–I15 + abas — leitura obrigatória em card
├── otimizacao-custos.md      # política de custo: subagente por etapa, cache, abas
├── agents/                   # a frota: um arquivo por agente     → frota.sh listar
├── commands/                 # atalhos de despacho (/card, /dev…) → frota.sh lint confere
├── frota/                    # README (roteamento), regras.md (fonte única), grupos.tsv
├── scripts/                  # hooks, kb, frota, fase, testes…    → README.md § Scripts do Brain
│                             #                                    → automacoes.md § Scripts de apoio
├── skills/                   # stack + processo + mapas dominio-* → skills/README.md
├── sustentacao/              # diagnóstico: fluxo, análise, decisão (S1–S6)
├── implementacao/            # plano, código, validação, E2E, local, homol (I1–I15)
├── arquitetura/              # estrutura + automações + brain.md + PERFIS por projeto
└── cache/                    # transitório e NÃO versionado: fase atual, mapas sujos, logs de teste
```

**Perfis por projeto** (em `arquitetura/`): trio `ambiente-local-{projeto}.md` ·
`estado-projeto-{projeto}.md` · `alteracoes-ambiente-local-{projeto}.md`, um para **cada**
repositório Solides. Todos coexistem na pasta em todos os repos; o agente usa o do projeto atual,
identificado pelo diretório `/var/www/html/{projeto}`. Ver AGENTS.md § *Perfil do projeto atual*.

**Onde o Brain é gerado, não configurado:** `scripts/gerar_plugin.py` empacota `agents/`,
`commands/`, `scripts/` e `frota/` em `~/solides-brain-plugin` — **fora** de `.cursor/`, de
propósito. Artefato gerado dentro da pasta de configuração parece uma segunda fonte de verdade.

## Princípio de separação

| Pasta | O que vai aqui | O que **não** vai aqui |
|-------|----------------|------------------------|
| **`skills/`** | Conhecimento de stack (CI2, Playwright, HTML evidências) e regra transversal consultável (`regras-de-trabalho`) | Passo a passo de etapa (→ `sustentacao/` / `implementacao/`) |
| **`sustentacao/`** | Fluxo de diagnóstico, análise, decisão | Plano de código; execução |
| **`implementacao/`** | Plano, validação plano/código, E2E, evidências de testes, HTML pós-implementação | Diagnóstico de card |
| **`arquitetura/`** | Estrutura de pastas (`docs/`, `.cursor/`), ambiente local, decisões consolidadas | Passo a passo de um card específico |
| **`docs/`** (raiz do repo) | Artefatos do card (fluxo, análise, evidências, implementação) | Regras do agente |

## Papel de cada pasta

### `skills/`

Uma pasta por skill, com `SKILL.md` + arquivos de detalhe ao lado (divulgação progressiva).

- **`rules/` voltou em 25/09/2026, em formato nativo:** `.cursor/rules/*.md` com frontmatter
  `paths:` — o Cursor carrega o arquivo só quando a sessão toca um caminho que casa. (A pasta
  antiga, apagada em 21/08, era de `.mdc`, convenção do Cursor que o Cursor nunca carregou.)
  Regra que só importa ao tocar certo arquivo vai em `rules/`; regra transversal é skill ou linha
  no `AGENTS.md`.
- `SKILL.md` enxuto, imperativo, com o detalhe em arquivo vizinho.
- Catálogo: fonte única em [`../skills/README.md`](../skills/README.md).

### `sustentacao/`

Guias **como fazer** o diagnóstico de sustentação: ciclo por card (**S1–S6**), fluxo, análise, evidências, decisão.

- Plano e código → [`.cursor/implementacao/`](../implementacao/fluxo-implementacao.md).

### `arquitetura/`

Referência **estável** do projeto: onde ficam os arquivos, ambiente local, decisões que não mudam a cada card.

- Atualizar `estado-projeto-{projeto}.md` quando houver decisão consolidada nova.
- Novos padrões de pasta → documentar aqui antes de espalhar no chat.

## Fluxo de consulta

```
0. reflexos (hooks) — lembrete reinjetado a cada mensagem + medidor de contexto + aviso de mapa sujo
1. AGENTS.md          (raiz — sempre carregado)
2. fluxo-completo.md  (cards e incidentes — inclui B0 e comportamento de abas)
3. skills/*           → stack relevante (CI2, QA, ambientes/testes, etc.)
4. sustentacao/*      → diagnóstico S1–S6 (após B0 = sustentação)
5. implementacao/*    → I1–I15 (após S6b OU B0 = implementação com (Y/n))
6. arquitetura/*      → paths, ambiente, decisões, automações
7. docs/              → artefatos do card
```

## Quando criar novos arquivos

| Situação | Onde criar |
|----------|------------|
| Nova regra transversal, consultável sob demanda | `skills/{tema}/SKILL.md` + índice em `skills/README.md` |
| Nova regra que vale para **toda** mensagem | linha no `AGENTS.md` (único arquivo sempre carregado) |
| Nova skill de stack ou domínio técnico | `skills/{nome}/SKILL.md` + índice em `skills/README.md` |
| Novo passo no processo de sustentação | `sustentacao/nome-do-guia.md` + link no `README.md` |
| Novo passo no processo de implementação | `implementacao/nome-do-guia.md` + link no `README.md` |
| Novo padrão de pasta ou decisão estável | `arquitetura/` + linha em `estado-projeto-{projeto}.md` |
| Entrega de um card específico | `docs/` conforme [estrutura-docs.md](estrutura-docs.md) |

## Relação `.cursor/` × `docs/` × `testes/`

| `.cursor/` | `docs/` | `testes/` |
|------------|---------|-----------|
| **Como** trabalhar (processo, regras) | **O quê** foi produzido (fluxo, análise, evidências) | **Specs Playwright** (E2E I7 + local I10 + homol I13) |
| Índice e guias reutilizáveis | Um conjunto de arquivos por `{card-id}` | `E2E/specs/{card-id}/`, `local/specs/{card-id}/`, `homol/specs/{card-id}/` |
| Mantido pela equipe como padrão | Versionado por incidente | Config em `playwright.config.ts` |

## Manutenção

- Ao **quebrar** um guia grande: manter no `SKILL.md` (ou no guia índice) só o imperativo + link, e mover o detalhe para arquivo vizinho, `sustentacao/` ou `arquitetura/`.
- Ao **adicionar** pasta nova em `.cursor/`: atualizar a árvore acima, o `README.md` e, se for decisão estável, `estado-projeto-{projeto}.md`.
- Ao **adicionar arquivo** dentro de pasta existente: registrar na **fonte única daquela pasta**
  (skill → `skills/README.md`; agente → `frota/grupos.tsv`; guia → `README.md`), **não** aqui —
  esta árvore lista pastas, não arquivos.
- **Não** colocar em skill ou guia conteúdo que só se aplica a um card — isso vai em `docs/`.
