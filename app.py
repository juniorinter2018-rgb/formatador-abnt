# app.py (Final)

from flask import Flask, request, send_file
from flask_cors import CORS
from motor import gerar_documento
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "<h1>API do Formatador ABNT está no ar!</h1>"

@app.route('/formatar', methods=['POST'])
def formatar():
    try:
        dados_json = request.get_json()
        
        info_trabalho = dados_json.get('info_trabalho', {})
        texto_html = dados_json.get('texto_html', '') 
        lista_referencias = dados_json.get('referencias', [])

        documento_em_memoria = gerar_documento(info_trabalho, texto_html, lista_referencias)
        
        return send_file(
            documento_em_memoria,
            as_attachment=True,
            download_name='trabalho_formatado.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        print(f"Ocorreu um erro:\n{traceback.format_exc()}")
        return "Erro interno ao processar o documento", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)