from models.product_model import Product


def fromModelToDict(recipe: Product):
    return {
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
    }


def fromDictToModel(data: dict):
    return Product(
        title=data["title"],
        description=data["description"],
        ingredients=data["ingredients"],
    )

