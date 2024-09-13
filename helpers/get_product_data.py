import requests
from bs4 import BeautifulSoup
from models.product_model import Product


def get_product_data(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.find('h1', class_='ui-pdp-title').text.strip()
    image_url = soup.find('figure', class_='ui-pdp-gallery__figure').find('img')['src']
    price = soup.find_all('span', class_='andes-money-amount__fraction')
    
    if len(price) > 1:
        price = price[1].text.strip()
    else:
        price = price[0].text.strip()

    # Crear el objeto Product con los datos básicos
    new_product = Product(title=title, image_url=image_url, price=price)

    return new_product
