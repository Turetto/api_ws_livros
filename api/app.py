from flask import Flask, jsonify

# Criar a instância principal
app = Flask(__name__)

@app.route("/api/v1/health", methods=['GET'])
def health_check():
    """
    Endpoint para verificar conexão da API.
    Retorna um status 'ok' se a API estiver rodando.
    """
    return jsonify({"Status": "OK", "message": "API está ativa."})

if __name__ == '__main__':
    app.run(debug=True, port=1312)
