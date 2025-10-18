# motor.py

import docx
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

def gerar_documento(dados_texto, dados_referencias):
    document = docx.Document()

    sections = document.sections
    for section in sections:
        section.top_margin = Cm(3)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2)

    style = document.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = 1.5
    paragraph_format.first_line_indent = Cm(1.25)
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for paragraph_text in dados_texto.split('\n\n'):
        document.add_paragraph(paragraph_text)

    if dados_referencias:
        ref_titulo = document.add_paragraph('REFERÊNCIAS')
        ref_titulo.paragraph_format.first_line_indent = Cm(0)
        ref_titulo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

        for ref in dados_referencias:
            p = document.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            tipo = ref.get('tipo')

            # --- LÓGICA DE FORMATAÇÃO PARA CADA TIPO ---
            if tipo == 'livro':
                p.add_run(f"{ref.get('autor', '')}. ")
                p.add_run(ref.get('titulo', '')).bold = True
                p.add_run(f". {ref.get('cidade', '')}: {ref.get('editora', '')}, {ref.get('ano', '')}.")
            
            elif tipo == 'site':
                p.add_run(f"{ref.get('autor', '')}. ")
                p.add_run(f"{ref.get('titulo', '')}. ")
                p.add_run(f"{ref.get('nome_site', '')}, {ref.get('ano', '')}. ")
                p.add_run(f"Disponível em: <{ref.get('url', '')}>. ")
                p.add_run(f"Acesso em: {ref.get('data_acesso', '')}.")

            elif tipo == 'artigo':
                p.add_run(f"{ref.get('autor', '')}. ")
                p.add_run(f"{ref.get('titulo', '')}. ")
                p.add_run(ref.get('nome_revista', '')).bold = True
                p.add_run(f", v. {ref.get('volume', '')}, n. {ref.get('numero', '')}, {ref.get('paginas', '')}, {ref.get('ano', '')}.")
            
            # Adicione mais 'elifs' aqui para futuros tipos
            # --------------------------------------------------

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream