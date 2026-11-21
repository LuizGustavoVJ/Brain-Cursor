# Contexto do projeto (Solides)

Índice da documentação `.cursor/` (genérica em todos os repos Solides; particularidades no perfil do projeto atual). **Antes de cada demanda**, consultar os arquivos relevantes abaixo.

**Leitura obrigatória para cards:** [fluxo-completo.md](fluxo-completo.md) — ciclo **C0** + **L0** + **B0 (bifurcação)** + S1–S6 + I1–I15, **comportamento de abas** e orçamento de contexto em uma página.

Padrão completo da pasta `.cursor/`: [`arquitetura/estrutura-cursor.md`](arquitetura/estrutura-cursor.md).

## Skills (`skills/`)

Conhecimento de **stack e domínio** — consultar quando a tarefa tocar o tema. O catálogo com o
uso de cada skill vive em **um lugar só**: [`skills/README.md`](skills/README.md). Busca por
termo: `.cursor/scripts/kb.sh buscar <termo>` (mapas `dominio-*` primeiro, `docs/` depois).

Escopo, repositório permitido e **checkpoint I5**: skill
[`skills/regras-de-trabalho`](skills/regras-de-trabalho/SKILL.md) — leitura obrigatória antes de
codar. Regras que carregam pelo caminho do arquivo: [`rules/`](rules/) (documento de card, SQL, testes, Brain) — formato em [`arquitetura/estrutura-cursor.md`](arquitetura/estrutura-cursor.md) § `skills/`.

## Frota de agentes (`agents/`) — um agente por função

O contexto principal **orquestra**; cada etapa roda em agente próprio, com contexto isolado,
ferramentas mínimas e modelo calibrado. Handoff **por caminho de arquivo**, nunca por conteúdo.

**O catálogo não é repetido aqui.** Ele tem uma fonte só, e ela é o disco:

| Quero… | Fonte única |
|---|---|
| a tabela etapa → agente → comando → modelo | **AGENTS.md** § *Frota* (sempre carregado) |
| catálogo completo, por grupo | `frota.sh listar [grupo]` — lido de `agents/*.md` |
| qual agente atende um tema | `frota.sh buscar <tema>` · `/frota <tema>` |
| **quando** cada especialista entra (por artefato) | `frota.sh gatilhos [tema]` — lido de [`frota/gatilhos.tsv`](frota/gatilhos.tsv) |
| quantos agentes há em cada grupo | `frota.sh grupos` — contado de [`frota/grupos.tsv`](frota/grupos.tsv) |
| que modelo cada um usa e por quê | `frota.sh modelos` · política em [`frota/README.md`](frota/README.md) |
| integridade (frontmatter, grupo, comando) | `frota.sh lint` |

Tabela em markdown duplicando essas colunas desatualiza na primeira mudança e passa a mentir —
foi o que aconteceu quando a contagem de especialistas mudou e quatro arquivos ficaram para trás.

Roteamento por sintoma, regras de uso e política de modelo: [`frota/README.md`](frota/README.md).
**Gatilho por artefato** — quando o especialista é obrigatório e como se registra:
[`frota/gatilhos.md`](frota/gatilhos.md).
Regras invioláveis de toda a frota: [`frota/regras.md`](frota/regras.md) — **fonte única**, citada
no rodapé de cada agente.

Diagnóstico geral: `/brain` · busca no acervo: `/kb <termo>`.
Arquitetura completa, incluindo o mecanismo de aprendizado: [`arquitetura/brain.md`](arquitetura/brain.md).

## Reflexos (hooks) do Brain

Os reflexos ligam conhecimento, contexto e testes ao fluxo **sem depender de o agente lembrar**:
lembrete reinjetado a cada mensagem, medidor de contexto, aviso e cobrança de mapa de domínio sujo,
a regra de não despejar stdout de teste, e a **cobrança do especialista pelo artefato produzido**
([`scripts/hook_gatilhos.py`](scripts/hook_gatilhos.py)). A configuração viva é [`settings.json`](settings.json);
o que cada um faz e por quê está em [`arquitetura/automacoes.md`](arquitetura/automacoes.md) §
*Hooks*. Quantos estão de pé agora: `/brain` (ou `brain_status.sh`) — a contagem não é escrita aqui
porque muda com o `settings.json`.

## Scripts do Brain

| Script | Uso |
|--------|-----|
| `scripts/kb.sh` | `buscar` · `indice` · `dominios` · `ancorar` · `verificar` · `sujos` · `limpar-sujos` |
| `scripts/ancoras.py` | Trava e **autocorrige** âncoras dos mapas — linha (`#L123`) e faixa (`#L123-L145`) |
| `scripts/brain_status.sh` | Diagnóstico: frota, conhecimento, reflexos, pendências |
| `scripts/frota.sh` | `listar` · `buscar <tema>` · `grupos` · `modelos` · **`gatilhos`** · `lint` — catálogo, calibragem, gatilho por artefato e integridade |
| `scripts/mcp.sh` | `listar` · `checar` · `agentes` — inventário e **saúde** dos MCPs; MCP quebrado é pior que ausente |
| `scripts/homol.sh` | `select` · `update` · `limpar` · `ping` — dado **ao vivo** de homologação (o MySQL `:3309` é dump congelado). **Só no cit** |
| `scripts/local.sh` | `status` · `apply` · `restore-repo` — patches locais (obrigatório antes de commit/PR) |
| `scripts/propagar.sh` | `--dry-run` · sem argumento replica o Brain em **todos** os repos git da máquina (backup datado antes) e **poda** no destino o que saiu da origem — o que é do destino se declara em `.cursor/proprio.txt` |
| `scripts/gerar_plugin.py` | Empacota o Brain em `~/solides-brain-plugin` (**fora** de `.cursor/`) para os outros repos |

## Sustentação (`sustentacao/`)

Diagnóstico e decisão — **sem alterar código**.

| Arquivo | Conteúdo |
|---------|----------|
| [`sustentacao/fluxo-por-card.md`](sustentacao/fluxo-por-card.md) | Ciclo sustentação (**S1–S6**) + handoff |
| [`sustentacao/documento-fluxo.md`](sustentacao/documento-fluxo.md) | Como produzir o MD de fluxo |
| [`sustentacao/documento-analise.md`](sustentacao/documento-analise.md) | Como produzir análise + HTML de evidências |
| [`sustentacao/validacao-subagente.md`](sustentacao/validacao-subagente.md) | Validação de fluxo e análise |
| [`sustentacao/consultas-bd.md`](sustentacao/consultas-bd.md) | Fluxo colaborativo de queries em produção |
| [`sustentacao/resposta-chat.md`](sustentacao/resposta-chat.md) | O que informar no chat (sustentação) |

## Implementação (`implementacao/`)

Plano, validação do plano e execução de código — **após** sustentação com **implementação necessária**.

| Arquivo | Conteúdo |
|---------|----------|
| [`implementacao/fluxo-implementacao.md`](implementacao/fluxo-implementacao.md) | Ciclo I1–I15 (detalhado) |
| [`implementacao/documento-implementacao.md`](implementacao/documento-implementacao.md) | Plano em `docs/implementacoes/plano/` (I1, I2-val) |
| [`implementacao/documento-implementacao-executada.md`](implementacao/documento-implementacao-executada.md) | Executada em `docs/implementacoes/executada/` (I5–I11) |
| [`implementacao/validacao-subagente.md`](implementacao/validacao-subagente.md) | Validação do plano (I2-val), código (I6), HTML local (I11) e HTML homol (I15) |
| [`implementacao/testes-e2e.md`](implementacao/testes-e2e.md) | Playwright project `e2e` (I7) |
| [`implementacao/testes-local.md`](implementacao/testes-local.md) | Testes URL local (I10) |
| [`implementacao/testes-homol.md`](implementacao/testes-homol.md) | Testes URL homol remota (I13) |
| [`implementacao/documento-testes.md`](implementacao/documento-testes.md) | Anexo `testes-e2e.md` — E2E (I8) + local (I11) |
| [`implementacao/documento-evidencias-html.md`](implementacao/documento-evidencias-html.md) | Atualizar `evidencias.html` (I9, I11) e `evidenciashomol.html` (I14) |
| [`implementacao/resposta-chat.md`](implementacao/resposta-chat.md) | O que informar no chat (implementação) |

## Arquitetura (`arquitetura/`)

| Arquivo | Conteúdo |
|---------|----------|
| [`arquitetura/estrutura-cursor.md`](arquitetura/estrutura-cursor.md) | Padrão da pasta `.cursor/` (genérico) |
| [`arquitetura/estrutura-docs.md`](arquitetura/estrutura-docs.md) | Padrão da pasta `docs/` (genérico) |
| [`arquitetura/automacoes.md`](arquitetura/automacoes.md) | Hooks, permissões e MCPs (genérico) |
| [`arquitetura/brain.md`](arquitetura/brain.md) | **Arquitetura do Brain** — camadas, frota, aprendizado, propagação (genérico) |
| `arquitetura/estado-projeto-{projeto}.md` | **Perfil:** decisões consolidadas (por projeto) |
| `arquitetura/ambiente-local-{projeto}.md` | **Perfil:** Docker local, BD, URLs, pasta `testes/` (por projeto) |
| `arquitetura/alteracoes-ambiente-local-{projeto}.md` | **Perfil:** alterações de código para rodar localmente (por projeto) |

> **Perfis:** um trio por projeto, nomeado pelo diretório em `/var/www/html/{projeto}`. O agente usa o do projeto atual (detectado pelo diretório). **A lista de projetos não é escrita aqui** — ela decai na primeira máquina diferente; para ver quem tem perfil: `ls .cursor/arquitetura/*-$(basename $PWD).md`. Ver AGENTS.md § *Perfil do projeto atual*.
