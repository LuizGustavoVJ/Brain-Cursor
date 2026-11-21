---
name: habilidades-do-brain
description: "Habilidade tem 3 origens (conta cursor.com, embutida no CLI, plugin sincronizado não instalado); mapa único é .cursor/habilidades.md, acesso sempre por skills_conta.sh, nunca por UUID de bucket ou de memória"
metadata:
  node_type: memory
  type: project
  originSessionId: 7781fa3b-ad08-4cb7-b197-746e220881cb
  modified: 2026-09-25T18:03:23.111Z
---

Consolida `habilidades-tres-origens` e `skills-da-conta-encaixe` (destilação de 25/09/2026).

Desde 18/09/2026 o Brain reconhece **três origens** de habilidade: (1) **8 skills da conta**
cursor.com (`skill-creator`, `pdf`, `docx`, `xlsx`, `pptx`, `docs`, `morning`, `import-memory`),
vivendo em `~/.cursor/skills/synced/<bucket-uuid>/` — escopo de **usuário**, valem em todos os
repositórios sem `propagar.sh`; (2) **16 skills embutidas no CLI**, invocáveis sem arquivo antes da
1ª invocação; (3) **9 plugins sincronizados** com `installationPreference: available` — baixados
pela conta, **não instalados** (`cursor plugin list` vazio, não invocáveis), valem só como texto de
referência via `.cursor/scripts/skills_conta.sh ler-plugin <plugin>/<skill>`.

**O mapa único é `.cursor/habilidades.md`** (renomeado de `skills-da-conta.md` — não citar o nome
antigo). O UUID do bucket muda a cada re-sync: todo acesso é por **nome**, via `skills_conta.sh`,
nunca cravando caminho/UUID nem citando de memória.

**Duas armadilhas reais das skills da conta:**
1. A `description` da skill `docs` empurra para criar documento na nuvem — competiria com
   "entregável de card vive em `docs/` do repo" e os gates I2-val/I11/I15. A trava é estrutural:
   nenhum agente declara a tool `mcp__legacy_docs__*`.
2. `skill-creator` escreve em `.cursor/commands/` e `<skill>-workspace/` **dentro do repositório** —
   o que nasce lá **viaja no `propagar.sh` para todos os repos**. Rodar sempre no scratchpad.

5 agentes têm a tool `Skill` habilitada desde a Fase 3 (25/09: engenheiro-de-brain, especialista-sql,
pesquisador-web, redator-tecnico, levantador-requisitos), cada um com a instrução "saída sempre em pt-BR, nunca invoque `docs` nem
`morning`" — o `/bom-dia` foi rejeitado (saída HTML de artifact degrada no terminal).

**How to apply:** antes de usar qualquer habilidade, `skills_conta.sh listar`; se `ler-plugin`
falhar, dizer "não disponível" e seguir.
