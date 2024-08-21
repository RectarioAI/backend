from models.recipe_model import Recipes


def fromModelToDict(recipe: Recipes):
    return {
        "title": recipe.title,
        "description": recipe.description,
        "ingredients": recipe.ingredients,
    }


def fromDictToModel(data: dict):
    return Recipes(
        title=data["title"],
        description=data["description"],
        ingredients=data["ingredients"],
    )

