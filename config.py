NUMBER_OF_PEERS = 20  # n
Z1 = 0.7  # zeta1
Z2 = 0.2  # zeta2
AVG_TXN_INTERVAL_TIME = 10  # Ttx


## below parameters are unchanged for all the experiments

SAVE_RESULTS = False

Z0 = 0.5  # network z0 is slow

NUMBER_OF_TRANSACTIONS_PER_PEER = 200  # not used

# mean of exponential time interval bw transactions (ms)
INITIAL_COINS = 1000
EVENT_QUEUE_TIMEOUT = 5
BLOCK_TXNS_MAX_THRESHOLD = 1020  # 1020
BLOCK_TXNS_TARGET_THRESHOLD = 10
BLOCK_TXNS_MIN_THRESHOLD = 5
AVG_BLOCK_MINING_TIME = 300  # avg block interval time (ms)

# sim stop conditions
MAX_NUM_BLOCKS = NUMBER_OF_PEERS * 5

NUMBER_OF_TRANSACTIONS = MAX_NUM_BLOCKS * BLOCK_TXNS_TARGET_THRESHOLD
