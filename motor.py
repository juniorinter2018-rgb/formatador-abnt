# motor.py (v14 - Revertendo Sumário para Parágrafos Simples)

import io
import re
from reportlab.lib import pagesizes
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, PageBreak, Frame, PageTemplate, NextPageTemplate, KeepTogether
# Remover importações de Table, TableStyle, TA_RIGHT, gray se não usadas em outro lugar
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

# --- CONFIGURAÇÃO INICIAL E ESTILOS ---
styles = getSampleStyleSheet()
PAGE_WIDTH, PAGE_HEIGHT = pagesizes.A4

# Estilos ABNT (removido SumarioPagina)
styles.add(ParagraphStyle(name='CorpoABNT', fontName='Times-Roman', fontSize=12, leading=18, alignment=TA_JUSTIFY, firstLineIndent=1.25*cm, spaceAfter=6))
styles.add(ParagraphStyle(name='CitacaoLonga', fontName='Times-Roman', fontSize=10, leading=12, alignment=TA_JUSTIFY, leftIndent=4*cm, spaceBefore=6, spaceAfter=6))
styles.add(ParagraphStyle(name='CapaTitulo', fontName='Times-Roman', fontSize=14, alignment=TA_CENTER, textColor=black))
styles.add(ParagraphStyle(name='CapaTexto', fontName='Times-Roman', fontSize=12, alignment=TA_CENTER, textColor=black))
styles.add(ParagraphStyle(name='FolhaRostoNota', fontName='Times-Roman', fontSize=10, leading=12, alignment=TA_LEFT, leftIndent=8*cm))
styles.add(ParagraphStyle(name='Referencia', fontName='Times-Roman', fontSize=12, leading=14, alignment=TA_LEFT, spaceAfter=6))
styles.add(ParagraphStyle(name='Titulo1', fontName='Times-Roman', fontSize=12, leading=18, spaceBefore=12, spaceAfter=6, keepWithNext=1, textColor=black))
styles.add(ParagraphStyle(name='Titulo2', fontName='Times-Roman', fontSize=12, leading=18, spaceBefore=12, spaceAfter=6, keepWithNext=1, textColor=black))
styles.add(ParagraphStyle(name='Titulo3', fontName='Times-Roman', fontSize=12, leading=18, spaceBefore=12, spaceAfter=6, keepWithNext=1, textColor=black))
styles.add(ParagraphStyle(name='SumarioItem', fontName='Times-Roman', fontSize=12, leading=14, alignment=TA_LEFT)) # Mantém estilo base


# --- FUNÇÕES DE DESENHO DE PÁGINA (Inalteradas da v12) ---
def draw_page_number_textual(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.saveState(); canvas.setFont('Times-Roman', 10)
    canvas.drawRightString(PAGE_WIDTH - 2*cm, PAGE_HEIGHT - 2*cm, str(page_num))
    canvas.restoreState()

def do_nothing_pretextual(canvas, doc):
    pass

# --- FUNÇÃO PRINCIPAL ---
def gerar_documento(info_trabalho, dados_texto, dados_referencias):
    buffer = io.BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=pagesizes.A4,
                          rightMargin=2*cm, leftMargin=3*cm,
                          topMargin=3*cm, bottomMargin=2*cm)

    # --- FRAMES E TEMPLATES (Inalterado da v12) ---
    frame_padrao = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='frame_normal')
    template_pre = PageTemplate(id='pretextual', frames=[frame_padrao], onPage=do_nothing_pretextual)
    template_corpo = PageTemplate(id='textual', frames=[frame_padrao], onPage=draw_page_number_textual)
    doc.addPageTemplates([template_pre, template_corpo])

    # --- MONTAGEM DA 'STORY' ---
    story = []
    story.append(NextPageTemplate('pretextual'))

    # --- ELEMENTOS PRÉ-TEXTUAIS (Inalterado da v12) ---
    tem_elementos_pre_textuais = bool(info_trabalho.get('instituicao'))
    if tem_elementos_pre_textuais:
        capa_content = [ Spacer(1, 1*cm), Paragraph(info_trabalho.get('instituicao', '').upper(), styles['CapaTexto']), Spacer(1, 0.5*cm), Paragraph(info_trabalho.get('curso', '').upper(), styles['CapaTexto']), Spacer(1, 5*cm), Paragraph(info_trabalho.get('autor', '').upper(), styles['CapaTexto']), Spacer(1, 5*cm), Paragraph(f"<b>{info_trabalho.get('titulo', '').upper()}</b>", styles['CapaTitulo']) ]
        if info_trabalho.get('subtitulo'): capa_content.extend([Spacer(1, 0.5*cm), Paragraph(info_trabalho.get('subtitulo', '').upper(), styles['CapaTexto'])])
        capa_content.extend([ Spacer(1, 7*cm), Paragraph(info_trabalho.get('cidade', '').upper(), styles['CapaTexto']), Spacer(1, 0.5*cm), Paragraph(info_trabalho.get('ano', ''), styles['CapaTexto']) ])
        story.append(KeepTogether(capa_content)); story.append(PageBreak())
        rosto_content = [ Spacer(1, 1*cm), Paragraph(info_trabalho.get('autor', '').upper(), styles['CapaTexto']), Spacer(1, 4*cm), Paragraph(f"<b>{info_trabalho.get('titulo', '').upper()}</b>", styles['CapaTitulo']) ]
        if info_trabalho.get('subtitulo'): rosto_content.extend([Spacer(1, 0.5*cm), Paragraph(info_trabalho.get('subtitulo', '').upper(), styles['CapaTexto'])])
        nota_curso = info_trabalho.get('curso', '[Nome do Curso]'); nota_instituicao = info_trabalho.get('instituicao', '[Nome da Instituição]')
        nota = f"Trabalho de Conclusão de Curso apresentado ao curso de {nota_curso} da {nota_instituicao}, como requisito parcial para a obtenção do título de Bacharel."
        rosto_content.extend([Spacer(1, 4*cm), Paragraph(nota, styles['FolhaRostoNota'])])
        if info_trabalho.get('orientador'): rosto_content.extend([Spacer(1, 2*cm), Paragraph(f"Orientador(a): {info_trabalho.get('orientador')}", styles['CapaTexto'])])
        rosto_content.extend([ Spacer(1, 7*cm), Paragraph(info_trabalho.get('cidade', '').upper(), styles['CapaTexto']), Spacer(1, 0.5*cm), Paragraph(info_trabalho.get('ano', ''), styles['CapaTexto']) ])
        story.append(KeepTogether(rosto_content)); story.append(PageBreak())

    # --- PROCESSAMENTO DO CORPO (Inalterado da v12) ---
    corpo_story = []; entradas_sumario = []; contadores_secao = {'h1': 0, 'h2': 0, 'h3': 0}
    linhas_texto = re.split(r'\n\s*\n+', dados_texto.strip())
    # ... (Loop de processamento do texto inalterado) ...
    for linha in linhas_texto:
        linha = linha.strip(); paragrafo_obj = None; titulo_formatado = ""
        if not linha: continue
        if linha.startswith('### '): contadores_secao['h3'] += 1; texto_limpo = linha.replace('###', '').strip().capitalize(); titulo_formatado = f"{contadores_secao['h1']}.{contadores_secao['h2']}.{contadores_secao['h3']} {texto_limpo}"; paragrafo_obj = Paragraph(titulo_formatado, styles['Titulo3'])
        elif linha.startswith('## '): contadores_secao['h2'] += 1; contadores_secao['h3'] = 0; texto_limpo = linha.replace('##', '').strip().capitalize(); titulo_formatado = f"{contadores_secao['h1']}.{contadores_secao['h2']} {texto_limpo}"; paragrafo_obj = Paragraph(f"<b>{titulo_formatado}</b>", styles['Titulo2'])
        elif linha.startswith('# '): contadores_secao['h1'] += 1; contadores_secao['h2'] = 0; contadores_secao['h3'] = 0; texto_limpo = linha.replace('#', '').strip().upper(); titulo_formatado = f"{contadores_secao['h1']} {texto_limpo}"; paragrafo_obj = Paragraph(f"<b>{titulo_formatado}</b>", styles['Titulo1'])
        elif linha.startswith('[clonga]'):
            match_clonga = re.match(r'\[clonga\](.*?)\[fimclonga\]\s*\((.*?)\)', linha, flags=re.DOTALL | re.IGNORECASE)
            if match_clonga:
                texto_citacao = match_clonga.group(1).strip(); autor_ano_pagina = match_clonga.group(2).strip()
                autor_match = re.match(r'([^,]+),\s*(\d{4}),\s*p\.\s*(\d+)', autor_ano_pagina, re.IGNORECASE)
                autor_formatado = f"({autor_match.group(1).strip().capitalize()}, {autor_match.group(2)}, p. {autor_match.group(3)})" if autor_match else f"({autor_ano_pagina.upper()})"
                corpo_story.append(Paragraph(texto_citacao, styles['CitacaoLonga'])); corpo_story.append(Paragraph(autor_formatado, styles['CitacaoLonga']))
            else: linha = re.sub(r'\[c:\s*([^,]+),\s*(\d{4}),\s*p\.\s*(\d+)\s*\]', lambda m: f" ({m.group(1).strip().capitalize()}, {m.group(2)}, p. {m.group(3)})", linha, flags=re.IGNORECASE); paragrafo_obj = Paragraph(linha, styles['CorpoABNT'])
        else: linha = re.sub(r'\[c:\s*([^,]+),\s*(\d{4}),\s*p\.\s*(\d+)\s*\]', lambda m: f" ({m.group(1).strip().capitalize()}, {m.group(2)}, p. {m.group(3)})", linha, flags=re.IGNORECASE); paragrafo_obj = Paragraph(linha, styles['CorpoABNT'])
        if paragrafo_obj: corpo_story.append(paragrafo_obj)
        if titulo_formatado: entradas_sumario.append(titulo_formatado)

    # --- SUMÁRIO (Página 3) ---
    if entradas_sumario:
        story.append(Paragraph("<b>SUMÁRIO</b>", styles['CapaTitulo']))
        story.append(Spacer(1, 1*cm))
        
        # *** REVERTIDO: Voltar a usar Parágrafos simples ***
        for entrada_texto in entradas_sumario:
            story.append(Paragraph(entrada_texto, styles['SumarioItem'])) # Usa o estilo base
        # *** FIM DA REVERSÃO ***

        # Define template da próxima página e quebra (ordem correta da v12)
        story.append(NextPageTemplate('textual'))
        story.append(PageBreak())

    # --- CORPO (A partir da Página 4 - Inalterado) ---
    story.extend(corpo_story)

    # --- REFERÊNCIAS (Inalterado) ---
    if dados_referencias:
        story.append(PageBreak()); story.append(Paragraph("<b>REFERÊNCIAS</b>", styles['Titulo1'])); story.append(Spacer(1, 0.5*cm))
        for ref in dados_referencias:
            texto_ref = ""; tipo = ref.get('tipo'); autor = ref.get('autor', ''); titulo = ref.get('titulo', ''); ano = ref.get('ano', '')
            if tipo == 'livro': cidade = ref.get('cidade', ''); editora = ref.get('editora', ''); texto_ref = f"{autor}. <b>{titulo}</b>. {cidade}: {editora}, {ano}."
            elif tipo == 'site': nome_site = ref.get('nome_site', ''); url = ref.get('url', ''); data_acesso = ref.get('data_acesso', ''); texto_ref = f"{autor}. {titulo}. {nome_site}, {ano}. Disponível em: &lt;{url}&gt;. Acesso em: {data_acesso}."
            elif tipo == 'artigo': revista = ref.get('nome_revista', ''); volume = ref.get('volume', ''); numero = ref.get('numero', ''); paginas = ref.get('paginas', ''); texto_ref = f"{autor}. {titulo}. <b>{revista}</b>, v. {volume}, n. {numero}, {paginas}, {ano}."
            story.append(Paragraph(texto_ref, styles['Referencia']))

    # Constrói o PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- BLOCO DE TESTE (igual v12, nome do arquivo v14) ---
if __name__ == "__main__":
    print("--- Iniciando teste do motor.py (v14 - Revertendo Sumário) ---")
    info_trabalho_teste = { 'autor': 'Junio da Silva', 'titulo': 'Desenvolvimento de um Formatador ABNT Automatizado', 'subtitulo': 'Um Estudo de Caso com Python e ReportLab', 'instituicao': 'Universidade Federal da Inovação', 'curso': 'Ciência da Computação', 'cidade': 'São Paulo', 'ano': '2025', 'orientador': 'Prof. Dr. Alan Turing' }
    dados_texto_teste = """# INTRODUÇÃO\n\nA automação de tarefas repetitivas representa um avanço significativo na otimização de processos.\n\nA formatação de documentos acadêmicos é uma atividade que consome tempo e exige atenção a detalhes. Como aponta a teoria, "a automação libera o potencial humano para tarefas mais criativas" [c: SANTOS, 2024, p. 15].\n\n## OBJETIVOS\n\n[clonga]O objetivo principal deste trabalho é desenvolver uma ferramenta robusta e de fácil utilização que possa ser amplamente adotada pela comunidade acadêmica, reduzindo significativamente o tempo gasto com formatação manual e aumentando a conformidade dos trabalhos com as normas técnicas vigentes.[fimclonga] (PEREIRA, 2023, p. 78)\n\nIsso é alcançado através de um desenvolvimento incremental.\n\n# METODOLOGIA\n\nA metodologia adotada foi o desenvolvimento ágil, focando em entregas contínuas de valor.\n"""
    dados_referencias_teste = [ { "tipo": "livro", "autor": "ASSIS, Machado de", "titulo": "Dom Casmurro", "cidade": "Rio de Janeiro", "editora": "Editora Clássicos", "ano": "1899" }, { "tipo": "artigo", "autor": "TURING, Alan", "titulo": "Computing Machinery and Intelligence", "nome_revista": "Mind", "volume": "LIX", "numero": "236", "paginas": "p. 433-460", "ano": "1950" } ]
    print("Gerando documento...")
    pdf_em_memoria = gerar_documento(info_trabalho_teste, dados_texto_teste, dados_referencias_teste)
    with open("TESTE_SAIDA_v14.pdf", "wb") as f: f.write(pdf_em_memoria.getbuffer())
    print("\n--- Teste Concluído! ---")
    print("Arquivo 'TESTE_SAIDA_v14.pdf' foi gerado.")