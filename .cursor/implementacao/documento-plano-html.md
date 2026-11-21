# `plano.html` — HTML do plano (I2-html)

**Etapa:** **I2-html** (só trilha completa), logo após o I1-rev e antes da **I2-val** — a validação única do plano.
**Quem produz:** subagente [`escritor-evidencias`](../agents/escritor-evidencias.md) (**opus**).
**Caminho:** `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html`

Guia operacional do ciclo: [fluxo-implementacao.md](fluxo-implementacao.md#ciclo-i2-html--planohtml).
Conteúdo do plano `.md`: [documento-implementacao.md](documento-implementacao.md).

O `plano.html` é o documento que o **usuário lê e posta no card antes de autorizar código**. Ele
não substitui o plano `.md` (que continua sendo a fonte técnica) — ele é a versão **apresentável
e ADO-safe** do mesmo plano, e é sobre **ele** que roda o gate do I4 (**I2-val**).

## Regras que valem para o arquivo inteiro

- **`<style>` canônico:** copiar da skill [evidencias-html-ado](../skills/evidencias-html-ado/SKILL.md)
  (template `template-evidencias.html`) — **não** duplicar CSS aqui nem inventar classes.
  Classes usadas: `.card-meta`, `.info-block`, `.solucao`, `.objetivo`, `.table-wrap`,
  `tr.highlight`, `tr.warn`, `pre.cmd`, `.resultado`, `.footer`.
- **`<body>` sem atributos** — o script de postagem casa `<body>(.*?)</body>` literal.
- **Sem PNG e sem Playwright em I2-html.** Não há código, não há teste executado, não há print:
  quem gera figura é I9/I11/I14. `plano.html` é texto, tabela e fluxo numerado.
- **Mermaid só no `.md`.** O comentário do ADO remove `<style>` e **não renderiza mermaid** —
  diagrama no HTML vira **tabela lado a lado + fluxo numerado** (ver seção 4).
- **Seção não aplicável recebe `N/A + motivo` e NUNCA é apagada.** Apagar seção = **recusa** em I2-val.
- pt-BR, sem caminhos internos (`docs/`, `.md`) no corpo do HTML.

---

## As 13 seções (ordem fixa)

| # | Seção | Conteúdo obrigatório |
|---|-------|----------------------|
| 1 | `h1` do título + `p.card-meta` | Card · Sistema · Ambiente · Data (separador `&nbsp;\|&nbsp;`) |
| 2 | `div.info-block` — **Objetivo e escopo** | Objetivo · escopo · **fora de escopo** em `ul` |
| 3 | **Como funciona hoje** | Tabela **Arquivo · Função/método · Âncora** — o comportamento atual, verificado no código |
| 4 | **Arquitetura Antes × Depois** | **Tabela lado a lado** + **fluxo numerado** (ver abaixo); cada linha marcada `novo`/`alterado`/`removido`/`inalterado` |
| 5 | **Decisões e por quê** | Tabela **Decisão · Alternativas · Por que esta · Custo de reverter** |
| 6 | **Alterações propostas** | Tabela **Arquivo · O que muda · Âncora · Risco** |
| 7 | **Banco e migration** | DDL/DML em `pre.cmd` + tabela/coluna afetada + dado existente; `N/A + motivo` se não houver |
| 8 | **Conformidade e segurança** | Os **8 itens** — nenhum em branco (ver abaixo) |
| 9 | **Impacto na experiência** | O que o usuário final vê mudar (tela, mensagem, e-mail, tempo de resposta); `N/A + motivo` se nada muda |
| 10 | **Matriz de testes por AC** | Tabela **AC · Cenário · Onde (E2E/local/homol) · Como se prova** |
| 11 | **Riscos e rollback** | `div.solucao` com risco → mitigação e o rollback passo a passo |
| 12 | **Registro de gatilhos (externo)** | **Não** citar agente no `plano.html`. As revisões de I1-rev vão no `_processo-revisoes.md` interno (regras.md § 11); aqui, no máximo um comentário HTML apontando para ele |
| 13 | `div.footer` | Identificação do card e da etapa (plano — I2-html) |

---

## Seção 4 — Arquitetura Antes × Depois (esqueleto)

Duas partes, sempre as duas:

**(a) Tabela lado a lado** — uma linha por elemento do fluxo, com a marcação obrigatória:

```html
<div class="table-wrap">
  <table>
    <thead><tr><th>#</th><th>Hoje (antes)</th><th>Proposto (depois)</th><th>Marcação</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>Termo grava aceite e dispara ganho</td><td>Termo grava aceite e chama o checkout</td><td>alterado</td></tr>
      <tr class="highlight"><td>2</td><td>—</td><td>Webhook de pagamento confirma e dispara o ganho</td><td>novo</td></tr>
      <tr><td>3</td><td>Job de conferência diária</td><td>Job de conferência diária</td><td>inalterado</td></tr>
      <tr class="warn"><td>4</td><td>Retentativa manual por planilha</td><td>—</td><td>removido</td></tr>
    </tbody>
  </table>
</div>
```

**Marcação obrigatória em toda linha:** `novo` · `alterado` · `removido` · `inalterado`.
Antes/depois sem marcação = **recusa** em I2-val.

**(b) Fluxo numerado** — a mesma mudança em passos, do gatilho ao efeito final:

```html
<ol>
  <li>Usuário aceita o termo → CIT grava o aceite <em>(alterado)</em></li>
  <li>CIT monta o JWT e redireciona ao checkout <em>(novo)</em></li>
  <li>Checkout tokeniza o cartão e cria o pedido <em>(inalterado)</em></li>
  <li>Webhook retorna ao CIT → CIT dispara o ganho <em>(novo)</em></li>
</ol>
```

Mermaid (se houver) fica **só no plano `.md`** — no HTML ele não renderiza e viraria texto solto.

---

## Seção 5 — Decisões e por quê (esqueleto)

| Decisão | Alternativas | Por que esta | Custo de reverter |
|---------|--------------|--------------|-------------------|
| Cobrança avulsa em CMOVIMENTOS | Recorrência nativa do provedor | Recorrência não suspende no cancelamento | Baixo: desligar a rotina e voltar ao boleto |

Decisão **sem alternativa** ou **sem custo de reverter** = **recusa** em I2-val.

---

## Seção 8 — Conformidade e segurança (8 itens)

Mesma lista respondida no plano `.md` — fonte única:
[documento-implementacao.md](documento-implementacao.md) § *`## Conformidade e segurança` (8 itens)*.
Aqui ela aparece para quem lê o card. Cada item fecha em **`OK`** / **`N/A + por quê`** /
**`Pendência`**; **nenhum em branco** (branco = recusa em I2-val). Reconferida em **I6-rev**.

| # | Item | Resposta |
|---|------|----------|
| 1 | Dado de cartão (PAN, CVV, validade, titular) trafega ou persiste? | OK \| N/A + por quê \| Pendência |
| 2 | Token/credencial: onde nasce, onde vive, quando expira, quem rotaciona | " |
| 3 | Token aparece em URL, log, HTML, `localStorage` ou histórico? | " |
| 4 | Rota nova é pública? Autenticação e autorização | " |
| 5 | Segredo no `.env` (nunca versionado) e no `.env.example` sem valor | " |
| 6 | LGPD: campo, finalidade, retenção, quem acessa | " |
| 7 | Efeito financeiro idempotente (duplo clique, duas abas, reenvio de webhook) | " |
| 8 | Limite de abuso: rate limit, tentativa, enumeração de token | " |

---

## Seção 12 — Registro de gatilhos (externo)

O `plano.html` **não cita agente da frota** (regras.md § 11). A tabela de revisões de I1-rev
(`Especialista · Veredito · Ponto · Onde foi acatado`) vive no **`_processo-revisoes.md`** da
pasta do card, arquivo interno não-entregável. No `plano.html`, esta seção é apenas um comentário:

```html
<!-- Revisões de especialistas (gate de gatilho de artefato): em _processo-revisoes.md, arquivo interno. -->
```

Gatilho de I1-rev que disparou e **não** tem linha no `_processo-revisoes.md` = **recusa** em
I2-val. Gatilhos e retorno fixo dos especialistas:
[`frota/gatilhos.tsv`](../frota/gatilhos.tsv) (`frota.sh gatilhos`).

---

## Validação (I2-val)

`validador-tecnico` (**Opus**) valida o `plano.html` contra o plano `.md`, as revisões de I1-rev e
o checklist de conformidade. Resultado registrado em **`## Validação do plano.html`** no plano `.md`.
Critérios de recusa: [validacao-subagente.md](validacao-subagente.md#ciclo-obrigatório-etapa-i2-val--planohtml).

**Sem `Status: Aprovado` em I2-val: proibido apresentar I3 e proibido pedir o OK do I4.**

---

## Entrega em Pós-I2-val (pergunta antes de postar)

Aprovada a I2-val, o agente pergunta *"Posto eu o `<arquivo>` no card `<n>`, ou te entrego o comando?"* e posta só com "sim" explícito (por postagem); senão entrega o comando. Entrega no chat:

1. **Caminho** do `plano.html` aprovado.
2. **GUID do projeto** do card (campo `System.TeamProject`, obtido no C0).
3. **Comando pronto:**

```bash
ADO_PROJECT=<GUID-do-projeto> python3 .cursor/scripts/ado_update_comment.py <plano.html> <work_item_id> [comment_id]
```

- Sem `comment_id` → **cria** (guardar o `id` impresso); com `comment_id` → **atualiza** (PATCH).
- O script inlina o CSS (o ADO ignora `<style>`); como o `plano.html` **não tem PNG**, não há
  anexo a subir — `ADO_ATTACH` é irrelevante aqui.
- Detalhes e GUIDs conhecidos: skill [azure-devops-cards](../skills/azure-devops-cards/SKILL.md).

Mesmo padrão de entrega da **Pós-S6a**, **Pós-I11** e **Pós-I15**: caminho + GUID + pergunta
**posto eu ou entrego o comando?** — posta só com "sim".

---

## Os três HTML do card

| Arquivo | Etapa | Conteúdo |
|---------|-------|----------|
| `plano.html` | **I2-html** (val. I2-val) | O plano: antes × depois, decisões, conformidade, revisões |
| `evidencias.html` | S3, I9, I11 | Diagnóstico + implementação + E2E + local L01–LN |
| `evidenciashomol.html` | I14, I15 | E2E (mesmo padrão) + homol U01–UN |

Guia dos dois últimos: [documento-evidencias-html.md](documento-evidencias-html.md).

## Checklist do agente antes de chamar a I2-val

- [ ] As **13 seções** presentes, na ordem — nenhuma apagada; não aplicável marcada `N/A + motivo`
- [ ] Seção 4 com **tabela lado a lado** *e* **fluxo numerado**, toda linha marcada
- [ ] Seção 5 com **alternativas** e **custo de reverter** em toda decisão
- [ ] Seção 8 com os **8 itens** respondidos (nenhum em branco)
- [ ] Seção 12 com **toda** revisão disparada em I1-rev + linha dos gatilhos não disparados
- [ ] `<style>` da skill, `<body>` sem atributos, **sem PNG**
- [ ] Caminho correto: `docs/evidencias/html/{tema-slug}/{card-id}-{Titulo-Slug}/plano.html`
