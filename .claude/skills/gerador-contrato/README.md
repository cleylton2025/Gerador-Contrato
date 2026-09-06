# Gerador de Contrato — skill para Claude

Skill que transforma uma entrevista curta com o advogado em um contrato completo,
diagramado em **visual law**, entregue em **PDF** (padrão) ou **DOCX**.

Funciona de três formas:

- **com o modelo do próprio advogado** — o contrato dele, automatizado e diagramado;
- **com um modelo redigido pelo Claude** — quando ele não tem modelo ou quer um melhor;
- **com uma ficha anterior** — regeração em segundos, trocando só o que muda.

## Instalação

**Claude Code (usuário)** — vale em todos os projetos:

```bash
mkdir -p ~/.claude/skills
cp -r gerador-contrato ~/.claude/skills/
```

**Em um projeto específico** — copie para `.claude/skills/gerador-contrato/` do projeto.

**Claude.ai / Claude Desktop** — Configurações → Capabilities → Skills → carregue a pasta
compactada (`zip -r gerador-contrato.zip gerador-contrato`).

Depois é só pedir, em linguagem natural:

> "Monta um contrato de honorários para a cliente Maria, ação de cobrança,
> entrada de R$ 2.000 e 3x de R$ 800."

## Configuração de uma vez só

Copie `assets/escritorio-exemplo.json` para `~/.claude/gerador-contrato/escritorio.json`
e preencha com os dados do seu escritório (nome, CNPJ, endereço, logo, PIX, cores,
signatário). A skill passa a usar isso sozinha, e nunca mais pergunta.

## Uso direto do script (sem conversa)

```bash
python3 scripts/gerar_contrato.py ficha.json --formato pdf
python3 scripts/gerar_contrato.py ficha.json --formato ambos --saida ./contratos
```

Formatos: `pdf` (padrão) · `docx` · `ambos` · `html`.

## Requisitos

- **Python 3.8+** — sem bibliotecas de terceiros.
- **PDF**: Google Chrome, Chromium, WeasyPrint **ou** LibreOffice (o script procura
  sozinho, nessa ordem). Sem nenhum deles, o HTML é gerado e você imprime em PDF pelo
  navegador (Ctrl+P).
- **DOCX**: nada. O `.docx` é escrito nativamente em OOXML, com tabelas, cores e
  cabeçalho — abre no Word, no Google Docs e no LibreOffice, totalmente editável.

## Estrutura

```
gerador-contrato/
├── SKILL.md                       fluxo que o Claude segue
├── referencias/
│   ├── 01-entrevista.md           roteiro de perguntas por tipo de contrato
│   ├── 02-anatomia-e-padroes.md   esquema da ficha e tipos de bloco
│   ├── 03-visual-law.md           princípios de legal design aplicados
│   ├── 04-biblioteca-clausulas.md cláusulas-base com alertas éticos (OAB/CDC)
│   └── 05-modelo-do-advogado.md   como automatizar um modelo já existente
├── assets/
│   ├── ficha-exemplo.json         contrato de honorários completo (padrão-ouro)
│   ├── escritorio-exemplo.json    configuração do escritório
│   └── estilo.css                 folha de estilo de visual law
└── scripts/
    ├── gerar_contrato.py          ficha.json → HTML → PDF/DOCX
    ├── render_docx.py             renderização em DOCX
    └── docx_writer.py             escritor OOXML sem dependências
```

## Aviso

O documento gerado é **minuta**. A revisão, a adequação ao caso concreto e a
responsabilidade profissional são do advogado que o assina. A skill sinaliza pontos de
atenção (percentual de êxito elevado, foro de eleição em relação de consumo, multa acima
do teto do CDC), mas não substitui o juízo do profissional.

## Licença

MIT — use, adapte e compartilhe.
