# app.py (com as alterações para PDF)

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
    return "<h1>API do Formatador ABNT (Versão PDF) está no ar!</h1>"

@app.route('/formatar', methods=['POST'])
def formatar():
    dados_json = request.get_json()
    
    info_trabalho = dados_json.get('info_trabalho', {})
    texto_trabalho = dados_json.get('texto', '') 
    lista_referencias = dados_json.get('referencias', [])

    documento_em_memoria = gerar_documento(info_trabalho, texto_trabalho, lista_referencias)
    
    return send_file(
        documento_em_memoria,
        as_attachment=True,
        # --- ALTERAÇÕES AQUI ---
        download_name='trabalho_formatado.pdf',
        mimetype='application/pdf'
        # --- FIM DAS ALTERAÇÕES ---
    )

if __name__ == '__main__':
    app.run(debug=True)