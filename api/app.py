import os
import sys
import subprocess
import joblib
import numpy as np
from typing import List
from flask import Flask, jsonify, g, abort, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func
from .database import SessionLocal
from .modelo import Livro, Usuario
from .schemas import SchemaLivro, ModeloInput

# Criar a instância principal
app = Flask(__name__)

# Configurações do JWT
app.config["JWT_SECRET_KEY"] = "fiap_mle"
jwt = JWTManager(app)

# Carregando o modelo de classificação e o scaler

try:
    model_path = os.path.join('models', 'kmeans_model.joblib')
    scaler_path = os.path.join('models', 'scaler.joblib')
    kmeans_model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("Modelos de ML carregados com sucesso.")

except FileNotFoundError:
    kmeans_model = None
    scaler = None
    print("AVISO: Arquivos de modelo não encontrados. O endpoint de predição não funcionará.")

# Mapeamento dos nomes dos clusters
cluster_names = {
    0: "Econômico",
    1: "Custo-Benefício",
    2: "Premium",
    3: "Colecionador"
}

# Mapeamento para feature engineering
rating_map = {"One": 1, 
              "Two": 2, 
              "Three": 3, 
              "Four": 4, 
              "Five": 5}

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


# Rotas para modelagem
# Rota para acessar dados de treinamento
@app.route("/api/v1/ml/training-data", methods=['GET'])
@jwt_required()
def training_data():
    """Endpoint para servir o dataset completo para treinamento."""

    db = get_db()

    todos_livros = db.query(Livro).all()
    livros_schema = [SchemaLivro.model_validate(livro) for livro in todos_livros]
    resultado_json = [livro.model_dump() for livro in livros_schema]
    return jsonify(resultado_json)

# Rotas para acessar features do modelo
@app.route("/api/v1/ml/features", methods=['GET'])
def get_features():
    """Endpoint que retorna as features do modelo."""
    
    db = get_db()

    todos_livros = db.query(Livro).all()

    lista_features = []
    for livro in todos_livros:
        avaliacao_numerica = rating_map.get(livro.avaliacao, 0)
        features = {
            "livro_id": livro.id,
            "preco": livro.preco,
            "avaliacao_numerica": avaliacao_numerica
        }
        lista_features.append(features)


    return jsonify(lista_features)

# Rotas para acessar features do modelo de um id
@app.route("/api/v1/ml/features/<int:livro_id>", methods=['GET'])
def get_book_features(livro_id):
    """Endpoint que retorna os dados de um livro formatados como features."""
    db = get_db()
    livro_orm = db.query(Livro).get(livro_id)
    if not livro_orm:
        abort(404, description=f"Livro com id {livro_id} não encontrado.")
    
    avaliacao_numerica = rating_map.get(livro_orm.avaliacao, 0)
    features = {
        "livro_id": livro_orm.id,
        "preco": livro_orm.preco,
        "avaliacao_numerica": avaliacao_numerica
    }
    return jsonify(features)

# Rota para projeção com kmeans
@app.route("/api/v1/ml/predictions", methods=['POST'])
def predict_cluster():
    """Endpoint para prever o cluster de um livro com base no preço e avaliação."""
    if not kmeans_model or not scaler:
        abort(503, description="Modelos de ML não estão disponíveis ou carregados.")

    input_data = ModeloInput.model_validate(request.get_json())
    avaliacao_numerica = rating_map.get(input_data.avaliacao, 0)
    features = np.array([[input_data.preco, avaliacao_numerica]])
    features_scaled = scaler.transform(features)
    proj_cluster = kmeans_model.predict(features_scaled)[0]
    cluster_name = cluster_names.get(int(proj_cluster), "Desconhecido")

    return jsonify({
        "input_data": input_data.model_dump(),
        "predicted_cluster_index": int(proj_cluster),
        "predicted_cluster_name": cluster_name
    })
   



if __name__ == '__main__':
    app.run(debug=True, port=1312)