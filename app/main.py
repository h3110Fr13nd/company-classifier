import io

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.utils import call_llm

app = FastAPI()


@app.post("/upload/")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    contents = await file.read()
    csv_file = io.StringIO(contents.decode("utf-8"))
    df = pd.read_csv(csv_file)
    df = await call_llm(df)

    result = db.execute(text("SELECT * FROM companies"))
    rows = result.fetchall()
    column_names = result.keys()
    data = [dict(zip(column_names, row)) for row in rows]
    return data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
