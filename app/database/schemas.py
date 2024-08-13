import datetime
from decimal import Decimal

from pydantic import BaseModel


class Settlement(BaseModel):
    id: str
    transaction: str
    merchant: str
    order: str
    customer: str
    amount: Decimal
    type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    settled: Decimal

    class Config:
        orm_mode = True
