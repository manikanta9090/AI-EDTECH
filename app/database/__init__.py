import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./edtech.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    from app.models import Base
    Base.metadata.create_all(bind=engine)