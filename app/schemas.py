from pydantic import BaseModel

class CompanyCreate(BaseModel):
    id: str
    description: str
    technology_company: bool
    # Other fields will be added dynamically

    class Config:
        orm_mode = True