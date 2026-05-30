import os
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./edtech.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db():
    Base.metadata.create_all(bind=engine)


init_db()