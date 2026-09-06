# Anatomia do contrato e esquema da ficha

## 1. A anatomia padrão (7 seções)

Contratos que funcionam bem em visual law seguem quase sempre esta ordem. Use-a como
esqueleto tanto na Trilha A (modelo do advogado, reordenado) quanto na Trilha B (do zero).

| # | Seção | Pergunta que ela responde para o leigo |
|---|-------|----------------------------------------|
| 0 | Capa / cabeçalho | Que documento é este e de quando? |
| 1 | Partes | Quem está contratando quem? |
| 2 | Objeto e escopo | O que exatamente está sendo contratado — e o que não está |
| 3 | Deveres do contratado | O que o profissional se compromete a fazer |
| 4 | Deveres do contratante | O que o cliente precisa fazer para o trabalho andar |
| 5 | Preço e pagamento | Quanto, quando e como se paga |
| 6 | Rescisão | Como isso termina, e o que acontece se terminar mal |
| 7 | Foro e disposições finais | Onde se resolve o conflito, e o fecho |

Seções opcionais entram **entre a 5 e a 6**: reajuste, LGPD, confidencialidade,
propriedade intelectual, garantias, sucumbência.

Duas regras de legibilidade que valem mais que qualquer enfeite:

- **Cada seção tem um subtítulo em linguagem simples.** O título é jurídico
  ("DESPESAS E HONORÁRIOS"); o subtítulo é humano ("Estrutura financeira da contratação").
- **Dinheiro vai em tabela, nunca em texto corrido.** Modalidade | Valor | Condição.
  É a única parte do contrato que o cliente lê duas vezes.

## 2. Esquema da ficha (`ficha.json`)

```jsonc
{
  "escritorio": {
    "nome": "Mendes Advocacia",
    "cnpj": "33.773.685/0001-68",
    "endereco": "Av. Rui Barbosa, 746, Sala 102, Centro, Linhares-ES, CEP 29900-072",
    "cidade_uf": "Linhares - ES",
    "telefone": "(27) 99999-9999",
    "email": "contato@escritorio.com.br",
    "site": "www.escritorio.com.br",
    "logo": "logo.jpg",              // caminho relativo à ficha; opcional
    "pix": "33.773.685/0001-68",
    "rodape": "Texto livre do rodapé" // opcional
  },

  "identidade_visual": {             // tudo opcional — há padrão para cada campo
    "cor_primaria":  "#1a3a5c",      // cabeçalhos de seção, tabela de honorários
    "cor_destaque":  "#b12229",      // números de seção, rótulos, bullets
    "cor_texto":     "#222222",
    "fundo_secao":   "#eee6e1",      // faixa do cabeçalho de seção
    "fundo_caixa":   "#fbf8f5",      // caixas de destaque
    "borda":         "#d8d1cb",
    "fonte_titulo":  "Georgia, 'Times New Roman', serif",
    "fonte_texto":   "'Segoe UI', Arial, Helvetica, sans-serif",
    "tamanho_base":  "10.5pt"
  },

  "documento": {
    "titulo": "CONTRATO DE HONORÁRIOS ADVOCATÍCIOS",
    "chamada": "= Leia o documento com atenção =",   // caixa ao lado do título; opcional
    "data": "2026-09-06",                            // ISO; vira "6 de setembro de 2026"
    "cidade_foro": "Linhares - ES",
    "nome_arquivo": "Contrato - Maria da Silva"      // opcional; senão é derivado
  },

  "campos_topo": [                                   // grade rótulo|valor logo abaixo do título
    { "rotulo": "Data",   "valor": "Linhares - ES, 6 de setembro de 2026" },
    { "rotulo": "Objeto", "valor": "ação de cobrança contra a construtora X" }
  ],

  "partes": {
    "contratada":  { "rotulo": "CONTRATADA",
                     "nome": "MENDES ADVOCACIA",
                     "qualificacao": "pessoa jurídica de direito privado, inscrita no CNPJ n. …" },
    "contratante": { "rotulo": "CONTRATANTE / CLIENTE",
                     "nome": "MARIA DA SILVA",
                     "qualificacao": "brasileira, casada, empresária, CPF n. …, residente …" }
  },

  "secoes": [
    {
      "numero": "1",
      "titulo": "QUEM SÃO AS PARTES DESTE CONTRATO",
      "subtitulo": "Identificação objetiva das partes contratantes.",
      "ativa": true,                                 // false = não sai no documento
      "blocos": [ { "tipo": "partes" } ]
    }
  ],

  "assinaturas": [
    { "nome": "CLEYLTON MENDES PASSOS", "linhas": ["OAB/ES 13.595", "Contratado — Mendes Advocacia"] },
    { "nome": "MARIA DA SILVA",         "linhas": ["Contratante / Cliente"] }
  ]
}
```

## 3. Tipos de bloco

Todo bloco é um objeto com `"tipo"`. Dentro de qualquer texto valem:
`**negrito**`, quebra de linha com `\n`, e o marcador de pendência `[[PREENCHER: algo]]`,
que sai destacado em amarelo no documento e é listado ao final da geração.

| `tipo` | Campos | Uso |
|---|---|---|
| `paragrafo` | `texto`, `alinhamento` (`justificado`\|`centro`\|`esquerda`) | corpo do contrato |
| `subtitulo` | `texto` | rótulo dentro da seção ("Honorários", "Taxas judiciais") |
| `lista` | `itens[]` | enumeração simples |
| `caixa` | `texto`, `itens[]` (opcional) | destaque com fundo — escopo, resumo, alerta |
| `campos` | `itens[{rotulo,valor}]` | grade rótulo/valor |
| `partes` | — | renderiza `partes.contratada` e `partes.contratante` lado a lado |
| `tabela` | `colunas[]`, `linhas[[]]`, `larguras[]` (opcional) | qualquer tabela |
| `honorarios` | `linhas[{modalidade,valor,condicao}]` | tabela financeira, com estilo próprio |
| `nota` | `texto` | letra menor, cinza — observações e ressalvas |
| `assinaturas` | — | bloco de firmas (usa `assinaturas` da raiz) |
| `quebra_pagina` | — | força página nova |

## 4. Os 8 eixos de alteração (mapa de manutenção)

Quando o usuário pedir mudança, vá direto ao campo. Nunca refaça a ficha inteira.

| Pedido | Onde mexer |
|---|---|
| "outro cliente" | `partes.contratante`, `campos_topo`, último item de `assinaturas` |
| "outro objeto" | `objeto` dentro dos blocos da seção 2 + `campos_topo` |
| "inclui recurso" / "só extrajudicial" | blocos `caixa`/`lista` da seção de escopo |
| "muda o valor / o parcelamento" | `blocos[tipo=honorarios].linhas` |
| "muda a data / o vencimento" | `documento.data`, `campos_topo`, textos das condições |
| "tira/põe cláusula" | `secoes[].ativa`, ou inserir seção da biblioteca |
| "muda o foro / quem assina" | `documento.cidade_foro`, `assinaturas` |
| "muda a cara do documento" | `identidade_visual`, `escritorio.logo` |

## 5. Validações antes de gerar

- Toda seção tem `numero`, `titulo` e pelo menos um bloco.
- Valores monetários aparecem **em algarismos e por extenso** — "R$ 2.000,00 (dois mil reais)".
- Datas por extenso no corpo, curtas em tabelas.
- Percentuais de êxito também por extenso.
- Nenhum `[[PREENCHER:]]` esquecido sem ser avisado ao usuário.
- Contratante e contratada não podem ter a mesma qualificação (erro clássico de
  copiar-colar de modelo antigo).
