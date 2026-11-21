---
name: google-workspace-conectores-nativos
description: Conectores Gmail/Agenda/Drive ativos desde 18/09/2026; Drive LÊ conteúdo de Sheets/Docs/Slides, mas não escreve célula; conector só entra na sessão após reiniciar
metadata:
  type: reference
---

Em 18/09/2026 o Luiz vinculou em claude.ai os conectores nativos **Gmail**, **Google Agenda** e
**Google Drive** (conta `luiz.finotello@solides.com.br`). Testados e funcionando nesta máquina.

O que já dá para fazer:
- Gmail: buscar thread, ler, rascunhar, responder, enviar, rotular.
- Agenda: listar/criar/mover evento, sugerir horário.
- Drive: buscar arquivo e **ler o conteúdo** de Google Sheets, Docs, Slides, PDF, xlsx e docx
  (`read_file_content` devolve a planilha inteira em markdown, aba por aba) — inclusive comentários.

O que NÃO dá: **escrever célula em planilha, editar Doc/Slide, criar Forms, Tasks e Chat.**
Para isso é preciso o servidor `workspace-mcp` (taylorwilsdon), que exige projeto no Google Cloud
e credencial OAuth "Desktop application" — pendente com o Luiz.

**Armadilha:** vincular o conector em claude.ai **não** injeta as ferramentas na sessão já aberta —
o catálogo é montado no start. Sempre reiniciar a sessão depois de vincular.

Escrita em terceiro (enviar e-mail, criar evento, alterar arquivo) segue a regra de
[[pedir-permissao-antes-de-escrita-externa]].
