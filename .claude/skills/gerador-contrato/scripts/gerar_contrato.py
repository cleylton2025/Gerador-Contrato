#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Contrato — ficha.json  ->  HTML  ->  PDF / DOCX

Uso:
    python3 gerar_contrato.py ficha.json                      # PDF (padrão)
    python3 gerar_contrato.py ficha.json --formato ambos
    python3 gerar_contrato.py ficha.json --formato html --saida ./out

Sem dependências de terceiros para montar o HTML.
Conversão: Chromium/Chrome -> WeasyPrint -> LibreOffice (o que estiver disponível).
"""

import argparse
import base64
import glob
import html as html_mod
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
CSS_PADRAO = os.path.join(AQUI, "..", "assets", "estilo.css")

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

PENDENCIAS = []


# ─────────────────────────────  texto  ─────────────────────────────

def data_extenso(iso):
    """'2026-09-06' -> '6 de setembro de 2026'. Devolve a entrada se não for ISO."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", str(iso or "").strip())
    if not m:
        return str(iso or "")
    a, mes, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{d} de {MESES[mes - 1]} de {a}"


def inline(texto):
    """Escapa HTML e aplica **negrito**, \\n e [[PREENCHER: ...]]."""
    if texto is None:
        return ""
    s = html_mod.escape(str(texto))

    def pend(m):
        rotulo = m.group(1).strip()
        if rotulo not in PENDENCIAS:
            PENDENCIAS.append(rotulo)
        return f'<span class="pendencia">⚠ PREENCHER: {rotulo}</span>'

    s = re.sub(r"\[\[\s*PREENCHER\s*:\s*(.+?)\s*\]\]", pend, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s, flags=re.S)
    return s.replace("\n", "<br>")


def alinhamento_classe(v):
    return {"centro": " centro", "esquerda": " esquerda"}.get(v, "")


# ─────────────────────────────  blocos  ─────────────────────────────

def bloco_paragrafo(b, ficha):
    return f'<p class="par{alinhamento_classe(b.get("alinhamento"))}">{inline(b.get("texto"))}</p>'


def bloco_subtitulo(b, ficha):
    return f'<h3 class="sub">{inline(b.get("texto"))}</h3>'


def bloco_lista(b, ficha):
    itens = "".join(f"<li>{inline(i)}</li>" for i in b.get("itens", []))
    return f'<ul class="lista">{itens}</ul>' if itens else ""


def bloco_nota(b, ficha):
    return f'<p class="nota">{inline(b.get("texto"))}</p>'


def bloco_caixa(b, ficha):
    partes = []
    if b.get("texto"):
        partes.append(f"<p>{inline(b['texto'])}</p>")
    if b.get("itens"):
        partes.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in b["itens"]) + "</ul>")
    return f'<div class="caixa">{"".join(partes)}</div>' if partes else ""


def bloco_campos(b, ficha):
    linhas = "".join(
        f'<tr><td class="rotulo">{inline(i.get("rotulo"))}</td>'
        f'<td>{inline(i.get("valor"))}</td></tr>'
        for i in b.get("itens", [])
    )
    return f'<table class="campos">{linhas}</table>' if linhas else ""


def _parte_html(p):
    nome = p.get("nome", "")
    qual = p.get("qualificacao", "")
    corpo = (f"<strong>{inline(nome)}</strong>, " if nome else "") + inline(qual)
    return (f'<tr><td class="rotulo">{inline(p.get("rotulo", ""))}</td>'
            f"<td>{corpo}</td></tr>")


def bloco_partes(b, ficha):
    partes = ficha.get("partes", {})
    linhas = ""
    for chave in ("contratada", "contratante"):
        if partes.get(chave):
            linhas += _parte_html(partes[chave])
    for extra in partes.get("outras", []):
        linhas += _parte_html(extra)
    return f'<table class="partes">{linhas}</table>' if linhas else ""


def bloco_tabela(b, ficha):
    cols = b.get("colunas", [])
    larguras = b.get("larguras", [])
    centro = set(b.get("centralizar", []))
    cg = ""
    if larguras:
        cg = "<colgroup>" + "".join(f'<col style="width:{w}">' for w in larguras) + "</colgroup>"
    th = "".join(
        f'<th class="{"centro" if i in centro else ""}">{inline(c)}</th>'
        for i, c in enumerate(cols)
    )
    trs = ""
    for linha in b.get("linhas", []):
        tds = "".join(
            f'<td class="{"centro" if i in centro else ""}">{inline(c)}</td>'
            for i, c in enumerate(linha)
        )
        trs += f"<tr>{tds}</tr>"
    return f'<table class="dados">{cg}<thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'


def bloco_honorarios(b, ficha):
    linhas = b.get("linhas", [])
    if not linhas:
        return ""
    trs = ""
    for l in linhas:
        trs += (
            "<tr>"
            f'<td class="destaque">{inline(l.get("modalidade"))}</td>'
            f'<td class="centro destaque">{inline(l.get("valor"))}</td>'
            f'<td>{inline(l.get("condicao"))}</td>'
            "</tr>"
        )
    return (
        '<table class="dados">'
        '<colgroup><col style="width:22%"><col style="width:16%"><col style="width:62%"></colgroup>'
        '<thead><tr><th>Modalidade</th><th class="centro">Valor</th><th>Condição</th></tr></thead>'
        f"<tbody>{trs}</tbody></table>"
    )


def bloco_assinaturas(b, ficha):
    ass = b.get("itens") or ficha.get("assinaturas", [])
    if not ass:
        return ""
    cols = ""
    for a in ass:
        extras = "".join(f"<span>{inline(x)}</span>" for x in a.get("linhas", []))
        cols += (
            '<div class="assinatura"><div class="linha"></div>'
            f'<strong>{inline(a.get("nome"))}</strong>{extras}</div>'
        )
    return f'<div class="assinaturas">{cols}</div>'


def bloco_quebra(b, ficha):
    return '<div class="quebra"></div>'


RENDERIZADORES = {
    "paragrafo": bloco_paragrafo,
    "subtitulo": bloco_subtitulo,
    "lista": bloco_lista,
    "nota": bloco_nota,
    "caixa": bloco_caixa,
    "campos": bloco_campos,
    "partes": bloco_partes,
    "tabela": bloco_tabela,
    "honorarios": bloco_honorarios,
    "assinaturas": bloco_assinaturas,
    "quebra_pagina": bloco_quebra,
}


# ─────────────────────────────  documento  ─────────────────────────────

def data_uri(caminho):
    ext = os.path.splitext(caminho)[1].lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif",
            "svg": "svg+xml", "webp": "webp"}.get(ext, "png")
    with open(caminho, "rb") as f:
        return f"data:image/{mime};base64," + base64.b64encode(f.read()).decode()


def css_variaveis(vis):
    mapa = {
        "cor_primaria": "--primaria", "cor_destaque": "--destaque",
        "cor_texto": "--texto", "fundo_secao": "--fundo-secao",
        "fundo_caixa": "--fundo-caixa", "borda": "--borda", "cinza": "--cinza",
        "fonte_titulo": "--fonte-titulo", "fonte_texto": "--fonte-texto",
        "tamanho_base": "--base", "margem_topo": "--margem-topo",
    }
    regras = [f"  {css}: {vis[k]};" for k, css in mapa.items() if vis.get(k)]
    return ":root{\n" + "\n".join(regras) + "\n}" if regras else ""


def montar_html(ficha, base_dir, css_path):
    esc = ficha.get("escritorio", {})
    doc = ficha.get("documento", {})
    vis = ficha.get("identidade_visual", {})

    with open(css_path, encoding="utf-8") as f:
        css = f.read()
    css += "\n" + css_variaveis(vis)

    # timbre
    logo_html = ""
    if esc.get("logo"):
        caminho = esc["logo"]
        if not os.path.isabs(caminho):
            caminho = os.path.join(base_dir, caminho)
        if os.path.exists(caminho):
            logo_html = f'<img src="{data_uri(caminho)}" alt="">'
        else:
            print(f"  ! logo não encontrada: {caminho}", file=sys.stderr)

    contato = " · ".join(x for x in [esc.get("endereco"), esc.get("telefone"),
                                     esc.get("email"), esc.get("site")] if x)
    timbre = ""
    if logo_html or esc.get("nome"):
        timbre = (
            '<div class="timbre">'
            f"{logo_html}"
            '<div class="escritorio">'
            f'<strong>{inline(esc.get("nome", ""))}</strong>'
            f'{inline(esc.get("cnpj") and "CNPJ " + esc["cnpj"] or "")}'
            "</div></div>"
        )
    rodape_txt = esc.get("rodape") or contato
    rodape = f'<div class="rodape">{inline(rodape_txt)}</div>' if rodape_txt else ""

    # título
    chamada = (f'<div class="chamada">{inline(doc["chamada"])}</div>'
               if doc.get("chamada") else "")
    titulo = (f'<div class="titulo-bloco"><h1>{inline(doc.get("titulo", "CONTRATO"))}</h1>'
              f"{chamada}</div>")

    corpo = [timbre, rodape, titulo]

    if ficha.get("campos_topo"):
        corpo.append(bloco_campos({"itens": ficha["campos_topo"]}, ficha))

    for sec in ficha.get("secoes", []):
        if sec.get("ativa") is False:
            continue
        cab = ""
        if sec.get("titulo"):
            num = f'{sec["numero"]}. ' if sec.get("numero") else ""
            sub = f'<p>{inline(sec["subtitulo"])}</p>' if sec.get("subtitulo") else ""
            cab = f'<div class="secao-cab"><h2>{inline(num + sec["titulo"])}</h2>{sub}</div>'
        blocos = ""
        for b in sec.get("blocos", []):
            fn = RENDERIZADORES.get(b.get("tipo"))
            if fn is None:
                print(f'  ! tipo de bloco desconhecido: {b.get("tipo")}', file=sys.stderr)
                continue
            blocos += fn(b, ficha)
        quebra = " quebra" if sec.get("quebra_antes") else ""
        corpo.append(f'<div class="secao{quebra}">{cab}<div class="secao-corpo">{blocos}</div></div>')

    # assinaturas automáticas se não houver bloco explícito
    ja_tem = any(b.get("tipo") == "assinaturas"
                 for s in ficha.get("secoes", []) for b in s.get("blocos", []))
    if ficha.get("assinaturas") and not ja_tem:
        corpo.append(bloco_assinaturas({}, ficha))

    return (
        "<!DOCTYPE html>\n<html lang=\"pt-BR\"><head><meta charset=\"utf-8\">"
        f'<title>{html_mod.escape(doc.get("titulo", "Contrato"))}</title>'
        f"<style>{css}</style></head><body>{''.join(corpo)}</body></html>"
    )


# ─────────────────────────────  conversão  ─────────────────────────────

def achar_chromium():
    for var in ("CHROME_PATH", "CHROMIUM_PATH"):
        if os.environ.get(var) and os.path.exists(os.environ[var]):
            return os.environ[var]
    padroes = [
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for p in padroes:
        achados = sorted(glob.glob(p))
        if achados:
            return achados[-1]
    for nome in ("google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "microsoft-edge"):
        c = shutil.which(nome)
        if c:
            return c
    return None


def html_para_pdf(html_path, pdf_path):
    chrome = achar_chromium()
    if chrome:
        perfil = tempfile.mkdtemp(prefix="chrome-contrato-")
        cmd = [chrome, "--headless", "--disable-gpu", "--no-sandbox",
               f"--user-data-dir={perfil}", "--no-pdf-header-footer",
               "--virtual-time-budget=4000",
               f"--print-to-pdf={pdf_path}", "file://" + os.path.abspath(html_path)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        shutil.rmtree(perfil, ignore_errors=True)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
            return "Chromium"
        print("  ! Chromium falhou:", (r.stderr or "")[-400:], file=sys.stderr)

    if shutil.which("weasyprint"):
        r = subprocess.run(["weasyprint", html_path, pdf_path], capture_output=True, text=True)
        if os.path.exists(pdf_path):
            return "WeasyPrint"
        print("  ! WeasyPrint falhou:", (r.stderr or "")[-400:], file=sys.stderr)

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice:
        saida = os.path.dirname(os.path.abspath(pdf_path))
        subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                        "--outdir", saida, html_path], capture_output=True, text=True)
        gerado = os.path.join(saida, os.path.splitext(os.path.basename(html_path))[0] + ".pdf")
        if os.path.exists(gerado):
            if os.path.abspath(gerado) != os.path.abspath(pdf_path):
                shutil.move(gerado, pdf_path)
            return "LibreOffice (layout aproximado)"

    return None


def gerar_docx(ficha, base_dir, docx_path, html_path):
    """DOCX nativo (OOXML, sem dependências). Cai para LibreOffice se falhar."""
    try:
        sys.path.insert(0, AQUI)
        import render_docx
        render_docx.gerar(ficha, base_dir, docx_path)
        if os.path.exists(docx_path) and os.path.getsize(docx_path) > 1000:
            return "nativo"
    except Exception as e:  # pragma: no cover
        print(f"  ! escritor nativo de DOCX falhou: {e}", file=sys.stderr)
    return html_para_docx(html_path, docx_path)


def html_para_docx(html_path, docx_path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None
    saida = os.path.dirname(os.path.abspath(docx_path))
    subprocess.run([soffice, "--headless", "--convert-to", "docx:MS Word 2007 XML",
                    "--outdir", saida, html_path], capture_output=True, text=True)
    gerado = os.path.join(saida, os.path.splitext(os.path.basename(html_path))[0] + ".docx")
    if os.path.exists(gerado):
        if os.path.abspath(gerado) != os.path.abspath(docx_path):
            shutil.move(gerado, docx_path)
        return "LibreOffice"
    return None


# ─────────────────────────────  main  ─────────────────────────────

def nome_base(ficha):
    doc = ficha.get("documento", {})
    if doc.get("nome_arquivo"):
        return re.sub(r'[\\/:*?"<>|]', "-", doc["nome_arquivo"])
    cliente = (ficha.get("partes", {}).get("contratante", {}) or {}).get("nome", "Cliente")
    data = str(doc.get("data", "")).replace("-", ".")
    nome = f"Contrato - {cliente}" + (f" - {data}" if data else "")
    return re.sub(r'[\\/:*?"<>|]', "-", nome)


def main():
    ap = argparse.ArgumentParser(description="Gera contrato a partir de uma ficha JSON.")
    ap.add_argument("ficha")
    ap.add_argument("--formato", default="pdf", choices=["pdf", "docx", "ambos", "html"])
    ap.add_argument("--saida", default=".", help="pasta de saída (padrão: atual)")
    ap.add_argument("--css", default=None, help="CSS alternativo")
    args = ap.parse_args()

    with open(args.ficha, encoding="utf-8") as f:
        ficha = json.load(f)

    base_dir = os.path.dirname(os.path.abspath(args.ficha))
    css_path = args.css or os.path.normpath(CSS_PADRAO)
    os.makedirs(args.saida, exist_ok=True)

    # data por extenso disponível para quem monta a ficha
    doc = ficha.setdefault("documento", {})
    if doc.get("data"):
        doc.setdefault("data_extenso", data_extenso(doc["data"]))

    html = montar_html(ficha, base_dir, css_path)

    base = nome_base(ficha)
    html_path = os.path.join(args.saida, base + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ HTML   : {html_path}")

    gerados = [html_path]

    if args.formato in ("pdf", "ambos"):
        pdf_path = os.path.join(args.saida, base + ".pdf")
        motor = html_para_pdf(html_path, pdf_path)
        if motor:
            print(f"✓ PDF    : {pdf_path}   [{motor}]")
            gerados.append(pdf_path)
        else:
            print("✗ PDF não gerado — nenhum conversor disponível.\n"
                  "  Instale um destes: Google Chrome/Chromium, WeasyPrint (pip install weasyprint)\n"
                  "  ou LibreOffice. O HTML acima abre no navegador e imprime em PDF (Ctrl+P).",
                  file=sys.stderr)

    if args.formato in ("docx", "ambos"):
        docx_path = os.path.join(args.saida, base + ".docx")
        motor = gerar_docx(ficha, base_dir, docx_path, html_path)
        if motor:
            print(f"✓ DOCX   : {docx_path}   [{motor}]")
            gerados.append(docx_path)
        else:
            print("✗ DOCX não gerado.\n"
                  "  Alternativa: abrir o HTML no Word (Arquivo > Abrir) e salvar como .docx.",
                  file=sys.stderr)

    if PENDENCIAS:
        print("\n⚠ Pendências a preencher no documento:")
        for p in PENDENCIAS:
            print(f"  · {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
