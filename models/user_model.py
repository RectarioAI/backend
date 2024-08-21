from pydantic import BaseModel

class User(BaseModel):
    password: str
    names: str
    last_names: str
    age: str
    genre: str
    email: str

    def toDict(self):
        return {
            "password": self.password,
            "names": self.names,
            "last_names": self.last_names,
            "age": self.age,
            "genre": self.genre,
            "email": self.email
        }


class UserAuth(BaseModel):
    email: str
    password: str

    def toDict(self):
        return {
            "password": self.password,
            "email": self.email
        }
