# Trilha A — automatizar o modelo do próprio advogado

Esta é a trilha mais valiosa: o advogado já tem um contrato que ele confia. Nosso
trabalho não é reescrevê-lo — é **transformá-lo em ficha + estilo**, preservando o texto.

## Passo 1 — Ler o modelo

| Formato | Como ler |
|---|---|
| `.docx` | descompacte e leia `word/document.xml`, ou use a skill `docx` se disponível |
| `.pdf`  | extraia o texto (`pdftotext -layout`) ou use a skill `pdf` |
| `.txt` / colado no chat | direto |
| foto/scan | peça o arquivo original; OCR de contrato erra número, e número errado em contrato é grave |

Leia o documento **inteiro** antes de perguntar qualquer coisa.

## Passo 2 — Identificar as variáveis

Percorra o texto marcando o que muda de um cliente para o outro. Os alvos, em ordem de
frequência:

1. Nomes próprios e qualificações (nome, CPF/CNPJ, estado civil, profissão, endereço)
2. Valores em R$ e seus extensos
3. Datas e prazos
4. Percentuais
5. Objeto/descrição do serviço
6. Número de processo, comarca, vara
7. Nome do signatário e OAB

Heurísticas úteis:
- Todo número por extenso entre parênteses acompanha um algarismo — os dois são a mesma
  variável e precisam ser gerados juntos.
- Trechos em CAIXA ALTA no meio do texto costumam ser rótulos de parte (CONTRATANTE),
  não variáveis.
- Espaços em branco, sublinhados (`_____`) e `XXX` no modelo são variáveis explícitas.
- Se o modelo veio de um caso real, **os dados daquele cliente estão lá** — troque todos
  por variáveis e confira se não sobrou nenhum. Este é o erro mais grave e mais comum
  desta trilha: o CPF do cliente anterior sobrevivendo no contrato novo.

## Passo 3 — Identificar os módulos opcionais

Marque as partes do modelo que às vezes entram e às vezes não: cláusula de êxito,
parcelamento, liminar, reajuste, LGPD, fiador. Cada uma vira uma **seção com `"ativa"`**
ou uma linha da tabela de honorários — ligável e desligável na próxima geração.

Pergunte de forma concreta:
> "No seu modelo há cláusula de êxito de 20%. Ela entra sempre, ou é caso a caso?"

## Passo 4 — Mapear para a anatomia

Encaixe as cláusulas do modelo nas 7 seções de `02-anatomia-e-padroes.md`. Reordenar é
permitido e desejável; **reescrever, não** — sem autorização expressa. Se o modelo tiver
uma cláusula que não cabe em nenhuma seção, crie uma seção própria com o título original.

Ao final, mostre um "de-para":

| Cláusula do modelo | Vai para |
|---|---|
| "CLÁUSULA PRIMEIRA – DO OBJETO" | Seção 2 — Objeto e escopo |
| "CLÁUSULA QUARTA – DOS HONORÁRIOS" | Seção 5 — Preço e pagamento (tabela) |

## Passo 5 — Preservar x melhorar

Você **pode**, avisando ao final em uma lista:
- corrigir erro de português, concordância e digitação;
- corrigir remissão legal errada (CPC/73 → CPC/2015, artigo revogado);
- padronizar a grafia dos rótulos das partes;
- quebrar um parágrafo de 20 linhas em três.

Você **não pode**, sem perguntar:
- mudar valor, prazo, percentual ou obrigação;
- suprimir cláusula, mesmo que a considere ruim;
- trocar a redação de uma cláusula por outra da biblioteca;
- adicionar cláusula nova.

Se identificar risco real (cláusula nula, abusiva perante o CDC, ou contrária ao Código
de Ética), **diga com franqueza, com o fundamento**, e proponha a redação alternativa —
mas deixe a decisão com o advogado.

## Passo 6 — Identidade visual do modelo

Se o modelo já tem papel timbrado, logo ou cores, extraia:
- a logo (imagem embutida no `.docx` está em `word/media/`);
- a cor dominante da logo → `cor_primaria`;
- fonte usada no corpo → `fonte_texto`.

Depois mostre lado a lado: "seu modelo atual" x "proposta em visual law", e pergunte se
mantém o layout dele ou adota o novo. Muitos advogados querem manter o timbre e ganhar
só a estrutura — isso é perfeitamente possível: mantenha logo e cores, aplique a
diagramação.
