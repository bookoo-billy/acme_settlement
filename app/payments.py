import logging
from typing import Optional
import requests

def list_transactions(ordering: Optional[str], updated_at__gte: Optional[str]):
    params = {}

    # Ordering is always ascending (undocumented Payments API assumption)
    if ordering is not None:
        params["ordering"] = ordering

    if updated_at__gte is not None:
        params["updated_at__gte"] = updated_at__gte

    response = requests.get(
        "https://api-engine-dev.clerq.io/tech_assessment/transactions/",
        params=params
    )

    if response.status_code != 200:
        logging.error(response)
        raise Exception(response)

    transactions = response.json()
    for transaction in transactions["results"]:
        yield transaction
    
    while transactions["next"] is not None:
        response = requests.get(transactions["next"], params=params)
        if response.status_code != 200:
            logging.error(response)
            raise Exception(response)

        transactions = response.json()
        for transaction in transactions["results"]:
            yield transaction
