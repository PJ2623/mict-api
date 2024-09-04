from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import models

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from src.routers import auth, users

from contextlib import asynccontextmanager


async def initialize_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client["mict-hackathon"]
    await init_beanie(
        database,
        document_models=[
            models.User,
            models.VerifiedUser,
            models.Poll,
            models.Post,
            models.Announcements,
        ],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="MICT Hackathon API",
    description="API for the MICT Hackathon",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
