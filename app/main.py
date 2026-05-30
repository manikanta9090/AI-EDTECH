from fastapi import FastAPI
from app.api import router
from app.database import init_db

app = FastAPI(title="EdTech NLP-to-SQL API")

app.include_router(router)

init_db()