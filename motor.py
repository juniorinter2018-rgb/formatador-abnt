# motor.py

import docx
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import re

# Função auxiliar para adicionar títulos de seção
def adicionar_titulo_secao(document, texto, nivel, contadores):
    texto_base = texto.replace('#', '').strip()
    if nivel == 1:
        contadores['h1'] += 1; contadores['h2'] = 0; contadores['h3'] = 0
        texto_limpo = texto_base.upper()
        texto_formatado = f"{contadores['h1']} {texto_limpo}"
    elif nivel == 2:
        contadores['h2'] += 1; contadores['h3'] = 0
        texto_limpo = texto_base.capitalize()
        texto_formatado = f"{contadores['h1']}.{contadores['h2']} {texto_limpo}"
    elif nivel == 3:
        contadores['h3'] += 1
        texto_limpo = texto_base.capitalize()
        texto_formatado = f"{contadores['h1']}.{contadores['h2']}.{contadores['h3']} {texto_limpo}"
    p = document.add_paragraph()
    run = p.add_run(texto_formatado)
    if nivel <= 2: run.bold = True
    return texto_formatado

# Função auxiliar para adicionar parágrafos com espaçamento e alinhamento
def add_paragraph_with_spacing(document, text, spacing_before=0, font_size=12, is_bold=False, alignment=WD_ALIGN_PARAGRAPH.CENTER):
    if text:
        p = document.add_paragraph()
        p.paragraph_format.space_before = Pt(spacing_before)
        run = p.add_run(text.upper())
        run.font.size = Pt(font_size)
        run.bold = is_bold
        p.alignment = alignment

# Função principal que gera o documento
def gerar_documento(info_trabalho, dados_texto, dados_referencias):
    document = docx.Document()
    sections = document.sections
    for section in sections:
        section.top_margin = Cm(3); section.bottom_margin = Cm(2); section.left_margin = Cm(3); section.right_margin = Cm(2)
    style = document.styles['Normal']
    font = style.font; font.name = 'Arial'; font.size = Pt(12)

    # GERAÇÃO DOS ELEMENTOS PRÉ-TEXTUAIS
    if info_trabalho.get('instituicao'):
        # --- CAPA ---
        add_paragraph_with_spacing(document, info_trabalho.get('instituicao'), 0)
        add_paragraph_with_spacing(document, info_trabalho.get('curso'), 12)
        add_paragraph_with_spacing(document, info_trabalho.get('autor'), 150)
        add_paragraph_with_spacing(document, info_trabalho.get('titulo'), 150, is_bold=True)
        if info_trabalho.get('subtitulo'):
            add_paragraph_with_spacing(document, info_trabalho.get('subtitulo'), 12)
        add_paragraph_with_spacing(document, info_trabalho.get('cidade'), 200)
        add_paragraph_with_spacing(document, info_trabalho.get('ano'), 12)
        document.add_page_break()

        # --- FOLHA DE ROSTO ---
        add_paragraph_with_spacing(document, info_trabalho.get('autor'), 150)
        add_paragraph_with_spacing(document, info_trabalho.get('titulo'), 150, is_bold=True)
        if info_trabalho.get('subtitulo'):
            add_paragraph_with_spacing(document, info_trabalho.get('subtitulo'), 12)
        
        nota_curso = info_trabalho.get('curso', '[Nome do Curso]')
        nota_instituicao = info_trabalho.get('instituicao', '[Nome da Instituição]')
        nota = f"Trabalho de Conclusão de Curso apresentado ao curso de {nota_curso} da {nota_instituicao}, como requisito parcial para a obtenção do título de Bacharel."
        p_nota = document.add_paragraph()
        p_nota.paragraph_format.space_before = Pt(150)
        p_nota.paragraph_format.left_indent = Cm(8)
        p_nota.add_run(nota)
        
        if info_trabalho.get('orientador'):
             add_paragraph_with_spacing(document, f"Orientador(a): {info_trabalho.get('orientador')}", 24, alignment=WD_ALIGN_PARAGRAPH.LEFT, is_bold=True)

        add_paragraph_with_spacing(document, info_trabalho.get('cidade'), 200)
        add_paragraph_with_spacing(document, info_trabalho.get('ano'), 12)
        document.add_page_break()

    # GERAÇÃO DO SUMÁRIO, CORPO E REFERÊNCIAS
    contadores_secao = {'h1': 0, 'h2': 0, 'h3': 0}
    entradas_sumario = []
    corpo_doc = docx.Document()
    
    padrao_clonga = r'\[clonga\](.*?)\[fimclonga\]\s*\((.*?)\)'
    blocos = re.split(padrao_clonga, dados_texto, flags=re.DOTALL)
    for i, bloco in enumerate(blocos):
        if i % 3 == 0: 
            paragrafos = bloco.split('\n\n')
            for paragrafo_texto in paragrafos:
                paragrafo_texto = paragrafo_texto.strip()
                if not paragrafo_texto: continue
                if paragrafo_texto.startswith('### '):
                    titulo = adicionar_titulo_secao(corpo_doc, paragrafo_texto, 3, contadores_secao); entradas_sumario.append(titulo)
                elif paragrafo_texto.startswith('## '):
                    titulo = adicionar_titulo_secao(corpo_doc, paragrafo_texto, 2, contadores_secao); entradas_sumario.append(titulo)
                elif paragrafo_texto.startswith('# '):
                    titulo = adicionar_titulo_secao(corpo_doc, paragrafo_texto, 1, contadores_secao); entradas_sumario.append(titulo)
                else:
                    p = corpo_doc.add_paragraph()
                    partes = re.split(r'(\[c:.*?\])', paragrafo_texto)
                    for parte in partes:
                        if parte.startswith('[c:'):
                            p.add_run(f" ({parte.strip('[c:]').upper()})")
                        else:
                            p.add_run(parte)
                    p.paragraph_format.line_spacing = 1.5
                    p.paragraph_format.first_line_indent = Cm(1.25)
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif i % 3 == 1:
            texto_citacao = bloco.strip()
            autor_citacao = blocos[i+1].strip() if (i+1) < len(blocos) else ""
            p_citacao = corpo_doc.add_paragraph(); p_citacao.add_run(texto_citacao)
            fmt = p_citacao.paragraph_format; fmt.left_indent = Cm(4); fmt.line_spacing = 1.0; fmt.first_line_indent = Cm(0)
            p_citacao.runs[0].font.size = Pt(10)
            p_autor = corpo_doc.add_paragraph(); p_autor.add_run(f"({autor_citacao.upper()})")
            fmt_autor = p_autor.paragraph_format; fmt_autor.left_indent = Cm(4); fmt_autor.line_spacing = 1.0; fmt_autor.first_line_indent = Cm(0)
            p_autor.runs[0].font.size = Pt(10)

    if entradas_sumario:
        document.add_paragraph('SUMÁRIO', style='Heading 1')
        for entrada in entradas_sumario: document.add_paragraph(entrada)
        document.add_page_break()

    for element in corpo_doc.element.body: document.element.body.append(element)

    if dados_referencias:
        document.add_page_break()
        ref_titulo = document.add_paragraph('REFERÊNCIAS')
        ref_titulo.paragraph_format.first_line_indent = Cm(0); ref_titulo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for ref in dados_referencias:
            p = document.add_paragraph(); p.paragraph_format.first_line_indent = Cm(0); p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            tipo = ref.get('tipo')
            if tipo == 'livro':
                p.add_run(f"{ref.get('autor', '')}. ").add_run(ref.get('titulo', '')).bold = True
                p.add_run(f". {ref.get('cidade', '')}: {ref.get('editora', '')}, {ref.get('ano', '')}.")
            elif tipo == 'site':
                p.add_run(f"{ref.get('autor', '')}. {ref.get('titulo', '')}. {ref.get('nome_site', '')}, {ref.get('ano', '')}. Disponível em: <{ref.get('url', '')}>. Acesso em: {ref.get('data_acesso', '')}.")
            elif tipo == 'artigo':
                p.add_run(f"{ref.get('autor', '')}. {ref.get('titulo', '')}. ").add_run(ref.get('nome_revista', '')).bold = True
                p.add_run(f", v. {ref.get('volume', '')}, n. {ref.get('numero', '')}, {ref.get('paginas', '')}, {ref.get('ano', '')}.")

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream