# app.py

from flask import Flask, request, send_file, render_template
from flask_cors import CORS # [NOVO] Importa a ferramenta CORS
from motor import gerar_documento

app = Flask(__name__)
CORS(app) # [NOVO] Ativa o CORS para toda a aplicação, liberando o acesso

# A partir daqui, o resto do seu código continua exatamente igual...
@app.route('/')
def index():
    # Esta rota não é mais usada pela Vercel, mas podemos manter para teste
    return "<h1>API do Formatador ABNT está no ar!</h1>"

@app.route('/formatar', methods=['POST'])
def formatar():
    dados_json = request.get_json()
    texto_trabalho = dados_json.get('texto', '')
    lista_referencias = dados_json.get('referencias', [])

    documento_em_memoria = gerar_documento(texto_trabalho, lista_referencias)

    return send_file(
        documento_em_memoria,
        as_attachment=True,
        download_name='trabalho_formatado.docx',
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

if __name__ == '__main__':
    app.run(debug=True)