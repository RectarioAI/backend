from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.user_model import User, UserAuth
from config.connection import get_collection
from schemas.user_schema import fromDictToModel


auth = APIRouter()

@auth.post("/login")
async def login(user: UserAuth):
    result = get_collection("Users").find_one({"email": user.email})
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"message": "User not found"}
        )
    else:
        if result["password"] == user.password:
            result = fromDictToModel(result)
            return JSONResponse(
                status_code=200,
                content={"message": result.toDict()}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"message": "Password incorrect"}
            )
    

@auth.post("/register")
def register(user: dict):
    userNew = fromDictToModel(user)
    result = get_collection("Users").find_one({"email": userNew.email})
    if result is None:
        get_collection("Users").insert_one(userNew.toDict())
        return JSONResponse(
            status_code=201,
            content={"message": "User created"}
        )
    else:
        return JSONResponse(
            status_code=404,
            content={"message": "User already exists"}
        )