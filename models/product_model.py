from pydantic import BaseModel


class Product(BaseModel):
    title: str
    image_url: str
    price: str
    negative_reviews: int
    positive_reviews: int
    neutral_reviews: int
    average_score: float
