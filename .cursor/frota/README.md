# Frota — um agente por função (contagem viva: `frota.sh grupos`)

Duas divisões, propósitos diferentes:

| Divisão | O que é | Como entra no trabalho |
|---|---|---|
| **Fluxo** (13) | etapas do card, com **gate** | na ordem da trilha: C0 → L0 → B0 → S1–S6 ou I1–I15 (curta ou completa) |
| **Especialistas** (16) | consultoria sob demanda | chamados **dentro** de uma etapa, pelo gatilho do artefato ou por pedido |

Frota enxuta na Fase 3 (25/09/2026): de 63 para 29 agentes, sem perder função — cada fundido foi
absorvido por um sobrevivente (rastreio: `docs/analises/brain/rastreio-fase3.md`). Especialista
**não substitui** etapa e nenhum gate é dispensado por consulta.

## Como achar o agente certo

```bash
.cursor/scripts/frota.sh buscar <tema>     # qual agente atende
.cursor/scripts/frota.sh gatilhos [tema]   # quando cada especialista entra (por artefato)
.cursor/scripts/frota.sh listar [grupo]    # catálogo completo, ou de um grupo
.cursor/scripts/frota.sh grupos            # contagem por grupo
.cursor/scripts/frota.sh modelos           # distribuicao de modelo e politica de custo
.cursor/scripts/frota.sh lint              # integridade da frota
```

O catálogo **não é duplicado aqui de propósito** — ele é gerado do disco por `frota.sh listar`.
Lista copiada em markdown desatualiza na primeira mudança e passa a mentir.

## Política de modelo

O modelo sai do **custo de errar**, não do prestígio da tarefa:

| Modelo | Para | Exemplos |
|---|---|---|
| `haiku` | extrair, listar, conferir estrutura — sem julgamento | `leitor-card`, `ambiente-local`, `validador-leve` |
| `sonnet` | escrever e revisar com padrão conhecido, configurar, diagnosticar com procedimento | `especialista-sql`, `escritor-evidencias`, `engenheiro-de-brain`, `testador` |
| `opus` | **porta única** — dinheiro, dado pessoal, contrato público, causa raiz, arquitetura | `especialista-financeiro-cobranca`, `especialista-seguranca`, `analista-causa-raiz`, `validador-tecnico` |

Somente leitura **não** é sinônimo de tarefa barata: `especialista-seguranca` não escreve e é opus
porque errar custa incidente. O orquestrador pode subir o modelo de um sonnet para opus na chamada
quando a pergunta for de porta única (ex.: `engenheiro-de-brain` em mudança arquitetural,
`pesquisador-web` em decisão cara). `frota.sh modelos` mostra a distribuição.

## Roteamento por sintoma

| Você tem… | Chame |
|---|---|
| bug intermitente, "funciona na minha máquina", "por que este código existe?" | `analista-causa-raiz` |
| "isto vai quebrar produção?" | `revisor-arquitetura` + `gestor-de-risco` |
| "está lento", N+1, índice | `especialista-sql` |
| "está errado o número", métrica, BigQuery, migration | `especialista-sql` |
| "cobrou duas vezes", webhook reenviado, cron sobreposto | `especialista-financeiro-cobranca` |
| "o terceiro não respondeu", contrato de API, rota nova | `especialista-integracao` |
| "pipeline vermelho", branch, conflito, o que está em qual branch | `especialista-git` |
| "container não sobe", "a requisição não chega", 3xx/5xx antes do PHP | `especialista-docker` |
| Lambda, IAM, fila, CloudWatch, fatura da AWS | `especialista-aws` |
| "isto está exposto?", "vazou segredo", bump de biblioteca, CVE | `especialista-seguranca` |
| "preciso decidir entre X e Y", doc oficial, "tenho 80 páginas para ler" | `pesquisador-web` |
| "o usuário erra sempre aqui", texto de tela, acessibilidade | `especialista-ux` |
| view, JS, CSS, controller legado | `especialista-php-legado` |
| "esta mudança é grande demais" | `arquiteto-plano` (fatiamento) |
| "o pedido está vago" | `levantador-requisitos` |
| "o código não faz o que o card combinou" | `revisor-regra-negocio` |
| "o Brain não obedeceu", agente novo, skill, MCP, sessão cara | `engenheiro-de-brain` |
| "preciso publicar o contrato / registrar a decisão", runbook, MR | `redator-tecnico` |
| "subir/atualizar collection ou environment no Postman" | `especialista-postman` |
| "onde está documentado X?", documento duplicado | `destilador-dominio` |

Comandos: os de etapa, `/sql` (caso duro do gatilho), `/frota`, `/especialista <tema> — <pergunta>`,
`/kb` e `/brain` — em [`../commands/`](../commands/). Os atalhos por especialista saíram na Fase 3
(0 usos em 42 dias): `/especialista` e o próprio `Agent` cobrem.

## Regras de uso

0. **O gatilho é por artefato, não por etapa.** Produziu ou alterou SQL, migration, rota,
   dinheiro, credencial, view, container, pipeline ou dependência → o especialista da classe entra
   **antes** de o artefato sair, em qualquer etapa e também fora do fluxo de card. Todos têm
   condição objetiva; parte é cobrada pelo hook (contagem: `frota.sh gatilhos`). Mecanismo:
   [`gatilhos.md`](gatilhos.md).
1. **Um assunto, um agente.** Chamar três especialistas para a mesma pergunta triplica o custo e
   produz três respostas que você precisa reconciliar. Escolha.
2. **Handoff por caminho de arquivo, nunca por conteúdo colado.** O subagente nasce sem ver a
   conversa: passe o caminho, e é isso que mantém o contexto principal enxuto.
3. **Paralelize o que é independente.** Especialistas de temas diferentes sobre o mesmo diff
   podem ir na mesma mensagem.
4. **Retorno de 15 linhas**, linha 1 `Artefato:`, linha 2 `Veredito:`. Se um agente devolver o
   artefato inteiro, o rodapé dele está errado — conserte com o `engenheiro-de-brain`.
5. **Somente leitura é deliberado.** Agente sem `Write`/`Edit` propõe; quem aplica é o
   `desenvolvedor`, dentro do fluxo, depois do gate I4.

## Manutenção

| Arquivo | Papel |
|---|---|
| [`regras.md`](regras.md) | regras invioláveis — **fonte única**; o rodapé de 3 linhas de cada agente só aponta para cá |
| [`grupos.tsv`](grupos.tsv) | `grupo<TAB>agente` — fonte do agrupamento, verificada pelo `lint` |
| [`gatilhos.tsv`](gatilhos.tsv) | `agente<TAB>classe<TAB>condição<TAB>detecção` — **fonte única** dos gatilhos; lida pelo hook e pelo `lint` |
| [`gatilhos.md`](gatilhos.md) | mecanismo do gatilho por artefato: como é cobrado, como se registra, o que não autoriza |
| `../agents/*.md` | um arquivo por agente |
| `../commands/*.md` | atalhos de despacho |

Agente novo: o `engenheiro-de-brain` confere antes se fundir resolve, cria o arquivo, registra em
`grupos.tsv`, **declara a condição de disparo em `gatilhos.tsv`** (sem ela o `lint` acusa erro),
usa o rodapé padrão de 3 linhas e roda `frota.sh lint`. Depois, `gerar_plugin.py` e `propagar.sh`.
