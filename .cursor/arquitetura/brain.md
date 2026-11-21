# Arquitetura do Brain

> "Brain" não é uma feature do Claude Code — é um padrão de montagem sobre seis peças reais.
> Este documento descreve como elas se encaixam neste repositório e, principalmente, **por quê**.

## O problema que o Brain resolve

Antes: um único contexto fazia tudo — lia o card, mapeava o fluxo, diagnosticava, planejava,
codava, testava e escrevia evidências. Duas consequências mediram-se sozinhas:

1. **Contexto estourava.** Não por orçamento mal calibrado, mas porque análise, código e stdout
   de teste coabitavam o mesmo contexto. Somar tudo no mesmo lugar é o defeito, não o sintoma.
2. **Conhecimento evaporava.** 74 documentos em `docs/` sem índice e sem recall: cada card
   redescobria por `grep` o que o anterior já provou — e âncoras `arquivo:linha` copiadas de
   análises antigas apontavam para o lugar errado, porque o código andou.

## As seis camadas

| Camada | Onde vive | Carregamento | Papel |
|--------|-----------|--------------|-------|
| **Núcleo** | `AGENTS.md` (9,3 KB) | **sempre** | Roteamento, gates, proibições. Só o que vale para toda mensagem. |
| **Reflexos** | `.cursor/scripts/hook_*.py` + `settings.json` | por evento | Determinismo sem LLM: medir contexto, marcar mapa sujo, cobrar destilação. |
| **Frota** | `.cursor/agents/*.md` | por invocação | Uma função por agente, **contexto isolado**, ferramentas mínimas, modelo calibrado. Contagem por `frota.sh grupos`. |
| **Procedimento** | `.cursor/fluxo-completo.md`, `sustentacao/`, `implementacao/` | sob demanda | Como executar cada etapa. |
| **Domínio** | `.cursor/skills/dominio-*` | sob demanda | Conhecimento de negócio destilado, com âncoras verificáveis. |
| **Memória** | `memory/` + `docs/` + `kb.sh` | recall | Fatos persistentes e acervo indexado. |

A fronteira que importa: **o núcleo é caro porque é sempre carregado; todo o resto é grátis
até ser necessário.** O enxugamento de 08/2026 cortou o `AGENTS.md` de 21 KB e o lembrete de
prompt de 2,6 KB para 0,6 KB, derrubando o custo fixo por sessão em ~46% **sem remover uma única
regra** — o que saiu foi duplicação do `fluxo-completo.md`. O núcleo voltou a crescer depois
(a frota de especialistas entrou nele), então o tamanho de hoje se mede, não se lê aqui:
`wc -c AGENTS.md`, e o teto do lembrete de prompt (< 800 tokens) está em
[automacoes.md](automacoes.md) § *Orçamento do hook*.

## A frota: uma função por agente

A frota tem **duas divisões com propósitos diferentes**, e confundi-las é o erro mais caro:

| Divisão | O que é | Como entra |
|---|---|---|
| **Fluxo** (13) | um agente por etapa do card, cada um atrás de um **gate** | na ordem da trilha: C0 → L0 → B0 → S1–S6 ou I1–I15, curta ou completa |
| **Especialistas** (16) | consultoria por tema (dados, segurança, fronteira HTTP, dinheiro, infra, Brain…) | **dentro** de uma etapa, pelo gatilho do artefato ou por pedido |

**Fase 3 (25/09/2026): 63 → 29 agentes.** A medição de uso mostrou 11 agentes nunca chamados, seis
disputando SQL e seis de meta-IA sem uso. Cada agente fundido foi absorvido por um sobrevivente
(o corpo dele virou seção do herdeiro) e três sem artefato em nenhum repo (Kubernetes, Terraform,
LLM em produto) foram aposentados. As descriptions somadas caíram de ~14,5k para ~8k caracteres —
é o que o contexto principal carrega em toda mensagem. Rastreio agente antigo → sobrevivente:
`docs/analises/brain/rastreio-fase3.md`. Todo agente termina no **rodapé padrão de 3 linhas**
(leia `frota/regras.md` · gatilho · retorno `Artefato:`/`Veredito:`), conferido pelo `frota.sh lint`.

Especialista **não substitui etapa nem dispensa gate**: `/plano` continua sendo do
`arquiteto-plano`; o `especialista-aws` entra quando aquele plano toca Lambda. Quem chama o
especialista é o contexto principal, não o subagente — subagente não aciona subagente.

Contagem, catálogo e calibragem saem do disco, nunca de tabela em markdown:
`frota.sh grupos` · `frota.sh listar [grupo]` · `frota.sh modelos` · `frota.sh lint`.
Roteamento por sintoma e regras de uso: [`../frota/README.md`](../frota/README.md).

O contexto principal deixa de executar e passa a **orquestrar**: chama, recebe o caminho do
artefato, passa adiante.

**O handoff é por arquivo, não por conversa.** Um subagente nasce sem ver a conversa — então
`docs/` deixa de ser depósito e passa a ser o **barramento** entre agentes: o `mapeador-fluxo`
escreve `docs/fluxos/…`, o `analista-causa-raiz` lê aquele caminho e escreve `docs/analises/…`,
o `arquiteto-plano` lê a análise. Por isso todo agente da frota tem a mesma instrução de
retorno: **devolva o caminho, nunca o conteúdo** — colar conteúdo no retorno reintroduz
exatamente o acúmulo que a frota existe para eliminar.

Efeito colateral de custo: `docker ps` no L0 não precisa de Opus. Tarefa mecânica vai para
Haiku; Opus fica para julgamento — causa raiz, arquitetura, plano, código, validação técnica. O
`escritor-evidencias` (HTML de layout fixo, 4 chamadas por card) desceu para Sonnet e perdeu o
MCP Playwright: os prints saem dos specs do `testador`.

## Trilhas e teto de validação (Fase 3)

O processo agora acompanha o tamanho do card. **Trilha curta** (bug pontual sem dinheiro, dado
pessoal, schema, contrato público, 2+ repos nem mudança grande): análise/plano curto → I4 → código →
teste local → evidência validada uma vez (código + HTML) → homol com I12 → destilação. **Trilha
completa**: o fluxo inteiro, com I2 fundido no I2-val e I11+I15 consolidadas quando o homol vem na
sequência. O agente propõe a trilha no B0 pelo critério objetivo e o usuário confirma; `fase.sh B0
<card> --trilha <t>` registra. Gates do usuário (I4, I12), gatilho por artefato e destilação valem
nas duas. Cada etapa validada tem **no máximo 3 rodadas** (`cache_validacao.py rodada|recusa`); na
3ª recusa, a etapa para e vai ao usuário. Detalhe: `fluxo-completo.md` § *Trilhas* e § *Teto*.

## O aprendizado — e seu limite honesto

**Um modelo não aprende entre sessões.** Não há treinamento acontecendo aqui. O que produz o
efeito de aprendizado é **escrita persistente disparada por gatilho determinístico**. A
distinção é prática: se depender de o agente *lembrar* de anotar, falha — e falhou, foi assim
que as âncoras envelheceram sem ninguém notar.

Quatro mecanismos, nenhum dependente da memória do agente:

1. **`kb.sh ancorar`** — grava a assinatura de cada âncora: o **texto da linha apontada**, não
   só o número. A linha é sua própria assinatura.
2. **`kb.sh verificar`** — se o número não aponta mais para o texto travado, procura esse texto
   no arquivo e **corrige o número no mapa**. Zero LLM, zero token. Quando nenhuma linha
   corresponde, declara **órfã** — o código mudou de forma que a afirmação do mapa não vale
   mais, e isso precisa de decisão humana, não de autocorreção.
3. **`PostToolUse[Edit|Write]` → `hook_dominio.py`** — editou arquivo que um mapa cita? O mapa
   entra em `.cursor/cache/dominios-sujos`. `SessionStart` avisa antes da primeira palavra do
   agente; `Stop` cobra a destilação se o card acabou com mapa sujo.
4. **`destilador-dominio`** — no encerramento, lê os artefatos do card e faz o append no mapa:
   armadilha nova, âncora conferida, valor real de coluna, hipótese descartada.

O ciclo fecha assim: **o card produz conhecimento → o hook detecta que o mapa envelheceu → o
script corrige o que é mecânico → o agente registra o que exige julgamento.**

## Fluxo de uma demanda no Brain

```
/card 162988      leitor-card (haiku)     → resumo + GUID do projeto
/ambiente         ambiente-local (haiku)  → URL no chat
B0 — bifurcação + trilha curta/completa (proposta pelo agente, confirmada pelo usuário)
/kb <termo>       mapa de domínio ANTES de qualquer grep
/fluxo            mapeador-fluxo          → docs/fluxos/…
/analise          analista-causa-raiz     → docs/analises/… + validador-tecnico
/requisitos       levantador-requisitos   → requisitos verificáveis (card vago)
/arquitetura      revisor-arquitetura     → impacto sistêmico (mudança grande)
/plano            arquiteto-plano         → plano curto (validador-leve) ou plano + plano.html (validador-tecnico)
                  ══ gate I4: OK explícito do usuário ══
/dev              desenvolvedor           → código + validador-tecnico
/testar e2e|local testador               → N/N (nunca stdout); curta só local
/evidencias       escritor-evidencias     → evidencias.html + comando de postagem
/destilar         kb.sh verificar + destilador-dominio → mapa atualizado

em qualquer ponto:
/frota <tema>     acha o especialista     → consulta DENTRO da etapa, sem dispensar gate
/especialista <tema> — <pergunta>
```

`/brain` mostra o estado de tudo: frota, mapas, âncoras, pendências.

## O que continua sendo do usuário

O Brain automatiza execução, **não decisão**. Permanecem humanos, por desenho:

- **Gates I4 e I12** — código e deploy só com OK explícito.
- **Postagem no ADO** — o agente monta o HTML e pergunta, a cada postagem, se posta ele (com "sim") ou entrega o comando; subagente nunca posta.
- **Git** — nenhum commit, push ou pull sem autorização na mensagem.
- **SQL em produção** — o agente monta a query; o usuário executa. (Local e homol são do agente.)
- **Âncoras órfãs** — quando o código mudou tanto que a afirmação do mapa caiu, a decisão é humana.

## Manutenção

| Quando | O que fazer |
|--------|-------------|
| Card encerrado | `/destilar` — não é opcional, é parte do encerramento |
| Mapa novo criado | `kb.sh ancorar` para travar as âncoras |
| Código refatorado | `kb.sh verificar` — corrige o que moveu, aponta o que morreu |
| Skill de domínio nova | Registrar em `skills/README.md` e rodar `kb.sh indice` |
| Agente novo na frota | `engenheiro-de-brain`: primeiro confere se fundir resolve; senão cria em `agents/` com o rodapé de 3 linhas, registra em `frota/grupos.tsv` e `frota/gatilhos.tsv` — depois `frota.sh lint` |
| Regra da frota mudou | Editar **só** [`frota/regras.md`](../frota/regras.md) — o rodapé de cada agente só aponta para lá |
| Levar o Brain a outro repo | `gerar_plugin.py` → `~/solides-brain-plugin` (**fora** de `.cursor/`) → `/plugin marketplace add` |

> **Por que o plugin mora fora de `.cursor/`:** ele é **artefato gerado** a partir de `agents/`,
> `commands/`, `scripts/` e `frota/`. Artefato gerado dentro da pasta de configuração passa a
> parecer uma segunda fonte de verdade — e foi exatamente essa confusão que motivou tirá-lo de lá.
> A fonte é o `.cursor/` deste repositório; o plugin é a cópia generalizada, sem os fatos do cit.

## Distribuição: de `propagar.sh` para plugin — caminho de migração (não aplicado)

Hoje o Brain chega aos repositórios por **cópia de pasta** (`propagar.sh`: rsync com poda, backup
em `~/backups-brain/`, `proprio.txt` protegendo o que é do destino). O `gerar_plugin.py` já produz
um plugin generalizado em `~/solides-brain-plugin` (agentes, comandos, scripts, `frota/`, hooks via
`${CURSOR_PLUGIN_ROOT}`, `marketplace.json`). A decisão da Fase 3 foi **documentar, não trocar**.

| | `propagar.sh` (atual) | Plugin via marketplace privado |
|---|---|---|
| Fonte única | cópia física em 13+ repos; divergência só se alguém editar o destino | uma instalação por máquina, versão explícita (`VERSAO` no gerador) |
| Custo de atualizar | rodar o script a cada mudança; poda + backup por repo | regenerar + `/plugin update`; nada escrito dentro dos repos |
| Arquivo próprio do repo | `proprio.txt` no destino | fica no `.cursor/` do repo, sem conflito com o plugin |
| `AGENTS.md`, `rules/`, `settings.json` | viajam | **não** viajam em plugin — continuariam com o `propagar.sh` (ou num `AGENTS.md` mínimo por repo) |
| Nome dos agentes/comandos | `/plano`, `revisor-codigo` | namespaced pelo plugin (`/solides-brain:plano`); hooks do `settings.json` do repo e do plugin somam |
| Fato específico do cit | `homol.sh` e perfis não viajam | o gerador **generaliza** (SECOES_LOCAIS/SUBSTITUICOES) — precisa acompanhar cada agente novo |
| Risco | poda errada apaga arquivo do destino (mitigado por backup e origem única) | plugin desatualizado na máquina; dois Brains ativos se a pasta copiada não for removida |

**Passos, quando decidir migrar:** (1) `gerar_plugin.py` e conferir no stdout que todo fato do cit
foi generalizado; (2) `/plugin marketplace add ~/solides-brain-plugin` e `/plugin install
solides-brain` numa máquina de teste; (3) num repo piloto, remover `agents/ commands/ scripts/
frota/` copiados (backup antes) e manter só `AGENTS.md`, `rules/`, `settings.json` e o que é próprio;
(4) medir um card inteiro (comandos namespaced, hooks duplicados, `frota.sh lint` apontando para
`${CURSOR_PLUGIN_ROOT}`); (5) só então trocar os demais repos e reduzir o `propagar.sh` ao que plugin
não carrega (núcleo, `rules/`, settings). Reversão: reinstalar a pasta a partir do backup e
`/plugin uninstall solides-brain`.

