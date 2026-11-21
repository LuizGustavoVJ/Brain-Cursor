---
name: proibido-git-sem-autorizacao
description: "Proibido rodar commit, push ou pull sem autorização explícita do usuário — apenas editar o working tree e esperar OK"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d3634154-b788-4a91-9e57-3cd0a62dd840
  modified: 2026-08-05T17:26:08.971Z
---

Nunca executar `git commit`, `git push` ou `git pull` sem autorização explícita do usuário, em nenhuma circunstância. Ajustes de código ficam **somente no working tree** até ele dar o OK.

**Nota de 05/08/2026:** a pedido do usuário, a seção "Git: proibido sem autorização" foi **removida** do `AGENTS.md` do cit (ele considerou o fluxo pesado demais e os outros repos não tinham a seção). A regra em si **continua valendo** — está registrada aqui e é o comportamento padrão esperado; só não está mais duplicada no AGENTS.md.

**Why:** em 05/08/2026 o usuário pediu para ajustar o `Cliente_model.php` e remover patches locais (`MAX(...)`) que tinham vazado para o MR !3923. Eu interpretei "subir apenas o que fizemos no white label" como autorização para commitar e dar push — não era. O usuário respondeu que estou proibido de fazer commits, pulls e pushes sem autorização dele, e reforçou "nunca mais faça isso". Alterar o remoto sem OK é ação outward-facing e difícil de reverter.

**How to apply:** editar os arquivos, mostrar o `git diff` / `git status` no chat, e parar. Perguntar "posso commitar e subir?" e aguardar resposta afirmativa. Verbos como "ajuste para subir", "deixe pronto para subir" ou "suba apenas X" descrevem o **conteúdo desejado**, não uma autorização de push. Vale também para `git checkout`/`restore` que descarte trabalho — mostrar antes o que será perdido. Relacionado: [[cit-branching-staging-vs-master]], [[patches-locais-cit-fora-do-git]].
