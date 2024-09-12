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

def get_opinions_and_ratings(model, max_opinions=10):
    url = f'https://www.opinautos.com/co/{model}/opiniones'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    opinions = []
    ratings = []
    exclude_phrases = ['Lo mejor', 'Lo peor', 'Busca tu problema', 'Deja tu opinión', 'ModelXXXX', 'xxx']

    for opinion_span in soup.find_all('span', class_='align-middle'):
        cleaned_text = clean_text(opinion_span.get_text(strip=True))
        if cleaned_text and len(opinions) < max_opinions and not any(phrase in cleaned_text for phrase in exclude_phrases):
            opinions.append(cleaned_text)

    for rating_box in soup.find_all('div', class_='LeftRightBox__left LeftRightBox__left--noshrink'):
        stars = 0
        for star_index in range(1, 6):
            star_span = rating_box.find('span', {'data-starindex': str(star_index)})
            if star_span and star_span.find('img', {'src': 'https://static.opinautos.com/images/design2/icons/icon_star--gold.svg?v=5eb58b'}):
                stars += 1
        ratings.append(stars)

    if len(opinions) < max_opinions:
        print(f'No se encontraron suficientes opiniones para {model}. Solo se encontraron {len(opinions)} opiniones.')

    return opinions, ratings

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

def summarize_with_textrank(opinions):
    text = "\n".join(opinions)
    parser = PlaintextParser.from_string(text, Tokenizer("spanish"))
    summarizer = TextRankSummarizer()
    summary_sentences = summarizer(parser.document, 5)

    summary = " ".join([str(sentence) for sentence in summary_sentences])
    summary = re.sub(r'\s+', ' ', summary).strip()

    if len(summary) > 200:
        last_space = summary[:150].rfind(' ')
        summary = summary[:last_space] + '.'

    return summary

def calculate_rating_change(ratings):
    if len(ratings) < 2:
        return 0  
    current_avg = sum(ratings[-5:]) / len(ratings[-5:])
    previous_avg = sum(ratings[:-5]) / len(ratings[:-5]) if len(ratings) > 5 else sum(ratings) / len(ratings)
    change = current_avg - previous_avg
    return round(change, 1)


def rank_products_by_individual(sentiments, urls):
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
        
        # Incluir el URL o identificador del producto para diferenciar
        product_rankings.append({
            'product_url': urls[i],  # Vincular con la URL del producto
            'average_score': average_score,
            'positive_reviews': positive_reviews,
            'negative_reviews': negative_reviews,
            'neutral_reviews': neutral_reviews,
        })

    # Ordenar productos por el puntaje promedio (o cualquier criterio que prefieras)
    product_rankings.sort(key=lambda x: x['average_score'], reverse=True)
    
    return product_rankings



@views.get("/api/opinions")
async def get_car_opinions(busqueda: str):
    urls: list[str] = get_url_products(busqueda)

    total_sentiments = []

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

        reviews = reviews_scrapping(driver)
        # print(reviews)

        sentiments = analyze_sentiments(reviews)
        total_sentiments.append(sentiments)
        
        driver.quit()

    # Llamar al nuevo método para crear el ranking por producto
    rankings = rank_products_by_individual(total_sentiments, urls)

    return JSONResponse({
        'rankings': rankings,
    })
