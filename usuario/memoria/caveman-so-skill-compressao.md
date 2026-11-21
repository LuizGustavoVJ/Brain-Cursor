---
name: caveman-so-skill-compressao
description: Do caveman só instalamos a skill de compressão de saída; proxy e Caveman Cloud descartados
metadata:
  node_type: memory
  type: project
  originSessionId: cf5727cc-ae3b-4ecd-ac10-bb833a345f10
  modified: 2026-09-25T15:10:26.707Z
---

Da ferramenta caveman (JuliusBrussee/caveman, redução de token) instalamos **apenas a skill `caveman`** (modo de compressão de saída lite/full/ultra/wenyan), em escopo global user-level (`~/.cursor/skills/caveman` → symlink para `~/.agents/skills/caveman`). É instrução passiva 100% local: sem rede, telemetria, SQLite ou cloud; ativa só com `/caveman`.

O install `npx skills add JuliusBrussee/caveman -g` trouxe ~20 skills junto (caveman-commit, caveman-review, safe-refactor, migration, verify-and-stop, lean-build, investigate-first, cavecrew e as do Caveman Cloud: caveman-setup/discover/manage/optimize/learn/evidence-review). Removidas todas com `npx skills remove -g <nomes> -y` — colidiam com as etapas/gates do Brain ou apontavam para o **Caveman Cloud gateway (descartado: manda tráfego para terceiro)**.

**Descartados e por quê:** o proxy `@caveman-ai/cli` (BSL-1.1, intercepta e guarda tráfego em SQLite local) e o gateway cloud. Se um dia for usar o proxy com dado real, passar antes pelo `especialista-seguranca (absorveu o de cibersegurança na Fase 3)` (gatilho de artefato: dependência que intercepta/armazena tráfego). Ver [[gatilho-por-artefato-nao-por-etapa]] e [[skills-da-conta-encaixe]].
