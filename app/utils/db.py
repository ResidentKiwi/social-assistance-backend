import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SOCIAL = os.getenv("DB_SOCIAL_NAME")
DB_SHARED = os.getenv("DB_SHARED_NAME")

URL_SOCIAL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_SOCIAL}"
URL_SHARED = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_SHARED}"

engine_social = create_engine(URL_SOCIAL, pool_pre_ping=True)
engine_shared = create_engine(URL_SHARED, pool_pre_ping=True)

SessionSocial = sessionmaker(bind=engine_social)
SessionShared = sessionmaker(bind=engine_shared)

def get_social_db():
    db = SessionSocial()
    try:
        yield db
    finally:
        db.close()

def get_shared_db():
    db = SessionShared()
    try:
        yield db
    finally:
        db.close()
