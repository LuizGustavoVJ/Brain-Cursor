---
description: Catálogo da frota — qual agente atende o tema, ou diagnóstico de integridade
argument-hint: [tema] | listar | grupos | gatilhos | lint
---

Sem argumento ou com um tema, descubra quem atende:

```bash
.cursor/scripts/frota.sh buscar $ARGUMENTS
```

Para o catálogo completo, `frota.sh listar [grupo]`; para contagem, `frota.sh grupos`; para
integridade (nome, modelo, rodapé, grupo, comando órfão, **especialista sem gatilho**),
`frota.sh lint`.

Para saber **quando** cada especialista é obrigatório — o gatilho é por **artefato**, não por
etapa — `frota.sh gatilhos [tema]`. Mecanismo e registro:
[`.cursor/frota/gatilhos.md`](../frota/gatilhos.md).

Apresente em tabela e recomende **um** agente, não três. Roteamento por sintoma:
[`.cursor/frota/README.md`](../frota/README.md).
