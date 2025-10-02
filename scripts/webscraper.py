import requests
import random
import time
from bs4 import BeautifulSoup 

# Configurações do script
URL = "https://books.toscrape.com/"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0'
]

# Requisição da página html
random_user_agent = random.choice(USER_AGENTS)
headers = {'User-Agent': random_user_agent}
response = requests.get(URL, headers=headers)
response.encoding = 'utf-8'
time.sleep(1) 

# Web Scrapping
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # product_pod é o container de cada livro
    livros = soup.find_all('article', class_='product_pod')
    
    print(f"{len(livros)} livros encontrados na página.")
    print("-" * 10)

    # Loop para extrair dados de cada livro
    for livro in livros:
        
        titulo = livro.h3.a['title']                
        preco = livro.find('p', class_='price_color').text
        preco = float(preco.replace('£', ''))
        avaliacao = livro.find('p', class_='star-rating')['class'][0]
        disponibilidade = livro.find('p', class_='instock availability').text.strip()
        url_imagem = livro.find('img')['src']
        
        print(f"Título: {titulo}")
        print(f"Preço: {preco}")
        print(f"Avaliação: {avaliacao}")
        print(f"Disponibilidade: {disponibilidade}")
        print(f"URL da Imagem: {url_imagem}")
        print("-" * 20)

else:
    print(f"Falha na conexão. Código de status: {response.status_code}")