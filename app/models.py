from sqlalchemy import Column, String, Boolean
from app.db import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, index=True)
    description = Column(String)
    technology_company = Column(Boolean)
    # Other columns will be added dynamically