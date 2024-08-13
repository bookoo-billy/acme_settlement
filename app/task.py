import datetime
from decimal import Decimal

from database import models
from database.db import Base, engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
import payments
import time
import uuid

def settle(db: Session, transaction):
    if transaction is None:
        return
    
    prior_settlement = db.query(models.Settlement).filter(
        models.Settlement.merchant == transaction["merchant"],
        models.Settlement.updated_at < datetime.datetime.fromisoformat(transaction["updated_at"])
    ).order_by(models.Settlement.updated_at.desc()).first()

    settled = Decimal(transaction["amount"])
    
    if prior_settlement is not None:
        settled += Decimal(transaction["amount"])

    settlement = models.Settlement(
        id=str(uuid.uuid4()),
        settled=settled,
        transaction=transaction["id"],
        merchant=transaction["merchant"],
        order=transaction["order"],
        customer=transaction["customer"],
        amount=Decimal(transaction["amount"]),
        type=transaction["type"],
        created_at=datetime.datetime.fromisoformat(transaction["created_at"]),
        updated_at=datetime.datetime.fromisoformat(transaction["updated_at"])
    )

    try:
        db.add(settlement)
        db.commit()
        db.refresh(settlement)
    except IntegrityError as ex:
        # Ignore integrity errors on unique constraints
        # because the Payments API may have multiple
        # transactions for the same date, causing
        # this task to attempt to re-process settled transactions
        session.rollback()
    return settlement

def get_last_settlement(db: Session) -> models.Settlement:
    return db.query(models.Settlement).order_by(models.Settlement.updated_at.desc()).first()

try:
    Base.metadata.create_all(engine)
except:
    logging.exception("Could not create table")

while True:
    with Session(engine) as session:
        logging.info("Attempting to settle pending transactions")
        start_point = get_last_settlement(session)
        try:
            # Read latest orders from the Payment API
            transactions = payments.list_transactions(ordering="updated_at", updated_at__gte=start_point.updated_at if start_point else None)

            for transaction in transactions:
                if isinstance(transaction, Exception):
                    # We've settled the last processed transaction and will retry later
                    logging.warn("Partially settled pending transactions, will retry later")
                    raise transaction

                # Settle the transaction
                settle(session, transaction)

            logging.info("Successfully settled all pending transactions")
        except:
            logging.exception("Failure while settling pending transactions")
        session.close()
    # Poll the Payments API every 5 seconds for transactions
    time.sleep(5)
