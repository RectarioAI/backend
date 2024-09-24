from fastapi import APIRouter
import re
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import random

from helpers.get_product_data import get_product_data
from helpers.get_all_reviews import reviews_scrapping
from helpers.get_urls_products import get_url_products

views = APIRouter()

# Descargar recursos de NLTK necesarios
nltk.download('punkt')
nltk.download('stopwords')

# Inicialización de analyzer y stopwords en español
analyzer = SentimentIntensityAnalyzer()
stopwords_es = set(nltk.corpus.stopwords.words('spanish'))

def clean_text(text):
    text = re.sub(r'\d+', '', text)  # Eliminar números
    text = re.sub(r'\s+', ' ', text)  # Reemplazar múltiples espacios por uno solo
    text = re.sub(r'[^\w\s]', '', text)  # Eliminar símbolos y puntuación
    return text.strip()

def remove_stopwords(text):
    words = nltk.word_tokenize(text, language='spanish')
    filtered_words = [word for word in words if word.lower() not in stopwords_es]
    return ' '.join(filtered_words)

def analyze_sentiments(opinions):
    sentiments = []
    for opinion in opinions:
        cleaned_opinion = clean_text(opinion)
        sentiment = analyzer.polarity_scores(cleaned_opinion)
        sentiment_score = sentiment['compound']
        if sentiment_score > 0.1:
            sentiment_label = 'Positivo'
        elif sentiment_score < -0.1:
            sentiment_label = 'Negativo'
        else:
            sentiment_label = 'Neutral'
        sentiments.append((opinion, sentiment_label, sentiment_score))
    return sentiments

def rank_products_by_individual(sentiments, products):
    product_rankings = []

    # Iterar sobre cada conjunto de opiniones por producto
    for i, product_reviews in enumerate(sentiments):
        total_score = 0
        total_reviews = len(product_reviews)
        positive_reviews = sum(1 for review in product_reviews if review[2] > 0)
        negative_reviews = sum(1 for review in product_reviews if review[2] < 0)
        neutral_reviews = total_reviews - positive_reviews - negative_reviews
        
        # Calcular el promedio de sentimiento
        for review in product_reviews:
            total_score += review[2]
        average_score = total_score / total_reviews if total_reviews > 0 else 0

        # Actualizar el producto con los nuevos datos
        product = products[i]
        product.positive_reviews = positive_reviews
        product.negative_reviews = negative_reviews
        product.neutral_reviews = neutral_reviews
        product.average_score = round(average_score, 2)

        # Añadir el producto actualizado a la lista de rankings
        product_rankings.append(product)

    # Ordenar productos por el puntaje promedio
    product_rankings.sort(key=lambda x: x.average_score, reverse=True)
    
    return product_rankings


@views.get("/api/opinions/{busqueda}")
async def get_car_opinions(busqueda: str):
    urls: list[str] = get_url_products(busqueda)

    total_sentiments = []
    products = []  # Almacenaremos productos aquí para completar los datos después

    for url in urls:
        chrome_options = Options()

        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Crear driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Abrir la página del producto
        driver.get(url)
        
        # Esperar a que la página cargue completamente
        time.sleep(random.randint(3,5))

        # Borrar cookies del navegador para evitar ban
        driver.delete_all_cookies()

        # Obtener los datos básicos del producto
        product = get_product_data(url)
        products.append(product)  # Almacenar el producto con los datos iniciales

        # Obtener las reseñas
        reviews = reviews_scrapping(driver)

        # Analizar los sentimientos de las reseñas
        sentiments = analyze_sentiments(reviews)
        total_sentiments.append(sentiments)
        
        driver.quit()

    # Llamar al nuevo método para crear el ranking por producto y completar los datos
    rankings = rank_products_by_individual(total_sentiments, products)

    return JSONResponse({
        'rankings': [product.dict() for product in rankings],  # Convertir cada producto a un diccionario para JSON
    })
