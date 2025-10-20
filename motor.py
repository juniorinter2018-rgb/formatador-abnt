# motor.py (Versão Definitiva com Lógica de Montagem Refatorada)

import docx
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

def adicionar_paragrafo_pre_textual(document, text, space_before=0, font_size=12, is_bold=False, alignment=WD_ALIGN_PARAGRAPH.CENTER, is_upper=True):
    if text:
        p = document.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        run_text = text.upper() if is_upper else text
        run = p.add_run(run_text)
        run.font.size = Pt(font_size)
        run.bold = is_bold
        p.alignment = alignment

def gerar_documento(info_trabalho, dados_texto, dados_referencias):
    document = docx.Document()

    # --- CONFIGURAÇÃO INICIAL DO DOCUMENTO ---
    style = document.styles['Normal']
    font = style.font; font.name = 'Arial'; font.size = Pt(12)
    for section in document.sections:
        section.top_margin = Cm(3); section.bottom_margin = Cm(2)
        section.left_margin = Cm(3); section.right_margin = Cm(2)

    # --- ELEMENTOS PRÉ-TEXTUAIS (Capa e Folha de Rosto) ---
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

    # --- NOVA LÓGICA DE PROCESSAMENTO E MONTAGEM ---
    
    # 1. PRÉ-PROCESSAMENTO: Analisa o texto e prepara os blocos de conteúdo e o sumário
    paragrafos = dados_texto.split('\n\n')
    blocos_de_conteudo = []
    entradas_sumario = []
    contadores_secao = {'h1': 0, 'h2': 0, 'h3': 0}

    for p_text in paragrafos:
        p_text = p_text.strip()
        if not p_text: continue

        if p_text.startswith('#'):
            texto_base = p_text.lstrip('# ').strip()
            nivel = p_text.count('#')
            texto_formatado = ""
            if nivel == 1:
                contadores_secao['h1'] += 1; contadores_secao['h2'] = 0; contadores_secao['h3'] = 0
                texto_formatado = f"{contadores_secao['h1']} {texto_base.upper()}"
            elif nivel == 2:
                contadores_secao['h2'] += 1; contadores_secao['h3'] = 0
                texto_formatado = f"{contadores_secao['h1']}.{contadores_secao['h2']} {texto_base}"
            elif nivel == 3:
                contadores_secao['h3'] += 1
                texto_formatado = f"{contadores_secao['h1']}.{contadores_secao['h2']}.{contadores_secao['h3']} {texto_base}"
            
            if texto_base:
                entradas_sumario.append(texto_formatado)
                blocos_de_conteudo.append({'type': f'h{nivel}', 'text': texto_formatado})
        elif p_text.startswith('[clonga]'):
            texto_citacao = p_text.replace('[clonga]', '').replace('[fimclonga]', '').strip()
            blocos_de_conteudo.append({'type': 'clonga', 'text': texto_citacao})
        else:
            blocos_de_conteudo.append({'type': 'p', 'text': p_text})

    # 2. MONTAGEM SEQUENCIAL GARANTIDA
    
    # Adiciona o Sumário
    if entradas_sumario:
        document.add_page_break()
        p_sumario = document.add_paragraph("SUMÁRIO")
        if p_sumario.runs: p_sumario.runs[0].bold = True
        p_sumario.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for entrada in entradas_sumario:
            document.add_paragraph(entrada)
    
    # Adiciona o Corpo do Texto
    if blocos_de_conteudo:
        document.add_page_break()
        for bloco in blocos_de_conteudo:
            tipo = bloco['type']
            texto = bloco['text']
            
            p = document.add_paragraph()
            if tipo.startswith('h'): # Se for h1, h2, h3
                run = p.add_run(texto)
                if tipo in ['h1', 'h2']:
                    run.bold = True
            elif tipo == 'clonga':
                p.text = texto
                fmt = p.paragraph_format
                fmt.left_indent = Cm(4); fmt.line_spacing = 1.0
                if p.runs: p.runs[0].font.size = Pt(10)
            elif tipo == 'p':
                p.text = texto
                fmt = p.paragraph_format
                fmt.line_spacing = 1.5
                fmt.first_line_indent = Cm(1.25)
                fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Adiciona as Referências
    if dados_referencias:
        document.add_page_break()
        p_ref = document.add_paragraph('REFERÊNCIAS')
        if p_ref.runs: p_ref.runs[0].bold = True
        p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        dados_referencias.sort(key=lambda x: x.get('autor', ''))
        for ref in dados_referencias:
            p = document.add_paragraph()
            p.paragraph_format.line_spacing = 1.0
            tipo = ref.get('tipo')
            if tipo == 'livro':
                p.add_run(f"{ref.get('autor', '')}. ")
                run_titulo = p.add_run(ref.get('titulo', '')); run_titulo.bold = True
                p.add_run(f". {ref.get('cidade', '')}: {ref.get('editora', '')}, {ref.get('ano', '')}.")
            elif tipo == 'site':
                p.add_run(f"{ref.get('autor', '')}. {ref.get('titulo', '')}. {ref.get('nome_site', '')}, {ref.get('ano', '')}. Disponível em: <{ref.get('url', '')}>. Acesso em: {ref.get('data_acesso', '')}.")
            elif tipo == 'artigo':
                p.add_run(f"{ref.get('autor', '')}. {ref.get('titulo', '')}. ")
                run_revista = p.add_run(ref.get('nome_revista', '')); run_revista.bold = True
                p.add_run(f", v. {ref.get('volume', '')}, n. {ref.get('numero', '')}, {ref.get('paginas', '')}, {ref.get('ano', '')}.")

    # --- SALVA O DOCUMENTO EM MEMÓRIA ---
    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream