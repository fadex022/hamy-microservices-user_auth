from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from configuration.config import DBSettings

db_settings = DBSettings()

DB_URL = f"postgresql+psycopg2://{db_settings.db_user}:{db_settings.db_password}@{db_settings.db_host}:\
        {db_settings.db_port}/{db_settings.db_name}"

engine = create_engine(DB_URL)

Base = declarative_base()

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def sess_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()
