# motor.py

import docx
import json
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io # [NOVO] Usado para salvar o arquivo em memória

# A lógica agora está dentro de uma função que recebe os dados
def gerar_documento(dados_texto, dados_referencias):
    """
    Função que gera um documento .docx formatado com base nos dados recebidos.
    Retorna o documento em memória.
    """
    
    # 1. Cria um novo documento em branco
    document = docx.Document()

    # 2. Define as margens ABNT
    sections = document.sections
    for section in sections:
        section.top_margin = Cm(3)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2)

    # 3. Define o estilo padrão do documento
    style = document.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = 1.5
    paragraph_format.first_line_indent = Cm(1.25)
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # 4. Adiciona o conteúdo do texto recebido
    for paragraph_text in dados_texto.split('\n\n'):
        document.add_paragraph(paragraph_text)

    # 5. Adiciona e formata a seção de Referências, se houver
    if dados_referencias:
        ref_titulo = document.add_paragraph('REFERÊNCIAS')
        ref_titulo.paragraph_format.first_line_indent = Cm(0)
        ref_titulo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

        for ref in dados_referencias:
            p = document.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

            if ref.get('tipo') == 'livro':
                p.add_run(f"{ref.get('autor', '')}. ")
                p.add_run(ref.get('titulo', '')).bold = True
                p.add_run(f". {ref.get('cidade', '')}: {ref.get('editora', '')}, {ref.get('ano', '')}.")

    # 6. [MUDANÇA CRÍTICA] Salva o documento em um objeto na memória, não em um arquivo
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0) # Volta para o início do "arquivo em memória"

    return file_stream