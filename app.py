# app.py - Versão Final com Correção de CORS

from flask import Flask, request, send_file
from flask_cors import CORS # Importa a ferramenta CORS
from motor import gerar_documento

app = Flask(__name__)

# --- INÍCIO DA CORREÇÃO DE CORS ---
#
# Configuração de CORS mais específica e segura.
# Isso cria uma "lista VIP" e diz ao nosso servidor no Render:
# "Permita que SOMENTE o site 'https://formatador-abnt-gamma.vercel.app' 
# faça requisições para a rota '/formatar'."
#
# É a solução definitiva para o erro.
#
CORS(app, resources={
    r"/formatar": {
        "origins": "https://formatador-abnt-gamma.vercel.app"
    }
})
# --- FIM DA CORREÇÃO DE CORS ---


# Rota principal da API (para testar se está no ar)
@app.route('/')
def index():
    return "<h1>API do Formatador ABNT está no ar e com a correção de CORS!</h1>"


# Rota que recebe os dados, gera o documento e o envia para download
@app.route('/formatar', methods=['POST'])
def formatar():
    dados_json = request.get_json()
    
    # Adicionamos valores padrão ('') para evitar erros se o campo vier vazio
    texto_trabalho = dados_json.get('texto', '') 
    lista_referencias = dados_json.get('referencias', [])

    # Chama o motor que faz todo o trabalho pesado
    documento_em_memoria = gerar_documento(texto_trabalho, lista_referencias)
    
    # Envia o arquivo .docx gerado de volta para o navegador do usuário
    return send_file(
        documento_em_memoria,
        as_attachment=True,
        download_name='trabalho_formatado.docx',
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

# Linha necessária para o Render.com usar o Gunicorn (não precisa mexer)
if __name__ == '__main__':
    app.run(debug=True)