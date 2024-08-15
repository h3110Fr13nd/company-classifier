import csv
import io

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import create_table, get_db
from app.models import Company
from app.schemas import CompanyCreate
from app.utils import classify_technology_company

app = FastAPI()


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()
    csv_data = csv.DictReader(io.StringIO(contents.decode("utf-8")))

    # Extract column names
    column_names = csv_data.fieldnames

    if "Description" not in column_names:
        raise HTTPException(
            status_code=400, detail="CSV must contain a 'Description' column"
        )

    # Create the table in the database
    create_table(db, column_names)

    # Process each row
    for row in csv_data:
        description = row["Description"]
        is_tech_company = classify_technology_company(description)

        company_data = CompanyCreate(**row, technology_company=is_tech_company)

        db_company = Company(**company_data.dict())
        print(db_company)
        db.add(db_company)

    db.commit()

    return {"message": "CSV processed successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
