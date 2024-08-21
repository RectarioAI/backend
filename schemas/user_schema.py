from models.user_model import User

def fromModelToDict(user: User):
    return {
        "names": user.names,
        "last_names": user.last_names,
        "password": user.password,
        "email": user.email,
        "age": user.age,
        "genre": user.genre,
    }

def fromDictToModel(data: dict):
    return User(
        names=data["names"],
        last_names=data["last_names"],
        password=data["password"],
        email=data["email"],
        age=data["age"],
        genre=data["genre"],
    )