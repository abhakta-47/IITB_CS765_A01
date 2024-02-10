from utils import generate_random_id
import logging

logger = logging.getLogger(__name__)


class Transaction:
    def __init__(self, from_id, to_id, amount, timestamp):
        self.txn_id: str = generate_random_id(4)
        self.from_id: "Peer" = from_id
        self.to_id: "Peer" = to_id
        self.amount: float = amount
        self.timestamp: float = timestamp
        self.size: int = 1  # KB

        logger.debug(f"{self} <txn_created>: {self.description()}")

    @property
    def __dict__(self) -> dict:
        return {
            "txn_id": self.txn_id,
            "from_id": self.from_id.__repr__(),
            "to_id": self.to_id.__repr__(),
            "amount": self.amount,
            "timestamp": self.timestamp
        }

    def description(self) -> str:
        return (f"Transaction(id:{self.txn_id}, from:{(self.from_id)}, to:{(self.to_id)}, :{self.amount}, 󰔛:{self.timestamp})")

    def __repr__(self) -> str:
        return f"Txn(id={self.txn_id})"
