from fastapi import APIRouter


recipes = APIRouter()


@recipes.get("/")
async def get_recipes():
    return {"message": "Get all recipes"}