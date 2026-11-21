---
name: dominio-pagamento-cartao
description: >-
  Mapa de domínio do pagamento por cartão (Pagar.me) do CIT — feature 161899, Fase 1: canal JWT
  CIT→checkout, tokenização, retorno por webhook via lambda AWS, cobrança avulsa mensal via
  CMOVIMENTOS/DATAVENCIMENTO (sem recorrência nativa da Pagar.me), régua de recusa com observação
  no CRM e a pendência do lado Omie. Use em qualquer card que toque cartão de crédito, Pagar.me,
  webhook de cobrança/pagamento, motor de cobrança avulsa, régua de recusa de mensalidade, ganho
  por cartão ou lambda de retorno de pagamento. Aplica-se ao repositório cit.
---

# Domínio — Pagamento por cartão (Pagar.me, feature 161899)

> **Toda esta skill descreve código em branch, ainda não mergeado na `master`.** Conferido em
> 25/09/2026 na worktree **principal** `~/worktrees/cit/161899_etapa_5_8_11_12_pos_venda` (branch
> de mesmo nome) — a mais evoluída das ~20 worktrees da feature 161899 em `~/worktrees/cit/`.
> Toda âncora `arquivo:linha` desta skill é **relativa a essa worktree**, não à `master`: antes de
> citar uma linha num card, confirme que ainda bate lá (`git -C ~/worktrees/cit/161899_etapa_5_8_11_12_pos_venda diff`).
> O `kb.sh ancorar`/`verificar` do repositório principal **não trava** essas âncoras (arquivo não
> existe fora da worktree) — isso é esperado, não é órfã real.
>
> **Não duplica `dominio-termo-aceite`** — aquele mapa cobre o desvio *dentro* do aceite
> (`desviaParaPagamentoCartao`/`assumeAceite`, elegibilidade no helper); esta skill cobre o que
> acontece *depois*: tokenização, webhook, cobrança recorrente e régua de recusa.

## Lambda — gerenciada no console AWS, não em repositório

A lambda que recebe o webhook da Pagar.me e reencaminha ao CIT é **gerenciada no console da AWS**,
não é deploy de imagem/repositório — o repositório GitLab `pagarme-webhook` (que hoje só tem um
README de template) **não mede a existência dela**: a função existe e roteia hoje mesmo estando o
repo vazio. Antes de tratar "repo vazio" como bloqueante de entrega, confirmar no console AWS se a
função está publicada — só a **origem de versionamento** dela é que falta.

## Desenho de sistemas (visão de 1 frase por salto)

CIT monta um JWT e manda o cliente ao **checkout** → checkout tokeniza o cartão na **Pagar.me** e
cria o pedido → a **lambda AWS** recebe o retorno da Pagar.me e reencaminha por webhook para o CIT
(3 destinos/tentativas — não é o CIT quem chama a Pagar.me na primeira cobrança) → CIT processa o
webhook, dispara o ganho (rota própria, fora do `termo-aceite/`) e passa a cobrar a mensalidade
**avulsamente**, mês a mês, direto na Pagar.me (sem usar `subscription` nativa).

## Canal JWT CIT→checkout

`PagamentoCartaoTermoLib.php` monta a URL assinada para o checkout:

- `CHECKOUT_JWT_TOKEN` ausente é fail-closed — lança exceção antes de gerar o link
  (`application/libraries/PagamentoCartaoTermoLib.php:605-611`, worktree).
- Claims `iss`/`exp` vêm de `TERMO_CARTAO_JWT_ISS`/`TERMO_CARTAO_JWT_EXPIRACAO`
  (`PagamentoCartaoTermoLib.php:633-634`).
- A URL final troca o token pelo placeholder `{jwt}` na última barra
  (`PagamentoCartaoTermoLib.php:732,743`).

Tokenização em si (BIN, `card_token`/`card_id`) acontece no repositório **checkout**
(`application/libraries/PagarmeLib/PagarmeLib.php`, `application/controllers/Compra.php`) — fora
do escopo de âncora desta skill (repositório diferente do cit); tratar como referência de memória,
não como fato travado por `kb.sh`.

## Retorno por webhook via lambda (dentro do aceite)

- Rota: `termo-aceite/webhook-pagamento-cartao` → `PagamentoCartaoTermo::webhook` (`routes.php:102`
  e `application/controllers/PagamentoCartaoTermo.php:27`, worktree).
- `WebhookPagamentoCartaoTermoLib::processa($evento, $segredoRecebido)`
  (`application/libraries/WebhookPagamentoCartaoTermoLib.php:38`) reidrata `payload_aceite` e, na
  aprovação, delega para `PosPagamentoCartaoLib::executaAcoesPosPagamento($termoAceite, $post, $registroCartaoId)`
  (`WebhookPagamentoCartaoTermoLib.php:202` → `application/libraries/Cartao/PosPagamentoCartaoLib.php:38`).
- A leitura do envelope da Pagar.me e a decisão sobre o segredo são um **serviço estático puro**
  compartilhado entre o webhook do aceite e o webhook da mensalidade —
  `EventoPagarmeCartao` (`application/libraries/Cartao/EventoPagarmeCartao.php:21`), com o
  docblock da classe (`:9-19`) avisando que a **ordem de checagem do segredo muda por consumidor**:
  o aceite projeta o payload para auditoria antes de autenticar (comportamento histórico
  preservado); o webhook da mensalidade autentica primeiro.
- Segredo do aceite: `TERMO_CARTAO_WEBHOOK_SECRET` (`application/config/constants/pagamento_cartao_termo.php:56`).
- Idempotência: `processado_em` + unique `(termo_aceite_token, pagarme_order_id)` na tabela
  satélite `termo_aceite_pagamento_cartao` (ver `dominio-termo-aceite`).

## Ganho por cartão — rota própria, fora do `termo-aceite/`

`ganho-cartao` → `GanhoCartao::processaGanhoCartao_post` (`routes.php:200` e
`application/controllers/GanhoCartao.php:36`) → `Cartao/GanhoCartaoLib::processa`
(`application/libraries/Cartao/GanhoCartaoLib.php:53`). Autenticado por `Authorization: Bearer`
contra `GANHO_CARTAO_WEBHOOK_SECRET` (`pagamento_cartao_termo.php:90`), fail-closed por cobrança
aprovada no CIT. Whitelist e restrição de método no `SessionHook` — ver `dominio-superficie-publica`
(seção "Classe na whitelist"), não duplicado aqui.

## Cobrança avulsa mensal — motor de cobrança (sem recorrência Pagar.me)

`MotorCobrancaCartaoLib` (`application/libraries/Cartao/MotorCobrancaCartaoLib.php:21`) roda a
régua de cobrança mês a mês, **sem usar `subscription` nativa da Pagar.me** — cada cobrança é um
`order` avulso:

- `executa($modo, $limite)` (`:47`) é o ponto de entrada da rotina.
- `envia($movimento, $cofre, $linha)` (`:401`) é o **ponto de não-retorno**: relê `valor_liquido`
  da linha **reservada** (não do candidato listado no início da rodada — evita cobrar valor
  desatualizado), marca posse via `marcaEnvioIniciado` (pré-condição do POST,
  `affected_rows() === 1`) e só então chama `pagarmecobrancaclient->criaOrder(...)` (`:416-419`) —
  comentário no código (`:401-408`) documenta que duas leituras do mesmo dinheiro fariam o webhook
  acusar divergência com tolerância zero e travar a linha em `a_conferir`.
- Elegibilidade de quem entra na régua: `ElegibilidadeCobrancaCartaoLib::candidatos`/`avalia`
  (`application/libraries/Cartao/ElegibilidadeCobrancaCartaoLib.php:44,143`).
- O retorno da cobrança da mensalidade chega por webhook **separado** do webhook do aceite:
  `cobranca-cartao/webhook` → `CobrancaCartaoWebhook::webhook` (`routes.php:103` e
  `application/controllers/CobrancaCartaoWebhook.php:29`), com comentário explícito no código
  (`:44`): **"fatal vira 500 e a lambda retenta"** — confirma que a lambda AWS reencaminha o
  webhook e trata erro 500 como sinal de nova tentativa (a contagem exata de tentativas da lambda
  não foi conferida nesta sessão — origem é memória de sessão, marcar como não verificado por
  código se precisar de precisão).
- A ligação ao Omie/CRM é por `CMOVIMENTOS`/`DATAVENCIMENTO`, não por assinatura da Pagar.me — é
  esse desenho que sustenta "sem recorrência Pagar.me": quem dita quando cobrar é o vencimento do
  título no CRM, não um ciclo da adquirente.

## Régua de recusa — histórico auditável + observação no CRM

`ReguaRecusaCartaoLib` (`application/libraries/Cartao/ReguaRecusaCartaoLib.php:25`), docblock
(`:5-23`) declara o contrato exato:

- Entrega **histórico auditável por tentativa** e **um e-mail no esgotamento** — não existe tela
  própria; a tela de retentativa manual **não lê** esta tabela (ligar as duas é card à parte).
- O estágio vem da coluna `tentativa` da linha de controle (nunca `COUNT(*)`) — unicidade real é
  `UNIQUE (idemp, id_movimento, tentativa)`.
- `registra($linhaCobranca, $motivoBruto)` (`:46`) grava o histórico e, via
  `registraObservacaoCrm($linha, $classificacao, $estagio, $tentativa, $idemp, $idMovimento)`
  (`:238`), anota no CRM **duas tabelas legíveis por humano**: `CMOVIMENTOSLOG` (log na tela do
  movimento) e `CCLIFORANOTACAO` (anotação na ficha do cliente) — best-effort, falha em silêncio
  (log) sem derrubar o webhook; a tabela auditável é que é fonte de verdade.
- **Não chama a Pagar.me e não dispara ganho** — a régua esgotada é por movimento e não bloqueia a
  competência seguinte; quem interrompe o ciclo é a suspensão por inadimplência (fora desta skill).

### Pendência declarada do lado Omie (docblock `:16-21`, comentário `:113-115`)

**Não escreve no Omie.** O movimento não guarda `codigo_lancamento_omie` e `CODOSOMIE` **não é
chave segura de título** — anotar a recusa no título do Omie fica como pendência, **fora desta
entrega**. Se um card pedir "mostrar a recusa no Omie", a resposta correta é "ainda não existe
elo seguro para isso" — não inventar um `UPDATE` por `CODOSOMIE`.

## Decisões operacionais fechadas (conta Pagar.me — config externa, não verificável por código)

Respostas de Wilker/Gustavo (19/08/2026) que fixam o que **não** se implementa no CIT — não têm
âncora `arquivo:linha` porque são configuração da conta Pagar.me/checkout, não código do cit:

- Conta é **modelo gateway**, **parcela única**, **captura automática**, `statement_descriptor`
  fixo **"Solides"**; **antifraude ligado na requisição do checkout** — nenhum desses parâmetros é
  configurado no CIT.
- Pagar.me **não limita cliente por documento** — documentos duplicados podem ter cartões
  diferentes; a regra de negócio é **considerar sempre o último cartão usado**, nunca supor
  cadastro único por CPF/CNPJ.
- **Retentativa automática de cobrança recusada foi descartada** de propósito ("geralmente falha; o
  ideal é comunicar o cliente antes"): o desenho aprovado é observação no Omie/CRM (ver
  `ReguaRecusaCartaoLib` acima) + botão de retentativa manual numa tela própria, nunca reprocessar
  sozinho.
- `chargeback.received` **não é tratado nesta fase** — pertence a uma frente futura de
  cancelamento/estorno.

## Armadilha — condicional de ganho por cartão precisa ser fail-closed (achado de card, ver workflow HubSpot)

O ganho por cartão só deve disparar com pagamento aprovado. Uma condicional de workflow escrita
como **negação** ("dispara SE `forma_de_pagamento` ≠ 'Cartão de crédito' OU
`status_pagamento_cartao` = 'Aprovado'") é **fail-open**: se a escrita da propriedade
`status_pagamento_cartao` falhar silenciosamente (`publicaAguardandoPagamentoNoDeal` loga e segue,
não lança — `application/libraries/PagamentoCartaoTermoLib.php:527-574`, worktree
`161899_etapa_5_8_11_12_pos_venda`), a propriedade fica vazia,
o primeiro ramo da negação é satisfeito e o ganho sai **sem pagamento confirmado** — efeito
irreversível (base e cadastro criados de graça). A forma correta é **lista afirmativa**: disparar
SE `status_pagamento_cartao = 'Aprovado'` OU `forma_de_pagamento` IN ('Boleto', 'Transferência').
Esse desenho vive no workflow do HubSpot (fora do repositório, não anexável por `arquivo:linha`) —
ao revisar ou recriar o workflow de ganho, exigir a forma afirmativa e um alerta ativo para
propriedade vazia, não confiar em "≠ Cartão de crédito". Ver `dominio-termo-aceite` §
"`forma_de_pagamento` no HubSpot" para a divergência de grafia/enumeração por portal, que agrava o
risco se a condicional comparar string em vez de usar a enumeração do portal certo.

## Segredos e rotação

Três segredos de webhook, todos com padrão de rotação (`_ANTERIOR` cobre a janela de troca):

| Constante | Onde | Cobre |
|---|---|---|
| `TERMO_CARTAO_WEBHOOK_SECRET` | `pagamento_cartao_termo.php:56` | webhook do aceite |
| `GANHO_CARTAO_WEBHOOK_SECRET` | `pagamento_cartao_termo.php:90` | rota `ganho-cartao` |
| `COBRANCA_CARTAO_WEBHOOK_SECRET` + `COBRANCA_CARTAO_WEBHOOK_SECRET_ANTERIOR` | `application/config/constants/cobranca_cartao.php:46-47` | webhook da mensalidade — o único dos três com janela de rotação dupla (`_ANTERIOR` vazio na operação normal) |

## Rotas (worktree `161899_etapa_5_8_11_12_pos_venda`, `application/config/routes.php`)

| Rota | Destino | Linha |
|---|---|---|
| `termo-aceite/webhook-pagamento-cartao` | `PagamentoCartaoTermo/webhook` | `:102` |
| `cobranca-cartao/webhook` | `CobrancaCartaoWebhook/webhook` | `:103` |
| `ganho-cartao` | `GanhoCartao/processaGanhoCartao` | `:200` |

## Acervo — onde já foi estudado

`docs/analises/cartao-credito-pagarme/` tem ~60 documentos da Fase 1 (arquitetura, contratos C2–C8,
levantamento de ambiente, checklist de testes). Não duplicar aqui — pontos de entrada úteis:

| Assunto | Documento |
|---|---|
| Contrato do webhook da lambda | `docs/analises/cartao-credito-pagarme/162988-Contrato-Webhook-Lambda.md` |
| Metadata e roteamento da lambda | `docs/analises/cartao-credito-pagarme/161899-Contrato-C2-Metadata-Roteamento-Lambda.md` |
| Validação do fluxo Omie/CMOVIMENTOS | `docs/analises/cartao-credito-pagarme/161899-Validacao-Fluxo-Omie-Cmovimentos.md` |
| Motor de cobrança avulsa (card 4b) | `docs/analises/cartao-credito-pagarme/161899-Card-4b-Motor-Cobranca-Avulsa.md` |
| Pagar.me como motor de cobrança — conflito com retentativa nativa | `docs/analises/cartao-credito-pagarme/pagarme-como-motor-de-cobranca.md` |
| Auditoria ganho por cartão vs. Pagar.me | `docs/analises/cartao-credito-pagarme/auditoria-ganho-cartao-vs-pagarme.md` |

Busca no acervo: `.claude/scripts/kb.sh buscar <termo>`.

## Cruzamento com outros mapas — não duplicar

- **`dominio-termo-aceite`** § "Pagamento via cartão no aceite": o desvio de fluxo *dentro* do
  aceite (`retomaPagamentoPendente`/`assumeAceite`, elegibilidade em cascata no helper). Esta skill
  começa **depois** — no que acontece uma vez que o desvio já aconteceu.
- **`dominio-superficie-publica`**: whitelist do `SessionHook` para `PagamentoCartaoTermo` e
  `GanhoCartao` — não repetir linha aqui, a fonte é aquele mapa.

## Manutenção

Ao fechar um card desta feature (161899) antes do merge para `master`, atualizar a worktree citada
no topo se a "principal" mudar, e reancorar o que o merge deslocar (`kb.sh verificar` só alcança
âncora dentro do repositório principal — depois do merge, rodar `kb.sh ancorar` de novo para travar
o que hoje está fora do lock).
