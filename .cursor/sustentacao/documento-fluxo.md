# Documento de fluxo

**Pasta:** `docs/fluxos/{tipo}/`  
**Nome do arquivo:** `{card-id}.md` (ex.: `alteracao-cnpj-alfa-numerico.md`)

## Quando produzir

**Primeiro** passo do ciclo — mapear **completamente** o fluxo operacional/técnico do problema.

## `{tipo}`

Categoria em kebab-case — pasta por demanda/assunto (ex.: `alteracao-cnpj-alfa-numerico`, `automacao-creditos`).

## Conteúdo mínimo

- Título, índice, resumo do problema relatado
- Atores e sistemas envolvidos
- Ponto(s) de entrada (endpoint, rota, fila, cron, tela, etc.)
- Sequência passo a passo (referências a arquivos/classes/métodos quando identificados)
- Integrações externas e dependências
- Pontos de falha ou comportamento observado no card
- Diagrama ou lista numerada quando ajudar a leitura

## Validação

Após elaborar o fluxo, o agente **deve** submeter à validação do subagente antes de avançar. Se recusado: corrigir o `.md` e **revalidar** até aprovação. Ciclo completo: [validacao-subagente.md](validacao-subagente.md).
