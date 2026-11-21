# Estado do projeto — {projeto}

Registrar somente decisões **estáveis** e úteis para próximas tarefas. Formato: Contexto → Decisão → Impacto.

## Estado atual

- Repositório de trabalho: *(caminho ou nome do repo de produto)*
- Estrutura `docs/`: [estrutura-docs.md](estrutura-docs.md) quando existir
- Ambiente local: [ambiente-local-projeto.md](ambiente-local-projeto.md) + [alteracoes-ambiente-local-projeto.md](alteracoes-ambiente-local-projeto.md) — renomeie o sufixo para o nome do repo no clone de produto
- **L0 (pré-requisito):** subir ambiente local + URL no chat antes de B0
- Testes: conforme o perfil do repo (Playwright, PHPUnit, etc.)

## Decisões consolidadas

| Contexto | Decisão | Impacto |
|----------|---------|---------|
| Fluxo Brain | Sustentação S1–S6 ou implementação I1–I15 | Padroniza gates |
| Propagação | Alterações em `.cursor/` e `AGENTS.md` saem do repositório canônico **Brain-Cursor** | Fonte única do harness |

---

## Manutenção

No **Brain-Cursor**, mantenha este arquivo genérico. No repositório de produto, copie para `estado-projeto-{nome-do-repo}.md` e registre decisões estáveis daquele sistema.