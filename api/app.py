import subprocess
import sys
from typing import List
from flask import Flask, jsonify, g, abort, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func
from .database import SessionLocal
from .modelo import Livro, Usuario
from .schemas import SchemaLivro

# Criar a instância principal
app = Flask(__name__)

# Configurações do JWT
app.config["JWT_SECRET_KEY"] = "fiap_mle"
jwt = JWTManager(app)

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

# Rota para fazer busca por filtros
@app.route("/api/v1/books/search", methods=['GET'])
def get_search():
    """
    Endpoint para buscar livros por título e/ou categoria.
    """
    
    db = get_db()

    titulo_filtro = request.args.get('titulo')
    categoria_filtro = request.args.get('categoria')

    query = db.query(Livro)

    if titulo_filtro:
        query = query.filter(Livro.titulo.ilike(f'%{titulo_filtro}%'))

    if categoria_filtro:
        query = query.filter(Livro.categoria.ilike(categoria_filtro))
    
    livros_filtro = query.all()

    livros_serializado = [SchemaLivro.model_validate(livro) for livro in livros_filtro]
    resultado = [livro.model_dump() for livro in livros_serializado]

    return jsonify(resultado)

# Rota para estatisticas gerais da coleção
@app.route("/api/v1/stats/overview", methods=["GET"])
def get_stats_overview():
    """
    Endpoint para obter estatísticas gerais da coleção de livros.
    """
    db = get_db()

    total_livros = db.query(Livro).count()
    preco_medio = round(db.query(func.avg(Livro.preco)).scalar(), 2)
    distribuicao_aval = db.query(Livro.avaliacao, func.count(Livro.id)).group_by(Livro.avaliacao).all()
    contagem_aval = {avaliacao: contagem for avaliacao, contagem in distribuicao_aval}

    overview = {
        "total_livros": total_livros,
        "preco_medio": preco_medio,
        "distribuicao_avaliacoes": contagem_aval
    }
    
    return jsonify(overview)

# Rota para estatísticas gerais por categoria de livro
@app.route("/api/v1/stats/categories", methods=['GET'])
def get_stats_categories():
    """
    Endpoint para obter estatísticas detalhadas por categoria.
    """

    db = get_db()

    stats_query = db.query(
        Livro.categoria,
        func.count(Livro.id).label("total_livros"),
        func.avg(Livro.preco).label("preco_medio")
    ).group_by(Livro.categoria).order_by(Livro.categoria).all()

    resultado_formatado = []
    for categoria, total_livros, preco_medio in stats_query:
        resultado_formatado.append({
            "categoria": categoria,
            "total_livros": total_livros,
            "preco_medio": round(preco_medio, 2)
        })
        
    return jsonify(resultado_formatado)

# Rota para listar top rank dos livros
@app.route("/api/v1/books/top-rated", methods=['GET'])
def get_top_rated():
    """
    Endpoint para listar os livros com a melhor avaliação.
    """
    db = get_db()
        
    top_rated = db.query(Livro).filter(
        Livro.avaliacao == "Five"
    ).order_by(Livro.titulo).all()

    livros_serializado = [SchemaLivro.model_validate(livro) for livro in top_rated]
    resultado = [livro.model_dump() for livro in livros_serializado]
        
    return jsonify(resultado)

# Rota para filtrar por faixa de preco
@app.route("/api/v1/books/price-range", methods=['GET'])
def get_price_range():
    """
    Endpoint para listar livros dentro de uma faixa de preço.
    """
    db = get_db()
       
    min = request.args.get('min')
    max = request.args.get('max')
        
    if not min or not max:
        abort(400, description="Parâmetros 'min' e 'max' são obrigatórios.")
        
    try:
        min_preco = float(min)
        max_preco = float(max)
    except ValueError:
        abort(400, description="Parâmetros 'min' e 'max' devem ser números válidos.")
        
    livros_na_faixa = db.query(Livro).filter(
        Livro.preco.between(min_preco, max_preco)
    ).order_by(Livro.preco).all()
    
    livros_serializado = [SchemaLivro.model_validate(livro) for livro in livros_na_faixa]
    resultado = [livro.model_dump() for livro in livros_serializado]
        
    return jsonify(resultado)

# Rota para autenticar login
@app.route("/api/v1/auth/login", methods=['POST'])
def login():
    """
    Endpoint para autenticar um usuário e retornar um token de acesso.
    """

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"msg": "Nome de usuário e senha são obrigatórios"}), 400
    
    db = get_db()

    user = db.query(Usuario).filter_by(username=username).first()

    # criação do token JWT
    if user and user.password == password:
        access_token = create_access_token(identity=str(user.username))
        return jsonify(access_token=access_token)
    
# Teste do login
@app.route("/api/v1/admin/test", methods=['GET'])
@jwt_required()
def admin_test():
    """
    rota de teste para usuário.    
    """

    user_id = get_jwt_identity()
    return jsonify(logged_in_as=user_id), 200

# Endpoint para inicializar o web scraping
@app.route("/api/v1/admin/scraping/trigger", methods=['POST'])
@jwt_required()
def scraping_trigger():
    current_user_id = get_jwt_identity()

    if current_user_id != 'bruno':
        return jsonify({"msg": "Acesso negado. Apenas administradores."}), 403
    
    try:
        print("Iniciando o processo de scraping em segundo plano...")
        python_executable = sys.executable
        script_path = "scripts/update_pipe.py"

        # Iniciar o processo sem bloquear a API
        subprocess.Popen([python_executable, "-m", "scripts.update_pipe"])

        return jsonify({"msg": "Pipeline ativado com sucesso."}), 202
        
    except Exception as e:
        print(f"Erro ao disparar o scraping: {e}")
        return jsonify({"msg": "Erro interno ao tentar iniciar o scraping."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=1312)