from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.constants.constants import *

from app.routers import  doc_api, file_api

origins = ["*"]

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESC,
    version=APP_VERSION,
    contact=APP_CONTACT,
    license_info=APP_LICENSE
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=origins,
    allow_headers=origins,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(file_api.router)

app.include_router(doc_api.router)

@app.get("/")
async def root():
    return {
        "status": "OK!",
        "app": "i see you 👀",
        "date": datetime.now()
    }