# -*- coding: utf-8 -*-
"""Renderiza a ficha do contrato em .docx, com o mesmo layout do PDF."""

import os
import re

import docx_writer as D

CW = D.CW
MEIO = CW // 2


def _cores(ficha):
    v = ficha.get("identidade_visual", {}) or {}
    return {
        "primaria": D.hexcor(v.get("cor_primaria"), "1A3A5C"),
        "destaque": D.hexcor(v.get("cor_destaque"), "B12229"),
        "texto": D.hexcor(v.get("cor_texto"), "222222"),
        "fundo_secao": D.hexcor(v.get("fundo_secao"), "EEE6E1"),
        "fundo_caixa": D.hexcor(v.get("fundo_caixa"), "FBF8F5"),
        "borda": D.hexcor(v.get("borda"), "D8D1CB"),
        "cinza": D.hexcor(v.get("cinza"), "6E6964"),
        "fonte": (v.get("fonte_texto") or "Segoe UI").split(",")[0].strip().strip("'\""),
    }


# ── blocos ─────────────────────────────────────────────────────────────────

def b_paragrafo(b, f, c):
    return D.texto_p(b.get("texto", ""), align=b.get("alinhamento", "justificado"),
                     cor=c["texto"], fonte=c["fonte"], after=140)


def b_subtitulo(b, f, c):
    return D.texto_p(b.get("texto", ""), align="esquerda", cor=c["primaria"],
                     fonte=c["fonte"], bold_base=True, after=60, before=140,
                     manter_junto=True)


def b_lista(b, f, c):
    saida = []
    for item in b.get("itens", []):
        runs = D._run("· ", True, 21, c["destaque"], c["fonte"]) + \
               D.runs_marcados(item, cor=c["texto"], fonte=c["fonte"])
        saida.append(D.para(runs, align="justificado", after=50, indent=240))
    return "".join(saida)


def b_nota(b, f, c):
    return D.texto_p(b.get("texto", ""), align="justificado", sz=17,
                     cor=c["cinza"], fonte=c["fonte"], after=140)


def b_caixa(b, f, c):
    dentro = []
    if b.get("texto"):
        dentro.append(D.texto_p(b["texto"], align="justificado", cor=c["texto"],
                                fonte=c["fonte"], bold_base=True, after=60))
    for item in b.get("itens", []):
        runs = D._run("· ", True, 21, c["destaque"], c["fonte"]) + \
               D.runs_marcados(item, cor=c["texto"], fonte=c["fonte"])
        dentro.append(D.para(runs, align="justificado", after=40, indent=200))
    if not dentro:
        return ""
    cel = D.celula("".join(dentro), CW, fundo=c["fundo_caixa"], borda=c["borda"],
                   vcenter=False, margens=(140, 160, 120, 160))
    return D.tabela([D.linha([cel])], [CW]) + D.vazio(120)


def _grade(pares, f, c, larg_rotulo=2600, fundo_rotulo=None):
    linhas = []
    for rot, val in pares:
        cel_r = D.celula(
            D.texto_p(rot, align="esquerda", cor=c["destaque"], fonte=c["fonte"],
                      bold_base=True, sz=19, after=0),
            larg_rotulo, fundo=fundo_rotulo or c["fundo_secao"], borda=c["borda"])
        cel_v = D.celula(
            D.texto_p(val, align="esquerda", cor=c["texto"], fonte=c["fonte"],
                      sz=20, after=0),
            CW - larg_rotulo, borda=c["borda"])
        linhas.append(D.linha([cel_r, cel_v]))
    return D.tabela(linhas, [larg_rotulo, CW - larg_rotulo])


def b_campos(b, f, c):
    pares = [(i.get("rotulo", ""), i.get("valor", "")) for i in b.get("itens", [])]
    return _grade(pares, f, c) + D.vazio(160) if pares else ""


def b_partes(b, f, c):
    partes = f.get("partes", {}) or {}
    linhas = []
    lista = [partes.get("contratada"), partes.get("contratante")] + \
        list(partes.get("outras", []))
    for p in [x for x in lista if x]:
        cel_r = D.celula(
            D.texto_p(p.get("rotulo", ""), align="centro", cor=c["destaque"],
                      fonte=c["fonte"], bold_base=True, sz=20, after=0),
            2700, fundo=c["fundo_secao"], borda=c["borda"])
        corpo = D.para(
            (D._run(p.get("nome", "") + ", ", True, 20, c["texto"], c["fonte"])
             if p.get("nome") else "") +
            D.runs_marcados(p.get("qualificacao", ""), sz=20, cor=c["texto"],
                            fonte=c["fonte"]),
            align="justificado", after=0)
        linhas.append(D.linha([cel_r, D.celula(corpo, CW - 2700, borda=c["borda"],
                                               margens=(140, 130, 140, 130))]))
    return D.tabela(linhas, [2700, CW - 2700]) + D.vazio(120) if linhas else ""


def _tabela_dados(colunas, linhas_dados, larguras, f, c, centralizar=(), destacar=()):
    cabec = []
    for i, col in enumerate(colunas):
        cabec.append(D.celula(
            D.texto_p(col, align="centro" if i in centralizar else "esquerda",
                      cor="FFFFFF", fonte=c["fonte"], bold_base=True, sz=19, after=0),
            larguras[i], fundo=c["primaria"], borda=c["primaria"]))
    linhas = [D.linha(cabec, cabecalho=True)]
    for lin in linhas_dados:
        cels = []
        for i, val in enumerate(lin):
            cor = c["primaria"] if i in destacar else c["texto"]
            cels.append(D.celula(
                D.texto_p(val, align="centro" if i in centralizar else "justificado",
                          cor=cor, fonte=c["fonte"], sz=19,
                          bold_base=(i in destacar), after=0),
                larguras[i], borda="B9B9B9", vcenter=False,
                margens=(110, 120, 110, 120)))
        linhas.append(D.linha(cels))
    return D.tabela(linhas, larguras, cabecalho_repete=True) + D.vazio(140)


def b_tabela(b, f, c):
    cols = b.get("colunas", [])
    if not cols:
        return ""
    n = len(cols)
    larg = b.get("larguras_twips") or [CW // n] * n
    larg[-1] = CW - sum(larg[:-1])
    return _tabela_dados(cols, b.get("linhas", []), larg, f, c,
                         centralizar=set(b.get("centralizar", [])))


def b_honorarios(b, f, c):
    linhas = b.get("linhas", [])
    if not linhas:
        return ""
    dados = [[l.get("modalidade", ""), l.get("valor", ""), l.get("condicao", "")]
             for l in linhas]
    return _tabela_dados(["Modalidade", "Valor", "Condição"], dados,
                         [2170, 1580, CW - 3750], f, c,
                         centralizar={1}, destacar={0, 1})


def b_assinaturas(b, f, c):
    itens = b.get("itens") or f.get("assinaturas", [])
    if not itens:
        return ""
    n = len(itens)
    larg = [CW // n] * n
    larg[-1] = CW - sum(larg[:-1])
    cels = []
    for i, a in enumerate(itens):
        dentro = [D.texto_p("_______________________________", align="centro",
                            cor=c["texto"], fonte=c["fonte"], sz=20, after=60),
                  D.texto_p(a.get("nome", ""), align="centro", cor=c["texto"],
                            fonte=c["fonte"], bold_base=True, sz=20, after=40)]
        for extra in a.get("linhas", []):
            dentro.append(D.texto_p(extra, align="centro", cor=c["cinza"],
                                    fonte=c["fonte"], sz=18, after=30))
        cels.append(D.celula("".join(dentro), larg[i], sem_borda=True, vcenter=False,
                             margens=(0, 120, 0, 120)))
    return D.vazio(600) + D.tabela([D.linha(cels)], larg)


def b_quebra(b, f, c):
    return D.quebra_pagina()


BLOCOS = {
    "paragrafo": b_paragrafo, "subtitulo": b_subtitulo, "lista": b_lista,
    "nota": b_nota, "caixa": b_caixa, "campos": b_campos, "partes": b_partes,
    "tabela": b_tabela, "honorarios": b_honorarios, "assinaturas": b_assinaturas,
    "quebra_pagina": b_quebra,
}


# ── documento ──────────────────────────────────────────────────────────────

def _cabecalho_secao(sec, c):
    num = f'{sec["numero"]}. ' if sec.get("numero") else ""
    dentro = [D.texto_p(num + sec.get("titulo", ""), align="esquerda",
                        cor=c["destaque"], fonte=c["fonte"], bold_base=True,
                        sz=25, after=0, manter_junto=True)]
    if sec.get("subtitulo"):
        dentro.append(D.texto_p(sec["subtitulo"], align="esquerda", cor=c["cinza"],
                                fonte=c["fonte"], sz=17, after=0, before=40,
                                manter_junto=True))
    cel = D.celula("".join(dentro), CW, fundo=c["fundo_secao"], sem_borda=True,
                   vcenter=False, margens=(120, 140, 100, 160))
    return D.tabela([D.linha([cel])], [CW]) + D.vazio(100)


def gerar(ficha, base_dir, caminho_saida):
    c = _cores(ficha)
    esc = ficha.get("escritorio", {}) or {}
    doc = ficha.get("documento", {}) or {}
    imagens = []
    corpo = []

    # ── título ──
    titulo_cel = D.celula(
        D.texto_p(doc.get("titulo", "CONTRATO"), align="esquerda", cor=c["texto"],
                  fonte=c["fonte"], bold_base=True, sz=38, after=0),
        MEIO + 800, sem_borda=True, margens=(80, 120, 80, 0))
    cels = [titulo_cel]
    if doc.get("chamada"):
        cels.append(D.celula(
            D.texto_p(doc["chamada"], align="centro", cor=c["destaque"],
                      fonte=c["fonte"], bold_base=True, sz=22, after=0),
            CW - MEIO - 800, fundo=c["fundo_caixa"], borda=c["borda"],
            margens=(140, 120, 140, 120)))
    else:
        cels.append(D.celula("", CW - MEIO - 800, sem_borda=True))
    corpo.append(D.tabela([D.linha(cels)], [MEIO + 800, CW - MEIO - 800]))
    corpo.append(D.vazio(200))

    if ficha.get("campos_topo"):
        corpo.append(b_campos({"itens": ficha["campos_topo"]}, ficha, c))

    # ── seções ──
    for sec in ficha.get("secoes", []):
        if sec.get("ativa") is False:
            continue
        if sec.get("quebra_antes"):
            corpo.append(D.quebra_pagina())
        if sec.get("titulo"):
            corpo.append(_cabecalho_secao(sec, c))
        for b in sec.get("blocos", []):
            fn = BLOCOS.get(b.get("tipo"))
            if fn:
                corpo.append(fn(b, ficha, c))
        corpo.append(D.vazio(160))

    ja_tem = any(b.get("tipo") == "assinaturas"
                 for s in ficha.get("secoes", []) for b in s.get("blocos", []))
    if ficha.get("assinaturas") and not ja_tem:
        corpo.append(b_assinaturas({}, ficha, c))

    # ── cabeçalho da página (logo + escritório) ──
    hdr_runs = ""
    if esc.get("logo"):
        caminho = esc["logo"]
        if not os.path.isabs(caminho):
            caminho = os.path.join(base_dir, caminho)
        if os.path.exists(caminho):
            ext = os.path.splitext(caminho)[1].lower().lstrip(".") or "png"
            with open(caminho, "rb") as fp:
                dados = fp.read()
            nome = f"logo.{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
            imagens.append((nome, dados, "header"))
            lp, ap = D.tamanho_imagem(caminho)
            alvo_alt = 48
            escala = alvo_alt / float(ap or 1)
            hdr_runs = D.imagem_run("rIdImg0", int(lp * escala), alvo_alt)
    if not hdr_runs and esc.get("nome"):
        hdr_runs = D._run(esc["nome"], True, 22, c["primaria"], c["fonte"])
    cabecalho = D.parte_xml("header", D.para(hdr_runs, align="esquerda", after=60)) \
        if hdr_runs else None

    contato = " · ".join(x for x in [esc.get("endereco"), esc.get("telefone"),
                                     esc.get("email"), esc.get("site")] if x)
    texto_rodape = esc.get("rodape") or contato
    rodape = D.parte_xml("footer",
                         D.texto_p(texto_rodape, align="centro", sz=15,
                                   cor=c["cinza"], fonte=c["fonte"], after=0)) \
        if texto_rodape else None

    D.escrever_docx(caminho_saida, D.documento("".join(corpo), bool(cabecalho),
                                               bool(rodape)),
                    cabecalho, rodape, imagens)
    return caminho_saida
