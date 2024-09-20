from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.dbconfig import configure_database
from app.database.models import db
from app.routers import user, image_retrieval

app = FastAPI()

# CORS Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
configure_database()


app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(image_retrieval.router, prefix="/ELimage", tags=["image_retrieval"])
# app.include_router(auth.router, tags=["auth"])

# To Run
# uvicorn app.main:app --reload --host 172.18.101.47 --port 2525