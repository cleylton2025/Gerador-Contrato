---
name: gerador-contrato
description: Gera contratos jurídicos completos, em PDF ou DOCX, com layout de visual law e legal design. Use quando o usuário pedir para criar, montar, redigir, gerar ou adaptar um contrato (honorários advocatícios, prestação de serviços, locação, compra e venda, parceria, confidencialidade/NDA, distrato, aditivo), quando anexar um contrato-modelo próprio pedindo para transformá-lo em modelo automatizado ou "deixar bonito", quando pedir um gerador de contratos, um contrato em visual law, um contrato com identidade visual do escritório, ou quando quiser regerar um contrato já feito trocando cliente, valores, prazos ou cláusulas. NÃO use para peças processuais (petições, recursos), pareceres ou notificações extrajudiciais.
---

# Gerador de Contratos com Visual Law

Transforma uma entrevista curta com o advogado em um contrato final, diagramado em
visual law, entregue em **PDF** (padrão) ou **DOCX**.

O núcleo da skill é uma separação rígida:

```
   FICHA (JSON)          +      ESTILO (CSS)      →   HTML  →  PDF / DOCX
   conteúdo jurídico            identidade visual
   (o que muda a cada           (definida uma vez
    contrato)                    por escritório)
```

Quem gera o contrato mexe **só na ficha**. É isso que dá a economia real de tempo:
o segundo contrato do mesmo tipo sai em segundos, trocando 4 ou 5 campos.

---

## Fluxo obrigatório

### Passo 1 — Descobrir a trilha

Pergunte (uma só pergunta, com as três opções):

> **Como vamos montar este contrato?**
> **A)** Tenho um modelo meu (arquivo .docx/.pdf/texto) e quero automatizá-lo.
> **B)** Não tenho modelo — quero que você redija um, já em visual law.
> **C)** Já tenho uma ficha (`ficha.json`) de um contrato anterior e quero só atualizar.

- **Trilha A** → leia `referencias/05-modelo-do-advogado.md`.
- **Trilha B** → leia `referencias/04-biblioteca-clausulas.md`.
- **Trilha C** → abra a ficha, pergunte só o que mudou, regere. Pule para o Passo 4.

Se o usuário já anexou um modelo na primeira mensagem, assuma a Trilha A e confirme
em uma linha, sem repetir a pergunta.

### Passo 2 — Entrevista

Siga `referencias/01-entrevista.md`. Regras que não se negociam:

1. **Pergunte em blocos, não uma pergunta por vez.** Máximo de 3 rodadas de perguntas.
2. **Nunca pergunte o que dá para inferir** do modelo anexado, do histórico da conversa
   ou de uma ficha anterior. Infira, mostre o que inferiu, e peça confirmação.
3. **Dados do escritório são perguntados uma vez na vida.** Se existir
   `~/.claude/gerador-contrato/escritorio.json` (ou `escritorio.json` na pasta do
   projeto), carregue e não pergunte de novo. Se não existir, colete no fim da
   primeira geração e salve.
4. **Nunca invente CNPJ, OAB, endereço, chave PIX, valor ou data.** Campo faltante vira
   marcador visível `[[PREENCHER: chave PIX]]` no documento, e você avisa a lista de
   pendências ao final.

### Passo 3 — Montar a ficha

Escreva `ficha.json` seguindo `referencias/02-anatomia-e-padroes.md` (o esquema completo
está lá, com todos os tipos de bloco). Use `assets/ficha-exemplo.json` como base — é um
contrato de honorários real, completo, que serve de padrão-ouro.

Antes de gerar, **mostre ao usuário um resumo em tabela** dos campos-chave (partes,
objeto, valores, datas, cláusulas ativadas) e peça o "ok". Não mostre o JSON cru, a
menos que ele peça.

### Passo 4 — Gerar

```bash
python3 scripts/gerar_contrato.py ficha.json --formato pdf
python3 scripts/gerar_contrato.py ficha.json --formato ambos --saida ./contratos
```

`--formato`: `pdf` (padrão) · `docx` · `ambos` · `html` (só para conferir o layout).

O script não tem dependência de terceiros para montar o HTML. Para converter, procura
sozinho, nesta ordem: Chromium/Chrome (`--print-to-pdf`), WeasyPrint, LibreOffice.
DOCX sai via LibreOffice. Se nenhum estiver disponível, ele gera o HTML e diz como
converter — nunca falha em silêncio.

### Passo 5 — Entregar

1. Entregue o arquivo ao usuário (`SendUserFile` quando disponível).
2. Liste as **pendências** (`[[PREENCHER: …]]`) se houver.
3. Diga a frase que fecha o ciclo:
   > "A ficha ficou salva em `ficha.json`. Para o próximo contrato deste tipo, me
   > mande a ficha e diga só o que muda."

---

## Os 8 padrões de alteração

Levantamento feito sobre contratos de escritórios reais: **mais de 90% das edições de
um contrato para o outro caem em 8 eixos**. A ficha é desenhada em cima deles, e é isso
que permite regerar um contrato em uma frase.

| # | Eixo | Campo na ficha | Pedido típico do advogado |
|---|------|----------------|---------------------------|
| 1 | Partes | `partes.contratante` | "mesmo contrato, cliente novo" |
| 2 | Objeto | `objeto` | "agora é para uma ação de usucapião" |
| 3 | Escopo / abrangência | `escopo` | "inclui recurso até segunda instância" |
| 4 | Preço e forma de pagamento | `honorarios.linhas` | "entrada de 2 mil + 5x de 800" |
| 5 | Prazos e datas | `documento.data`, vencimentos | "começa dia 10" |
| 6 | Cláusulas opcionais (liga/desliga) | `secoes[].ativa` | "tira a de êxito, põe LGPD" |
| 7 | Foro e assinaturas | `documento.cidade_foro`, `assinaturas` | "foro de Vitória, quem assina é a Dra. X" |
| 8 | Identidade visual | `identidade_visual` | "com as cores e a logo do escritório" |

Sempre que o usuário pedir uma alteração, **identifique o eixo, mexa só nele e regere**.
Não reescreva o contrato inteiro nem refaça a entrevista.

---

## Regras jurídicas inegociáveis

- **Você não é o advogado responsável.** O documento sai como minuta; a revisão e a
  assinatura são do profissional. Diga isso uma vez, no fim, sem repetir a cada geração.
- **Honorários advocatícios**: respeite o Código de Ética da OAB e a tabela de honorários
  da seccional. Sinalize (sem bloquear) quando o percentual de êxito passar de 30%, ou
  quando houver cláusula que possa ser lida como captação ou quota litis abusiva.
- **Cláusula que não foi pedida não entra.** Se você julgar que falta uma cláusula
  relevante (rescisão, foro, LGPD, sucumbência, multa), **sugira em texto** e só inclua
  depois do "sim".
- **Não altere texto de cláusula do modelo do advogado** sem avisar. Se corrigir
  português, concordância ou remissão legal errada, liste as correções ao final.

---

## Arquivos de apoio

| Arquivo | Quando ler |
|---|---|
| `referencias/01-entrevista.md` | Sempre, no Passo 2 — roteiro de perguntas por tipo de contrato |
| `referencias/02-anatomia-e-padroes.md` | Sempre, no Passo 3 — esquema completo da ficha e tipos de bloco |
| `referencias/03-visual-law.md` | Ao definir/ajustar identidade visual, ou quando o usuário reclamar do layout |
| `referencias/04-biblioteca-clausulas.md` | Trilha B (redigir do zero) e ao sugerir cláusulas |
| `referencias/05-modelo-do-advogado.md` | Trilha A — como extrair variáveis de um modelo existente |
| `assets/ficha-exemplo.json` | Sempre como ponto de partida da ficha |
| `assets/estilo.css` | Só quando for personalizar o visual além das cores |
