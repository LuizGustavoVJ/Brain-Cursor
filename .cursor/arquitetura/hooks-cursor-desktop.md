# Hooks — desktop vs Cloud Agent

| Evento | Onde roda |
|--------|-----------|
| `beforeSubmitPrompt`, `postToolUse`, `stop` | Desktop e Cloud (repo `.cursor/hooks.json`) |
| `sessionStart` / `sessionEnd` | **Apenas desktop** (não no Cloud Agent padrão) |
| Hooks em `usuario/.cursor/hooks/falar.sh`, `narrar.sh` | **Apenas desktop** — voz/narração |

Os scripts `hook_*.py` ainda emitem `hookSpecificOutput` + `additionalContext` (compatível com import de hooks de terceiros no Cursor IDE). Para Cloud, confie em `beforeSubmitPrompt` e `stop` para lembretes de ADO/git e destilação.

Saída `decision: block` no `stop` (ex.: `hook_card.py`) — validar no desktop; no cloud pode virar `followup_message` conforme doc Cursor.
