from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base
from config.settings import settings

engine = create_engine(
    f"sqlite:///{settings.DB_PATH}",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
