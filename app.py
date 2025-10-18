# app.py

# A importação do render_template é a novidade aqui
from flask import Flask, request, send_file, render_template 
from motor import gerar_documento

app = Flask(__name__)

# [MUDANÇA] Agora, a rota principal vai renderizar nosso arquivo HTML
@app.route('/')
def index():
    return render_template('index.html') # Procura por index.html na pasta 'templates'

# A rota de formatação continua a mesma
@app.route('/formatar', methods=['POST'])
def formatar():
    dados_json = request.get_json()
    texto_trabalho = dados_json.get('texto', '') # Adicionado valor padrão
    lista_referencias = dados_json.get('referencias', []) # Adicionado valor padrão

    documento_em_memoria = gerar_documento(texto_trabalho, lista_referencias)
    
    return send_file(
        documento_em_memoria,
        as_attachment=True,
        download_name='trabalho_formatado.docx',
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

if __name__ == '__main__':
    app.run(debug=True)