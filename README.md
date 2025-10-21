# API Pública para Consulta de Livros (Projeto Tech Challenge)

Este repositório contém o código-fonte de uma API RESTful para consulta de informações sobre livros, extraídas do site "Books to Scrape". O projeto inclui um pipeline de dados completo (web scraping, armazenamento em banco de dados) e uma API com funcionalidades de consulta, estatísticas e integração com um modelo de Machine Learning (clusterização).

**Deploy da API:** A API está disponível publicamente em: `https://turetto-api-livros-3a30130b990d.herokuapp.com/` 

**Documentação Interativa (Swagger):** `https://turetto-api-livros-3a30130b990d.herokuapp.com/apidocs/` 

## Arquitetura do Projeto

![Diagrama da Arquitetura](images/arquitetura.png)



* **Fonte de Dados:** Books to Scrape (https://books.toscrape.com/)
* **Web Scraping:** Script Python (`scripts/scraper.py`) usando `requests` e `BeautifulSoup` para extrair dados de todos os livros e categorias.
* **Armazenamento Temporário:** Arquivo `data/livros.csv` gerado pelo scraper (ignorado pelo Git).
* **Banco de Dados:** PostgreSQL (no Heroku, `heroku-postgresql:essential-0`) acessado via SQLAlchemy. Modelos definidos em `api/modelo.py`.
* **API:** Aplicação Flask (`api/app.py`) servida com Gunicorn.
* **Machine Learning:**
    * Treinamento (offline): Script `scripts/train_model.py` usa `pandas` e `scikit-learn` para treinar um modelo K-Means com base em preço e avaliação.
    * Artefatos: O modelo treinado (`kmeans_model.joblib`) e o scaler (`scaler.joblib`) são salvos na pasta `models/`.
    * Inferência (online): A API carrega os artefatos e usa o endpoint `POST /api/v1/ml/predictions` para prever o cluster de novos livros.
* **Documentação:** Gerada automaticamente com `Flasgger` (Swagger UI).
* **Deploy:** Hospedado na plataforma Heroku.

## Funcionalidades da API

A API oferece os seguintes endpoints principais (prefixo `/api/v1`):

* **Livros:**
    * `GET /books`: Lista todos os livros.
    * `GET /books/{id}`: Detalhes de um livro específico.
    * `GET /books/search`: Busca livros por título e/ou categoria.
    * `GET /books/top-rated`: Lista os livros com avaliação 5 estrelas.
    * `GET /books/price-range`: Filtra livros por faixa de preço.
* **Categorias:**
    * `GET /categories`: Lista todas as categorias únicas.
* **Insights:**
    * `GET /stats/overview`: Estatísticas gerais da coleção.
    * `GET /stats/categories`: Estatísticas detalhadas por categoria.
* **Autenticação:**
    * `POST /auth/login`: Autentica um usuário e retorna um token JWT.
* **Admin (Protegido):**
    * `POST /admin/scraping/trigger`: Dispara o pipeline de atualização de dados (requer token de admin).
* **Machine Learning:**
    * `GET /ml/training-data`: Retorna todos os dados brutos para treinamento.
    * `GET /ml/features`: Retorna features processadas para todos os livros.
    * `GET /ml/features/{id}`: Retorna features processadas para um livro específico.
    * `POST /ml/predictions`: Prevê o cluster de um livro (requer preço e avaliação).
* **Health Check:**
    * `GET /health`: Verifica se a API está operacional.

*Para detalhes completos sobre parâmetros e respostas, consulte a [Documentação Interativa (Swagger)](https://turetto-api-livros-3a30130b990d.herokuapp.com/apidocs/).*

## Como Executar o Projeto Localmente

**Pré-requisitos:**

* Python 3.10+ (ou a versão especificada em `runtime.txt`)
* Git
* `psql` (cliente de linha de comando do PostgreSQL, opcional para banco local SQLite)
* Um ambiente virtual (recomendado)

**Instalação:**

1.  Clone o repositório usando o comando `git clone` com a URL do seu repositório GitHub e navegue para a pasta do projeto.
2.  Crie um ambiente virtual com `python -m venv venv` e ative-o (usando `venv\Scripts\activate` no Windows ou `source venv/bin/activate` no macOS/Linux).
3.  Instale todas as dependências necessárias, incluindo as de treinamento, usando o comando `pip install -r requirements.txt`.
4.  Crie a pasta `data/` na raiz do projeto, caso ela ainda não exista.

**Configuração do Banco de Dados (Local - SQLite):**

O código usará um arquivo `data/books.db` automaticamente se a variável de ambiente `DATABASE_URL` não estiver definida.

**Execução do Pipeline de Dados (Local):**

1.  Execute o scraper para gerar o arquivo `livros.csv` usando o comando: `python -m scripts.scraper`.
2.  Crie as tabelas no banco de dados SQLite usando o comando: `python -m scripts.init_db`.
3.  Popule a tabela de livros com os dados do CSV usando o comando: `python -m scripts.populate_db`.
4.  Crie um usuário administrador. Execute o script `create_admin.py` diretamente (`python scripts/create_admin.py`) para que ele peça interativamente o nome de usuário e a senha.
5.  Treine o modelo de Machine Learning e salve os arquivos do modelo e do scaler usando o comando: `python -m scripts.train_model`.

**Iniciando a API (Local):**
```bash
flask --app api/app run --port 5000
```

Execute o comando `flask --app api/app run --port 5000` para iniciar o servidor de desenvolvimento do Flask. A API estará acessível em `http://127.0.0.1:5000` e a documentação em `http://127.0.0.1:5000/apidocs/`.

## Exemplos de Chamadas à API (Usando `curl`)
```bash
curl -X GET "https://<URL_projeto>/api/v1/books/"
```

**Exemplo: Listar todos os livros**
Use o curl com o método GET para a URL `https://<URL_projeto>/api/v1/books/`.

```bash
curl -X GET "https://<URL_projeto>/api/v1/books/"
```

**Exemplo: Fazer login (substitua com suas credenciais)**
Use o curl com o método POST para a URL `https://<URL_projeto>/api/v1/auth/login`, enviando um cabeçalho `Content-Type: application/json` e o corpo JSON com seu `username` e `password`.
```bash
curl -X POST "https://<URL_projeto>/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
           "username": "admin",
           "password": "sua_senha"
         }'
```

**Exemplo: Disparar o scraping (substitua <SEU_TOKEN>)**
Use o curl com o método POST para a URL `https://<URL_projeto>/api/v1/admin/scraping/trigger`, enviando o cabeçalho `Authorization: Bearer <SEU_TOKEN>`.

**Exemplo: Prever o cluster de um livro**
Use o curl com o método POST para a URL `https://<URL_projeto>/api/v1/ml/predictions`, enviando um cabeçalho `Content-Type: application/json` e o corpo JSON com `preco` e `avaliacao`.

```bash
curl -X POST "https://<URL_projeto>/api/v1/ml/predictions" \
     -H "Content-Type: application/json" \
     -d '{
           "preco": 35.50,
           "avaliacao": "Four"
         }'
```

## Dashboard Streamlit

O projeto inclui um dashboard simples para visualização dos dados da API.

**Como executar localmente:**
Execute o comando `streamlit run dashboard/app_dashboard.py` no terminal. O dashboard abrirá automaticamente no seu navegador. *(Certifique-se de que a `API_BASE_URL` no script do dashboard aponta para a sua API na Heroku).*

## Próximos Passos / Melhorias Futuras


