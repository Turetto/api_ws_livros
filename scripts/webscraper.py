import requests
import random
import time
from bs4 import BeautifulSoup 
from urllib.parse import urljoin

# Configurações do script
BASE_URL = "https://books.toscrape.com/"
# A URL inicial pode ser a página de catálogo
next_page_url = "catalogue/page-1.html"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0'
]

# Lista para armazenar os dados
dados_livros = []

# Web Scrapping
while next_page_url:

    # Constrói a URL completa
    url_completa = urljoin(BASE_URL, next_page_url)
    print(f"Extração em: {url_completa}")

    random_user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': random_user_agent}
    
    try:
        response = requests.get(url_completa, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
        time.sleep(1)

        soup = BeautifulSoup(response.text, 'html.parser')
        livros = soup.find_all('article', class_='product_pod')

        if not livros:
            print("Nenhum livro encontrado nesta página.")
            break

        for livro in livros:
            titulo = livro.h3.a['title']
            preco = livro.find('p', class_='price_color').text
            preco = float(preco.replace('£', ''))
            avaliacao = livro.find('p', class_='star-rating')['class'][1]
            disponibilidade = livro.find('p', class_='instock availability').text.strip()                        
            url_imagem = urljoin(BASE_URL, livro.find('img')['src']) # juntando com a URL base

            # Adiciona os dados a lista
            dados_livros.append({
                'titulo': titulo,
                'preco': preco,
                'avaliacao': avaliacao,
                'disponibilidade': disponibilidade,
                'url_imagem': url_imagem
            })

        # procura pelo link da próxima página
        next_li = soup.find('li', class_='next')
        if next_li and next_li.a and next_li.a['href']:
            next_page_url = urljoin(url_completa, next_li.a['href'])
        else:
            print("Fim da paginação.")
            next_page_url = None

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página {url_completa}: {e}")
        break

# Encerrar script
print("-" * 30)
print(f"Web Scraping finalizado!")
print(f"Total de livros extraídos: {len(dados_livros)}")
