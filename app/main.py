from fastapi import FastAPI
from app.routers import gloss2text, pose2gloss


app = FastAPI()
app.include_router(gloss2text.router)
app.include_router(pose2gloss.router)