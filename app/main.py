import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.cheatsheet import router as cheatsheet_router
from app.routes.chat import router as chat_router
from app.routes.history import router as history_router
from app.routes.rag import router as rag_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title="QuickSheet-AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cheatsheet_router)
app.include_router(chat_router)
app.include_router(rag_router)
app.include_router(history_router)


@app.api_route("/health", methods=["GET", "HEAD"])
def health_check() -> dict:
    return {"status": "ok"}


@app.api_route("/", methods=["GET", "HEAD"])
def read_root() -> dict:
    return {"message": "Welcome to QuickSheet AI API"}
