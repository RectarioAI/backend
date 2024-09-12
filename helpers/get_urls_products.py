import requests
from bs4 import BeautifulSoup

def get_url_products(busqueda: str):
    urlBase = "https://listado.mercadolibre.com.co/"
    busqueda = busqueda.replace(" ", "-")
    urlFull = f"{urlBase}{busqueda}"
    response = requests.get(urlFull)

    soup = BeautifulSoup(response.text, 'html.parser')
    resultados = soup.find_all('h2', 'poly-box poly-component__title')

    hrefs = []
    
    for resultado in resultados:
        enlace = resultado.find('a')
        if enlace and enlace.get('href'):
            hrefs.append(enlace['href'])

    hrefs = hrefs[:1]

    return hrefs