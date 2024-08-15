from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_table(db, column_names):
    class DynamicCompany(Base):
        __tablename__ = "companies"

        id = Column(String, primary_key=True, index=True)
        technology_company = Column(Boolean)

        for column in column_names:
            if column != 'id':
                setattr(DynamicCompany, column, Column(String))

    Base.metadata.create_all(bind=engine)