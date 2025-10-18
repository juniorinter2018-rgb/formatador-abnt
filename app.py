# app.py

from flask import Flask, request, send_file
from flask_cors import CORS
from motor import gerar_documento

app = Flask(__name__)

# Configuração de CORS para permitir acesso apenas do seu site na Vercel
CORS(app, resources={
    r"/formatar": {
        "origins": "https://formatador-abnt-gamma.vercel.app"
    }
})

@app.route('/')
def index():
    return "<h1>API do Formatador ABNT está no ar!</h1>"

@app.route('/formatar', methods=['POST'])
def formatar():
    dados_json = request.get_json()
    
    # Pega os três blocos de dados do JSON enviado pelo frontend
    info_trabalho = dados_json.get('info_trabalho', {})
    texto_trabalho = dados_json.get('texto', '') 
    lista_referencias = dados_json.get('referencias', [])

    # Passa as informações do trabalho para o motor
    documento_em_memoria = gerar_documento(info_trabalho, texto_trabalho, lista_referencias)
    
    return send_file(
        documento_em_memoria,
        as_attachment=True,
        download_name='trabalho_formatado.docx',
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

if __name__ == '__main__':
    app.run(debug=True)