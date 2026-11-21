---
name: comando-de-projeto-sombreia-embutido
description: comando em .cursor/commands/ com nome de comando embutido do CLI TAPA o embutido; o /mcp do Brain escondeu o gerenciador de servidores MCP e foi renomeado para /mcp-diag em 18/09/2026
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ff7ce71a-31e5-41a2-bf1c-3330da8fb924
  modified: 2026-09-18T19:31:50.308Z
---

Comando de projeto em `.cursor/commands/<nome>.md` **sombreia** o comando embutido de mesmo nome.
Em 18/09/2026 isso queimou de verdade: o Brain tinha `/mcp` apontando para o `especialista-mcp`,
então o usuário digitava `/mcp` para autorizar o Grafana e recebia um diagnóstico de subagente —
o gerenciador de servidores do CLI **nunca abria**, e nenhuma mensagem dizia que havia colisão.
Pior: o próprio texto do comando mandava "autorize em sessão interativa (`/mcp`)", ou seja,
apontava para aquilo que ele mesmo bloqueava. Renomeado para **`/mcp-diag`** (comando removido na Fase 3 em 25/09 por falta de uso; a lição — não nomear comando igual a embutido — continua) (atalho no `AGENTS.md`
atualizado, replicado nos 13 repos).

Caminho direto para autorizar OAuth, sem depender de menu nenhum: **`claude mcp login <servidor>`**
no terminal (existe também `claude mcp logout <servidor>`). Ver [[monitoramento-datadog-grafana]].

**Why:** o sintoma ("não aparece a opção") aponta para o servidor, mas a causa está no Brain. Sem
saber da regra de sombreamento, o diagnóstico vira caça ao fantasma do lado do conector.

**How to apply:** antes de criar comando em `.cursor/commands/`, conferir se o nome já é embutido
do CLI (`mcp`, `init`, `run`, `loop`, `schedule`, `compact`, `clear`, `review`…). Nome que colide,
renomeia. E quando o usuário disser "fiz e não apareceu a opção", suspeitar de comando do Brain
tapando o embutido ANTES de investigar o conector.
