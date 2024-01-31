class Transaction:
    from_id: "Peer"
    to_id: "Peer"
    amount: int
    txn_id: int

    def __init__(self, txn_id, from_id, to_id, amount):
        self.txn_id = txn_id
        self.from_id = from_id
        self.to_id = to_id
        self.amount = amount