from sqlalchemy import  Column, Date, Numeric, String

from .db import Base


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(String, primary_key=True)
    transaction = Column(String, unique=True, index=True)
    merchant = Column(String, index=True)
    order = Column(String)
    customer = Column(String)
    amount = Column(Numeric(14, 2))
    type = Column(String)
    created_at = Column(Date, index=True)
    updated_at = Column(Date)
    settled = Column(Numeric(14, 2))
