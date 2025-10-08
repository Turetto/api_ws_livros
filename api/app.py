from typing import List
from flask import Flask, jsonify, g, abort
from .database import SessionLocal
from .modelo import Livro
from .schemas import SchemaLivro

# Criar a instância principal
app = Flask(__name__)

# Gerenciamento das sessões do banco de dados
def get_db():
    """
    Cria e retorna uma nova sessão com o banco de dados para cada requisição.
    """
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db
    
@app.teardown_appcontext
def close_db(exception=None):
    """
    Fecha a sessão do banco de dados ao final de cada requisição.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Rota de verificação da conexão
@app.route("/api/v1/health", methods=['GET'])
def health_check():
    """
    Endpoint para verificar conexão da API.
    Retorna um status 'ok' se a API estiver rodando.
    """
    return jsonify({"Status": "OK", "message": "API está ativa."})

# Rota para listar livros no banco de dados livraria
@app.route("/api/v1/books", methods=['GET'])
def get_livros():
    """
    Endpoint para acessar lista de livros no banco de dados.
    """
    
    db = get_db()
    todos_livros = db.query(Livro).all()

    livros_serializado = [SchemaLivro.model_validate(livro) for livro in todos_livros]
    resultado = [livro.model_dump() for livro in livros_serializado]

    return jsonify(resultado)

# Rota para buscar um livro por ID
@app.route("/api/v1/books/<int:livro_id>", methods=['GET'])
def get_livro_id(livro_id):
    """
    Endpoint para buscar um livro específico pelo seu ID.
    """

    db = get_db()
    livro = db.query(Livro).get(livro_id)

    if not livro:
        abort(404, description=f"Livro com id {livro_id} não encontrado.")

    livro_serializado = SchemaLivro.model_validate(livro)
    resultado = livro_serializado.model_dump()

    return jsonify(resultado)

# Rota para listar as categorias de livro
@app.route("/api/v1/categories", methods=['GET'])
def get_categorias():
    """
    Endpoint para listar categorias de livros disponíveis no banco de dados.
    """

    db = get_db()

    categorias = db.query(Livro.categoria).distinct().all()
    categorias = [categoria[0] for categoria in categorias]

    return jsonify(categorias)


if __name__ == '__main__':
    app.run(debug=True, port=1312)