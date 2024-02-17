class CONFIG:
    # def __init__(self) -> None:
    # pass
    SAVE_RESULTS = True
    #
    NUMBER_OF_PEERS = 20
    Z0 = 0.7  # network z0 is slow
    Z1 = 0.8  # cpu z1 is slow
    NUMBER_OF_TRANSACTIONS_PER_PEER = 15
    NUMBER_OF_TRANSACTIONS = NUMBER_OF_TRANSACTIONS_PER_PEER*NUMBER_OF_PEERS

    # mean of exponential time interval bw transactions (ms)
    INITIAL_COINS = 1000
    EVENT_QUEUE_TIMEOUT = 5
    BLOCK_TXNS_MAX_THRESHHOLD = 10  # 1020
    BLOCK_TXNS_MIN_THRESHHOLD = 1
    AVG_TXN_INTERVAL_TIME = 1000
    AVG_BLOCK_MINING_TIME = 20000  # avg block interval time (ms)

    # sim stop conditions
    MAX_NUM_BLOCKS = (NUMBER_OF_TRANSACTIONS -
                      NUMBER_OF_TRANSACTIONS_PER_PEER)/BLOCK_TXNS_MAX_THRESHHOLD

    @property
    def __dict__(self) -> dict:
        return ({
            "SAVE_RESULTS": self.SAVE_RESULTS,
            "NUMBER_OF_PEERS": self.NUMBER_OF_PEERS,
            "Z0": self.Z0,
            "Z1": self.Z1,
            "NUMBER_OF_TRANSACTIONS_PER_PEER": self.NUMBER_OF_TRANSACTIONS_PER_PEER,
            "NUMBER_OF_TRANSACTIONS": self.NUMBER_OF_TRANSACTIONS,
            "INITIAL_COINS": self.INITIAL_COINS,
            "EVENT_QUEUE_TIMEOUT": self.EVENT_QUEUE_TIMEOUT,
            "BLOCK_TXNS_MAX_THRESHHOLD": self.BLOCK_TXNS_MAX_THRESHHOLD,
            "BLOCK_TXNS_MIN_THRESHHOLD": self.BLOCK_TXNS_MIN_THRESHHOLD,
            "AVG_TXN_INTERVAL_TIME": self.AVG_TXN_INTERVAL_TIME,
            "AVG_BLOCK_MINING_TIME": self.AVG_BLOCK_MINING_TIME,
            "MAX_NUM_BLOCKS": self.MAX_NUM_BLOCKS,
        })
