from pydantic import BaseModel


class Recipes(BaseModel):
    title: str
    description: str
    ingredients: list[str, int, float]
