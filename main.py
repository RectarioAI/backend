from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.recipes import views
from router.auth import auth

app = FastAPI()
app.include_router(auth, prefix="/auth")
app.include_router(views, prefix="/views")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
