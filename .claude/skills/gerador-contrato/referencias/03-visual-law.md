# Visual law e legal design aplicados a contratos

Legal design não é enfeitar contrato. É reduzir o custo cognitivo de quem assina.
Um contrato bem diagramado diminui pergunta de cliente, acelera assinatura e reduz
alegação futura de "eu não entendi o que estava assinando".

## Os 7 princípios que a skill aplica

1. **Hierarquia visível.** Título do documento > cabeçalho de seção > subtítulo interno
   > corpo. Três níveis, no máximo quatro. Mais que isso vira ruído.
2. **Seção numerada com faixa colorida.** O olho encontra "onde fala de dinheiro" em
   dois segundos. Faixa com fundo suave, número e título na cor de destaque.
3. **Subtítulo humano.** Abaixo do título jurídico, uma linha em cinza, em português
   simples, dizendo o que aquela seção faz.
4. **Dinheiro em tabela.** Modalidade | Valor | Condição. Cabeçalho na cor primária,
   texto branco. Nunca esconda valor dentro de parágrafo.
5. **Caixas para o que não pode passar batido.** Escopo, prazos críticos, alertas.
   Fundo claro, borda fina, texto em negrito curto.
6. **Respiro.** Margens generosas, entrelinha 1,45, parágrafos curtos (3 a 5 linhas).
   Página cheia é página não lida.
7. **Linguagem direta no que dá para simplificar.** "O cliente paga as custas" em vez de
   "correrão por conta exclusiva do CONTRATANTE as despesas processuais". Onde a
   precisão técnica for necessária, mantenha o rigor — legibilidade não é imprecisão.

## Paleta

Uma cor primária (institucional, escura), uma de destaque (quente, usada com parcimônia)
e dois tons de fundo. Nada além disso.

| Papel | Padrão | Onde aparece |
|---|---|---|
| Primária | `#1a3a5c` | cabeçalho da tabela de honorários, títulos |
| Destaque | `#b12229` | número da seção, rótulos das partes, bullets |
| Fundo de seção | `#eee6e1` | faixa do cabeçalho de seção |
| Fundo de caixa | `#fbf8f5` | caixas de destaque |
| Borda | `#d8d1cb` | contornos suaves |
| Texto | `#222222` | corpo |

Regra do destaque: se mais de 10% da página estiver na cor de destaque, ela deixou de
destacar. Vermelho/dourado só em pontos nobres.

Ao adotar a identidade do escritório, pegue a cor da logo como primária e escolha a de
destaque por contraste, não por semelhança. Verifique contraste mínimo de 4,5:1 para
texto sobre fundo colorido.

## Tipografia

- **Corpo**: sans-serif, 10,5 a 11pt. Serifada também funciona, se for uma boa serifada.
- **Título do documento**: 20 a 24pt, negrito, caixa alta.
- **Cabeçalho de seção**: 12 a 13pt, negrito, na cor de destaque.
- **Subtítulo da seção**: 8,5 a 9pt, cinza, sem negrito.
- **Tabela**: 9 a 9,5pt.
- **Nota/observação**: 8,5pt, cinza.
- Duas famílias no máximo. Uma, de preferência.

## Página

- A4, margens 20mm laterais, 22mm no topo (mais, se houver papel timbrado), 18mm no pé.
- Logo no cabeçalho, repetida em todas as páginas (é o que a versão em CSS `position:fixed`
  faz na impressão).
- Rodapé discreto com nome do escritório e contato.
- Quebra de página antes de seções longas, para não deixar título órfão no pé.
- Bloco de assinaturas nunca sozinho na última página — deve ter ao menos o fecho do
  contrato acima dele.

## Erros que estragam o resultado

| Erro | Por que dói |
|---|---|
| Ícone/emoji decorativo em cláusula | tira a seriedade sem ganhar clareza |
| Mais de três cores | o leitor perde a pista do que é importante |
| Texto centralizado no corpo | dificulta a leitura contínua; centralize só títulos e fecho |
| Tabela sem cabeçalho repetido | tabela de honorários que vira duas páginas fica ilegível |
| Caixa alta em parágrafo inteiro | 30% mais lento de ler |
| Justificado sem hifenização | rios de espaço em branco no meio da página |

## Personalizando além das cores

`assets/estilo.css` é CSS puro e comentado, dividido em blocos (`@page`, cabeçalho,
seção, caixa, tabela, assinaturas). As cores vêm de variáveis CSS preenchidas a partir
de `identidade_visual` — mexer no CSS só é necessário para mudar estrutura (por exemplo,
partes em coluna única em vez de duas).
