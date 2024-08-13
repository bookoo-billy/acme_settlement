import datetime

from app.database import models, schemas
from app.database.db import SessionLocal, engine
from typing import Optional, Union
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health():
    return {"status": "UP"}

@app.get("/settlements", response_model=list[schemas.Settlement])
def list_settlements(merchant_id: Optional[str] = None, start_date: Optional[datetime.datetime] = None, end_date: Optional[datetime.datetime] = None, db: Session = Depends(get_db)):
    query = db.query(models.Settlement)
    
    if merchant_id is not None:
        query = query.filter(models.Settlement.merchant == merchant_id)

    if start_date is not None:
        query = query.filter(models.Settlement.updated_at > start_date)

    if end_date is not None:
        query = query.filter(models.Settlement.updated_at < end_date)

    return query.all()

@app.get("/settlements/{settlement_id}", response_model=schemas.Settlement)
def get_settlement(settlement_id: str, q: Union[str, None] = None, db: Session = Depends(get_db)):
    return db.query(models.Settlement).filter(models.Settlement.id == settlement_id).first()
