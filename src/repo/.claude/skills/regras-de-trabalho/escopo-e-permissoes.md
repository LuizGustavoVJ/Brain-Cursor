# Escopo e permissões — referência

Detalhe das 5 regras de [SKILL.md](SKILL.md). Ler por completo **antes de I5**.

## Checkpoint I5 — o que reler antes de tocar código

1. Esta referência inteira (as 5 regras + os exemplos abaixo).
2. O plano aprovado em `docs/implementacoes/plano/` — é ele, e não a conversa, que define o diff.
3. O `plano.html` aprovado em **I2-val**: é o artefato sobre o qual o usuário deu o OK em I4.

Se algum dos três não existir ou não estiver aprovado, **não** há I5. Ordem das etapas e gates:
[`fluxo-completo.md`](../../fluxo-completo.md).

## 1. Escopo completo dentro do repositório aberto

"Só o que foi pedido" limita **iniciativa**, não **completude**. Dentro do repo aberto na IDE,
todo touchpoint que a demanda mapeou entra no mesmo card: controller, model, view, JS, rota,
migration, constante, teste.

Exclusão só existe em duas condições, **as duas juntas**:

- está **registrada** na análise ou no plano, com motivo (ex.: "integração X adiada para card
  posterior"); e
- foi **aprovada pelo humano** — silêncio não é aprovação.

Touchpoint descoberto durante o I5 e fora do plano: registrar na `executada/` e avisar no chat.
Não implementar por conta própria nem apagar do plano.

## 2. Zona livre × zona que exige permissão

**Livre, sem pedir nada:**

- ler qualquer arquivo de qualquer repositório da máquina;
- **copiar ou adaptar** código de outro repositório **para dentro** do workspace aberto —
  o arquivo alterado é do repo atual, então não há autorização a pedir.

**Exige pedido explícito antes:** alterar (editar, criar, apagar, aplicar patch, commitar)
arquivo de **outro** repositório. O que informar no pedido e a exceção permanente do Brain
(`.claude/` e `CLAUDE.md` viajam para todos os repos): **CLAUDE.md** § *Regras de escopo* e
§ *Propagação do Brain*. Git em repositório de fora obedece à mesma regra de git do repo atual —
[`frota/regras.md`](../../frota/regras.md) § *Git*.

## 3. Regra explícita da demanda é literal

Sai exatamente como o card definiu, sem "melhoria" de redação ou de nome:

- texto de termo de aceite e mensagens ao usuário final;
- nome de propriedade, chave de payload, nome de coluna, nome de constante;
- integrações citadas (endpoint, evento, ordem das chamadas);
- rótulos de tela e conteúdo de e-mail.

Renomear variável, arquivo ou função **só** com pedido explícito. Ambiguidade não se resolve por
suposição: vira ponto de esclarecimento no documento da etapa.

## 4. Código em I5 é incremental

- Passo a passo, o menor diff que cumpre o plano.
- Nada de invenção, melhoria não pedida ou refatoração de oportunidade — arquivo legado grande
  não é convite para arrumar a casa; se a refatoração for necessária, ela é **card próprio**
  (ou consulta ao `arquiteto-plano` **no I1**, antes do plano fechar).
- Decisão **análise suficiente** (S5) = **nenhuma** alteração de código.

## 5. Correção não dispensa revalidação

Recusa em **I2-val**, **I6**, **I11** ou **I15** abre um ciclo: corrigir → **revalidar a mesma etapa**
com o subagente validador. Aprovação pelo próprio agente não conta, e gate aprovado antes da
correção não vale para a versão corrigida. Quem valida cada etapa:
[`implementacao/validacao-subagente.md`](../../implementacao/validacao-subagente.md).

Em sustentação, quando S2-S4 é consolidada e o validador recusa **um** dos documentos, revalidar
**somente** o recusado ([`fluxo-completo.md`](../../fluxo-completo.md) § *Validação consolidada*).

## Quando o fluxo não se aplica

Pergunta conceitual, leitura de código sem mudança e pedido explícito do usuário para pular etapa
dispensam o ciclo — a lista completa de exceções é do
[`fluxo-completo.md`](../../fluxo-completo.md) § *Exceções*, não desta skill.
