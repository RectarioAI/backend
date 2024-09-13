from pydantic import BaseModel


class Product(BaseModel):
    title: str
    image_url: str
    price: str
    negative_reviews: int = 0
    positive_reviews: int = 0
    neutral_reviews: int = 0
    average_score: float = 0.0

    