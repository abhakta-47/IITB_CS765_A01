from utils import generate_random_id


class Transaction:
    from_id: "Peer"
    to_id: "Peer"
    amount: int
    txn_id: int
    timestamp: float

    def __init__(self, from_id, to_id, amount, timestamp):
        self.txn_id = generate_random_id(4)
        self.from_id = from_id
        self.to_id = to_id
        self.amount = amount
        self.timestamp = timestamp
        self.size = 1  # KB

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return (f"Transaction(id:{self.txn_id}, from:{(self.from_id).__repr__()}, to:{(self.to_id).__repr__()}, :{self.amount}, 󰔛:{self.timestamp})")
