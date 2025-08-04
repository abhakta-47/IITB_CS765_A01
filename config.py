class Config:
    NUMBER_OF_PEERS = 20  # n
    Z1 = 0.3  # zeta1
    Z2 = 0.3  # zeta2
    AVG_TXN_INTERVAL_TIME = 100  # Ttx

    ## below parameters are unchanged for all the experiments

    SAVE_RESULTS = False

    Z0 = 0.5  # network z0 is slow

    NUMBER_OF_TRANSACTIONS_PER_PEER = 200  # not used

    # mean of exponential time interval bw transactions (ms)
    INITIAL_COINS = 1000
    EVENT_QUEUE_TIMEOUT = 5
    BLOCK_TXNS_MAX_THRESHOLD = 1020  # 1020
    BLOCK_TXNS_TARGET_THRESHOLD = 5
    BLOCK_TXNS_MIN_THRESHOLD = 1
    AVG_BLOCK_MINING_TIME = 10000  # avg block interval time (ms)

    # sim stop conditions
    MAX_NUM_BLOCKS = NUMBER_OF_PEERS * 3

    NUMBER_OF_TRANSACTIONS = MAX_NUM_BLOCKS * BLOCK_TXNS_TARGET_THRESHOLD

    def __repr__(self) -> str:
        return f"Config: {self.NUMBER_OF_PEERS} peers, {self.NUMBER_OF_TRANSACTIONS} transactions, {self.MAX_NUM_BLOCKS} blocks"


# CONFIG = Config()


def update_config(config: Config):
    global CONFIG
    CONFIG = config
    return CONFIG
