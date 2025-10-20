# motor.py (Versão com formatação de referências ABNT corrigida)

import docx
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
from bs4 import BeautifulSoup, NavigableString

def formatar_autor_abnt(autor_str):
    """Formata o nome do autor para o padrão ABNT (SOBRENOME, Nome)."""
    if not autor_str or ',' not in autor_str:
        return autor_str.upper() # Retorna em maiúsculas se o formato for inesperado
    
    partes = autor_str.split(',', 1)
    sobrenome = partes[0].strip().upper()
    # .title() capitaliza a primeira letra de cada nome (ex: "joão carlos" -> "João Carlos")
    nome = partes[1].strip().title() 
    return f"{sobrenome}, {nome}"

def adicionar_paragrafo_pre_textual(document, text, space_before=0, font_size=12, is_bold=False, alignment=WD_ALIGN_PARAGRAPH.CENTER, is_upper=True):
    if text:
        p = document.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        run_text = text.upper() if is_upper else text
        run = p.add_run(run_text)
        run.font.size = Pt(font_size)
        run.bold = is_bold
        p.alignment = alignment

def process_node_recursively(paragraph, node, is_bold=False, is_italic=False):
    if isinstance(node, NavigableString):
        text = str(node).replace('\xa0', ' ')
        if text:
            run = paragraph.add_run(text)
            run.bold = is_bold
            run.italic = is_italic
        return

    new_bold = is_bold or (node.name in ['strong', 'b'])
    new_italic = is_italic or (node.name in ['em', 'i'])
    
    for child in node.children:
        process_node_recursively(paragraph, child, new_bold, new_italic)


def processar_html_para_docx(document, html_string):
    soup = BeautifulSoup(html_string, 'lxml')
    h1_counter = 0
    h2_counter = 0

    for element in soup.body.find_all(recursive=False):
        if not element.get_text(strip=True):
            continue

        p = document.add_paragraph()
        
        if element.name == 'h1':
            h1_counter += 1
            h2_counter = 0
            texto_titulo = f"{h1_counter} {element.get_text(strip=True).upper().replace('Â ', ' ')}"
            run = p.add_run(texto_titulo)
            run.bold = True
        
        elif element.name == 'h2':
            h2_counter += 1
            texto_titulo = f"{h1_counter}.{h2_counter} {element.get_text(strip=True).replace('Â ', ' ')}"
            run = p.add_run(texto_titulo)
            run.bold = True

        elif element.name == 'blockquote':
            fmt = p.paragraph_format
            fmt.left_indent = Cm(4)
            fmt.line_spacing = 1.0
            process_node_recursively(p, element)
            for run in p.runs:
                run.font.size = Pt(10)
        
        else:
            fmt = p.paragraph_format
            fmt.line_spacing = 1.5
            fmt.first_line_indent = Cm(1.25)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            process_node_recursively(p, element)


def gerar_documento(info_trabalho, texto_html, dados_referencias):
    document = docx.Document()
    style = document.styles['Normal']
    font = style.font; font.name = 'Arial'; font.size = Pt(12)
    for section in document.sections:
        section.top_margin = Cm(3); section.bottom_margin = Cm(2)
        section.left_margin = Cm(3); section.right_margin = Cm(2)

    if info_trabalho.get('autor') and info_trabalho.get('titulo'):
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('instituicao'))
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('curso'), 12)
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('autor'), 120)
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('titulo'), 120, is_bold=True)
        if info_trabalho.get('subtitulo'):
            adicionar_paragrafo_pre_textual(document, info_trabalho.get('subtitulo'), 12)
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('cidade'), 150)
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('ano'), 12)
        document.add_page_break()
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('autor'), 0)
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('titulo'), 120, is_bold=True)
        if info_trabalho.get('subtitulo'):
            adicionar_paragrafo_pre_textual(document, info_trabalho.get('subtitulo'), 12)
        nota_curso = info_trabalho.get('curso', '[Nome do Curso]')
        nota_instituicao = info_trabalho.get('instituicao', '[Nome da Instituição]')
        nota = (f"Trabalho de Conclusão de Curso apresentado ao curso de {nota_curso} da {nota_instituicao}, "
                f"como requisito parcial para a obtenção do título de Bacharel.")
        p_nota = document.add_paragraph(); p_nota.paragraph_format.space_before = Pt(100)
        p_nota.paragraph_format.left_indent = Cm(8); p_nota.add_run(nota)
        if info_trabalho.get('orientador'):
            adicionar_paragrafo_pre_textual(document, f"Orientador(a): {info_trabalho.get('orientador')}", 24, alignment=WD_ALIGN_PARAGRAPH.LEFT, is_upper=False)
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('cidade'), 120)
        adicionar_paragrafo_pre_textual(document, info_trabalho.get('ano'), 12)
    
    document.add_page_break()
    processar_html_para_docx(document, texto_html)

    # --- SECÇÃO DE REFERÊNCIAS (COM FORMATAÇÃO ABNT CORRIGIDA) ---
    if dados_referencias:
        document.add_page_break()
        p_ref = document.add_paragraph('REFERÊNCIAS')
        if p_ref.runs: p_ref.runs[0].bold = True
        p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        dados_referencias.sort(key=lambda x: x.get('autor', ''))
        for ref in dados_referencias:
            p = document.add_paragraph()
            p.paragraph_format.line_spacing = 1.0
            
            autor_formatado = formatar_autor_abnt(ref.get('autor', ''))
            # Capitaliza apenas a primeira letra do título
            titulo = ref.get('titulo', '').strip()
            titulo_capitalizado = titulo.capitalize() if titulo else ''
            
            tipo = ref.get('tipo')
            if tipo == 'livro':
                cidade = ref.get('cidade', '').strip().title()
                editora = ref.get('editora', '').strip().title()
                
                p.add_run(f"{autor_formatado}. ")
                run_titulo = p.add_run(titulo_capitalizado)
                run_titulo.bold = True
                p.add_run(f". {cidade}: {editora}, {ref.get('ano', '')}.")

            elif tipo == 'site':
                nome_site = ref.get('nome_site', '')
                p.add_run(f"{autor_formatado}. {titulo_capitalizado}. {nome_site}, {ref.get('ano', '')}. Disponível em: <{ref.get('url', '')}>. Acesso em: {ref.get('data_acesso', '')}.")
            
            elif tipo == 'artigo':
                nome_revista = ref.get('nome_revista', '')
                p.add_run(f"{autor_formatado}. {titulo_capitalizado}. ")
                run_revista = p.add_run(nome_revista)
                run_revista.bold = True
                p.add_run(f", v. {ref.get('volume', '')}, n. {ref.get('numero', '')}, p. {ref.get('paginas', '')}, {ref.get('ano', '')}.")

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream