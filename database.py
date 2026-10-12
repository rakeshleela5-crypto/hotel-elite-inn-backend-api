import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Railway provides DATABASE_URL / POSTGRES_URL in postgres:// format; SQLAlchemy 2.0 expects postgresql://
raw_db_url = (
    os.getenv("DATABASE_URL") or 
    os.getenv("POSTGRES_URL") or 
    os.getenv("DATABASE_PUBLIC_URL") or 
    os.getenv("DATABASE_PRIVATE_URL") or 
    os.getenv("PGURL") or 
    ""
).strip()

if not raw_db_url:
    # Graceful local fallback to SQLite if no remote database is configured
    DATABASE_URL = "sqlite:///./hotel_elite.db"
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    if raw_db_url.startswith("postgres://"):
        DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = raw_db_url
    
    # Production-ready PostgreSQL connection pool
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
