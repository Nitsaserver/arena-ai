import os
import time
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from .models import Base, ArenaRound, TrainingData  # ensure models are registered

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

# Read DB config (fallback to docker values if not set)
DB_HOST = os.getenv("DB_HOST", "db")  # ✅ 'db' is the Docker service name
DB_USER = os.getenv("DB_USER", "arena_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "arena_pass")
DB_NAME = os.getenv("DB_NAME", "arena_db")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# Encode password for URL safety
encoded_password = quote_plus(DB_PASSWORD) 
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize and seed the database (with retry for Docker startup delays)."""
    print("Initializing database...")

    from backend import models  # ensure models are loaded

    # Retry if DB isn’t ready yet
    retries = 10
    for i in range(retries):
        try:
            print("Attempting to connect to DB...")
            models.Base.metadata.create_all(bind=engine)
            print("✅ Database connection successful.")
            print("Tables created:", models.Base.metadata.tables.keys())
            break
        except OperationalError as e:
            print(f"⚠️ Database not ready (attempt {i+1}/{retries}): {e}")
            time.sleep(3)
    else:
        raise RuntimeError("❌ Could not connect to the database after multiple attempts.")

    # ✅ Seed initial data if required
    try:
        from backend.seed_data import seed_data
        seed_data()
        print("✅ Database seeded successfully.")
    except Exception as e:
        print(f"⚠️ Skipping seeding or error occurred: {e}")

    print("✅ Done creating tables and initializing DB.")


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
