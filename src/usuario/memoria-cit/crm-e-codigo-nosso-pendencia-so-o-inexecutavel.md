---
name: crm-e-codigo-nosso-pendencia-so-o-inexecutavel
description: CRM é código nosso (o agente desenvolve e executa); pendência de terceiros é APENAS o que o agente não consegue executar
metadata:
  type: feedback
---

Na feature 161899 (ganho via cartão) e adiante, o **solides-crm é código nosso**: o agente
desenvolve nele como desenvolve no cit. O agente é responsável por **executar o código em todos
os ambientes necessários** à demanda.

"Pendência de terceiros" tem definição estreita e literal: **apenas o que o agente não consegue
executar**. Nada mais. Todo o restante é responsabilidade do agente fazer.

**Why:** eu vinha classificando como "pendência de terceiros com dono no time do CRM" trabalho
que era simplesmente trabalho — encolhia a entrega por suposição de fronteira organizacional em
vez de por incapacidade real. O usuário cortou isso: a fronteira é técnica (consigo executar?),
não política (de quem é o time?).

**How to apply:** antes de mandar qualquer item para o documento de pendências, responder uma
pergunta só — "eu consigo executar isto?". Se sim, é meu e eu faço, mesmo que o arquivo viva em
outro repositório. Só entra em pendência o que depende de acesso, credencial, agendamento ou
ambiente que eu não alcanço (agendar cron, migration em ambiente fora do meu alcance, ajuste no
portal do HubSpot, rotação de credencial de terceiro). Ver [[cartao-autorizacao-cross-repo-branches]]
e [[migrations-homol-doc-consolidado-161899]].
