# -*- coding: utf-8 -*-
"""
Escritor de .docx (OOXML) sem dependências — espelha o layout de visual law do HTML.

Usado por gerar_contrato.py. Gera um Word realmente editável: seções em faixa
colorida, tabelas de partes e honorários, caixas de destaque e assinaturas.
"""

import os
import re
import struct
import zipfile
from xml.sax.saxutils import escape as _esc

# ── medidas ────────────────────────────────────────────────────────────────
A4_W, A4_H = 11906, 16838          # twips
MARG = dict(top=1800, right=1020, bottom=1180, left=1020, header=567, footer=567)
CW = A4_W - MARG["left"] - MARG["right"]        # largura útil
EMU = 9525                                       # 1 px = 9525 EMU

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')


def esc(t):
    return _esc("" if t is None else str(t))


def hexcor(c, padrao):
    c = (c or padrao).lstrip("#").upper()
    return c if re.fullmatch(r"[0-9A-F]{6}", c) else padrao.lstrip("#").upper()


# ── runs e parágrafos ──────────────────────────────────────────────────────

def _run(texto, bold=False, sz=21, cor="222222", fonte="Segoe UI", realce=None, quebra=False):
    rpr = [f'<w:rFonts w:ascii="{esc(fonte)}" w:hAnsi="{esc(fonte)}"/>']
    if bold:
        rpr.append("<w:b/>")
    rpr.append(f'<w:color w:val="{cor}"/>')
    rpr.append(f'<w:sz w:val="{int(sz)}"/><w:szCs w:val="{int(sz)}"/>')
    if realce:
        rpr.append(f'<w:shd w:val="clear" w:fill="{realce}"/>')
    br = "<w:br/>" if quebra else ""
    return (f'<w:r><w:rPr>{"".join(rpr)}</w:rPr>{br}'
            f'<w:t xml:space="preserve">{esc(texto)}</w:t></w:r>')


def runs_marcados(texto, sz=21, cor="222222", fonte="Segoe UI", bold_base=False):
    """Converte **negrito**, \\n e [[PREENCHER: x]] em runs."""
    if texto is None:
        return ""
    out = []
    for i, linha in enumerate(str(texto).split("\n")):
        primeiro = True
        pedacos = re.split(r"(\*\*.+?\*\*|\[\[\s*PREENCHER\s*:.+?\]\])", linha, flags=re.S)
        for p in pedacos:
            if not p:
                continue
            quebra = (i > 0 and primeiro)
            if p.startswith("**") and p.endswith("**"):
                out.append(_run(p[2:-2], True, sz, cor, fonte, quebra=quebra))
            elif p.startswith("[["):
                rot = re.sub(r"^\[\[\s*PREENCHER\s*:\s*|\s*\]\]$", "", p)
                out.append(_run(f"⚠ PREENCHER: {rot}", True, sz, "7A5C00", fonte,
                                realce="FFF3B0", quebra=quebra))
            else:
                out.append(_run(p, bold_base, sz, cor, fonte, quebra=quebra))
            primeiro = False
        if not pedacos or all(not p for p in pedacos):
            out.append(_run("", bold_base, sz, cor, fonte, quebra=(i > 0)))
    return "".join(out)


JC = {"justificado": "both", "centro": "center", "esquerda": "left", "direita": "right"}


def para(conteudo_runs, align="justificado", after=120, before=0, indent=0,
         manter_junto=False):
    ppr = ["<w:keepNext/>"] if manter_junto else []
    ppr.append(f'<w:spacing w:before="{before}" w:after="{after}" w:line="276" '
               f'w:lineRule="auto"/>')
    if indent:
        ppr.append(f'<w:ind w:left="{indent}" w:hanging="{min(indent, 200)}"/>')
    ppr.append(f'<w:jc w:val="{JC.get(align, "both")}"/>')
    return f'<w:p><w:pPr>{"".join(ppr)}</w:pPr>{conteudo_runs}</w:p>'


def texto_p(texto, **kw):
    est = {k: kw.pop(k) for k in ("sz", "cor", "fonte", "bold_base") if k in kw}
    return para(runs_marcados(texto, **est), **kw)


def vazio(after=80):
    return f'<w:p><w:pPr><w:spacing w:after="{after}"/></w:pPr></w:p>'


def quebra_pagina():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


# ── tabelas ────────────────────────────────────────────────────────────────

def _bordas(cor, sz=6, nenhuma=False):
    if nenhuma:
        return "<w:tcBorders/>"
    lados = "".join(
        f'<w:{l} w:val="single" w:sz="{sz}" w:space="0" w:color="{cor}"/>'
        for l in ("top", "left", "bottom", "right"))
    return f"<w:tcBorders>{lados}</w:tcBorders>"


def celula(conteudo, largura, fundo=None, borda="D8D1CB", sem_borda=False,
           vcenter=True, margens=(110, 110, 110, 110)):
    props = [f'<w:tcW w:w="{int(largura)}" w:type="dxa"/>',
             _bordas(borda, nenhuma=sem_borda)]
    if fundo:
        props.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{fundo}"/>')
    t, r, b, l = margens
    props.append(f'<w:tcMar><w:top w:w="{t}" w:type="dxa"/><w:left w:w="{l}" w:type="dxa"/>'
                 f'<w:bottom w:w="{b}" w:type="dxa"/><w:right w:w="{r}" w:type="dxa"/></w:tcMar>')
    if vcenter:
        props.append('<w:vAlign w:val="center"/>')
    return f'<w:tc><w:tcPr>{"".join(props)}</w:tcPr>{conteudo or vazio(0)}</w:tc>'


def tabela(linhas_html, larguras, cabecalho_repete=False):
    grid = "".join(f'<w:gridCol w:w="{int(w)}"/>' for w in larguras)
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{int(sum(larguras))}" w:type="dxa"/>'
            '<w:tblLayout w:type="fixed"/></w:tblPr>'
            f"<w:tblGrid>{grid}</w:tblGrid>{''.join(linhas_html)}</w:tbl>")


def linha(celulas, cabecalho=False):
    trpr = "<w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>" if cabecalho else \
           "<w:trPr><w:cantSplit/></w:trPr>"
    return f'<w:tr>{trpr}{"".join(celulas)}</w:tr>'


# ── imagem ─────────────────────────────────────────────────────────────────

def tamanho_imagem(caminho):
    """(largura, altura) em px para PNG/JPEG/GIF, sem dependências."""
    with open(caminho, "rb") as f:
        cab = f.read(32)
        if cab[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", cab[16:24])
            return w, h
        if cab[:3] == b"\xff\xd8\xff":
            f.seek(2)
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                marcador = f.read(1)
                while marcador == b"\xff":
                    marcador = f.read(1)
                if not marcador:
                    break
                if marcador[0] in tuple(range(0xC0, 0xC4)) + tuple(range(0xC5, 0xC8)) + \
                        tuple(range(0xC9, 0xCC)) + tuple(range(0xCD, 0xD0)):
                    f.read(3)
                    h, w = struct.unpack(">HH", f.read(4))
                    return w, h
                tam = struct.unpack(">H", f.read(2))[0]
                f.seek(tam - 2, 1)
        if cab[:6] in (b"GIF87a", b"GIF89a"):
            w, h = struct.unpack("<HH", cab[6:10])
            return w, h
    return 400, 130


def imagem_run(rid, larg_px, alt_px, nome="logo"):
    cx, cy = int(larg_px * EMU), int(alt_px * EMU)
    return (
        '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="1" name="{esc(nome)}"/>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:pic><pic:nvPicPr><pic:cNvPr id="1" name="{esc(nome)}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
        "</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>")


# ── empacotamento ──────────────────────────────────────────────────────────

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Default Extension="jpeg" ContentType="image/jpeg"/>
<Default Extension="jpg" ContentType="image/jpeg"/>
<Default Extension="gif" ContentType="image/gif"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
{overrides}
</Types>"""

RELS_RAIZ = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI"/><w:sz w:val="21"/><w:szCs w:val="21"/>
</w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault>
</w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
</w:styles>"""


def escrever_docx(caminho, corpo_xml, cabecalho_xml=None, rodape_xml=None, imagens=None):
    """imagens: lista de (nome_arquivo, bytes, destino) — destino: 'header' ou 'document'."""
    imagens = imagens or []
    overrides = ['<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
                 if cabecalho_xml else "",
                 '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
                 if rodape_xml else ""]

    rels_doc = ['<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>']
    if cabecalho_xml:
        rels_doc.append('<Relationship Id="rIdHdr" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>')
    if rodape_xml:
        rels_doc.append('<Relationship Id="rIdFtr" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>')

    rels_hdr = []
    for i, (nome, _dados, destino) in enumerate(imagens):
        rel = (f'<Relationship Id="rIdImg{i}" Type="http://schemas.openxmlformats.org/'
               f'officeDocument/2006/relationships/image" Target="media/{nome}"/>')
        (rels_hdr if destino == "header" else rels_doc).append(rel)

    def bloco_rels(itens):
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + "".join(itens) + "</Relationships>")

    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES.format(overrides="".join(overrides)))
        z.writestr("_rels/.rels", RELS_RAIZ)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/document.xml", corpo_xml)
        z.writestr("word/_rels/document.xml.rels", bloco_rels(rels_doc))
        if cabecalho_xml:
            z.writestr("word/header1.xml", cabecalho_xml)
            z.writestr("word/_rels/header1.xml.rels", bloco_rels(rels_hdr))
        if rodape_xml:
            z.writestr("word/footer1.xml", rodape_xml)
        for nome, dados, _d in imagens:
            z.writestr(f"word/media/{nome}", dados)


def documento(corpo, tem_cabecalho, tem_rodape):
    ref = ""
    if tem_cabecalho:
        ref += '<w:headerReference w:type="default" r:id="rIdHdr"/>'
    if tem_rodape:
        ref += '<w:footerReference w:type="default" r:id="rIdFtr"/>'
    sect = (f"<w:sectPr>{ref}"
            f'<w:pgSz w:w="{A4_W}" w:h="{A4_H}"/>'
            f'<w:pgMar w:top="{MARG["top"]}" w:right="{MARG["right"]}" '
            f'w:bottom="{MARG["bottom"]}" w:left="{MARG["left"]}" '
            f'w:header="{MARG["header"]}" w:footer="{MARG["footer"]}" w:gutter="0"/>'
            "</w:sectPr>")
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f"<w:document {NS}><w:body>{corpo}{sect}</w:body></w:document>")


def parte_xml(tipo, corpo):
    tag = "w:hdr" if tipo == "header" else "w:ftr"
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f"<{tag} {NS}>{corpo}</{tag}>")
