import numpy as np
import random
import logging
from copy import deepcopy

from Transaction import Transaction
from Block import Block
from utils import expon_distribution
from DiscreteEventSim import simulation, Event


from config import RATE_PARAMETER, INITIAL_COINS
import config

logger = logging.getLogger(__name__)


class Link:
    def __init__(self, peer1: "Peer", peer2: "Peer"):
        self.peer1 = peer1
        self.peer2 = peer2
        # overall latency = ρij + |m|/cij + dij
        self.pij = random.uniform(10, 501)  # ms
        self.cij = 5 if peer1.is_slow_network or peer2.is_slow_network else 100  # Mbps
        self.cij = self.cij*1024/8*1000  # kB/ms

    def get_delay(self, message: Transaction):
        dij = expon_distribution((96/8)/self.cij)  # ms
        return self.pij + message.size/self.cij + dij  # ms

    def __repr__(self):
        return f"Link({self.peer1}, {self.peer2})"

    def __eq__(self, other):
        return (self.peer1 == other.peer1 and self.peer2 == other.peer2) or (self.peer1 == other.peer2 and self.peer2 == other.peer1)

    def __hash__(self):
        return hash((self.peer1, self.peer2))


class BlockChain:
    blocks: list[Block]
    block_tree: dict[Block, Block]
    chain_length: dict[Block, int]
    __balances: dict["Peer", float]
    __leaves: list[Block]
    # all transactions in the blocks
    __transactions_in_blocks: list[Transaction]
    __transactions_new: list[Transaction]  # all transactions in the network
    avg_interval_time: float  # avg block interval time in ms
    hk: float  # hash power of the network
    peer: "Peer"

    def __init__(self, peer: "Peer"):
        self.avg_interval_time = 1000  # ms
        self.cur_longest_chain = 1
        self.chain_length = {}

        self.__transactions_new = []
        self.__transactions_in_blocks = []

        self.peer: Peer = peer

        genesis_block = self.create_genesis_block()
        self.add_block(genesis_block)

    def create_genesis_block(self) -> Block:
        genesis_block = Block()
        genesis_block.block_id = 0
        genesis_block.prev_block = None
        genesis_block.timestamp = 0
        genesis_block.transactions = []
        return genesis_block

    def longest_chain(self) -> (Block, int):
        cur_longest_chain = 0
        longest_chains = []
        for block, length in self.chain_length.items():
            if length > cur_longest_chain:
                longest_chains = []
                cur_longest_chain = length
            if length == cur_longest_chain:
                longest_chains.append(block)
        return longest_chains[0], cur_longest_chain

    def add_block(self, block: Block) -> bool:

        if not self.validate_block(block):
            return False

        prev_block = block.prev_block
        if prev_block not in self.blocks:
            return False
        chain_len_upto_block = self.chain_length[prev_block] + 1
        self.blocks.append(block)
        self.block_tree[block] = prev_block
        self.chain_length[block] = chain_len_upto_block

        self.__leaves.append(block)

        if prev_block in self.__leaves:
            self.__leaves.remove(prev_block)

        for transaction in block.transactions:
            self.__transactions_in_blocks.append(transaction)
            self.__balances[transaction.from_peer] -= transaction.amount
            self.__balances[transaction.to_peer] += transaction.amount

        if chain_len_upto_block > self.cur_longest_chain:
            self.cur_longest_chain = chain_len_upto_block
            self.generate_block()

    def add_transaction(self, transaction: Transaction) -> bool:
        if transaction in self.__transactions_new:
            return False
        self.__transactions_new.append(transaction)
        logger.info(f"Transaction added: {transaction}")
        if len(self.__transactions_new) > config.BLOCK_GEN_TRXN_THRESHOLD:
            self.generate_block()

    def generate_block(self) -> Block:
        new_block = Block()
        new_block.block_id = random.randint(0, 1000000)
        new_block.prev_block, _ = self.longest_chain()
        new_block.transactions = deepcopy(self.__transactions_new)
        new_block.timestamp = simulation.clock
        self.__transactions_new = []

        delay = random.expovariate(self.peer.hk/self.avg_interval_time)
        new_event = Event("mine_block", simulation.clock,
                          delay, self.pre_broadcast_block, (new_block,), f"{new_block.block_id}")
        simulation.enqueue(new_event)

    def broadcast_block(self, block: Block):
        self.peer.broadcast_block(block)

    def pre_broadcast_block(self, block: Block):
        # if block.prev_block == self.longest_chain()[0]:
        new_event = Event("broadcast_block", simulation.clock,
                          0, self.broadcast_block, (block,), f"{block.block_id}")
        simulation.enqueue(new_event)

    def validate_block(self, block: Block) -> bool:
        '''
        1. no balance of any peer should go negative
        2. transactions are not repeated
        '''
        block_total_transactions = self.__balances.copy()
        for transaction in block.transactions:
            block_total_transactions[transaction.from_peer] -= transaction.amount
            block_total_transactions[transaction.to_peer] += transaction.amount
        for peer, balance in block_total_transactions.items():
            if balance < 0:
                return False

        for transaction in block.transactions:
            if transaction in self.__transactions_in_blocks:
                return False

        return True

    def validate_chain(self):
        raise Exception("Not implimented")

    def get_balance(self, peer_id):
        raise Exception("Not implimented")

    def __repr__(self):
        raise Exception("Not implimented")


class Peer:
    id: int
    is_slow_network: bool
    is_slow_cpu: bool
    # connected_peers: list["Peer"]
    neighbours: dict["Peer", Link]
    crypto_coins: int
    forwarded_txns: list[Transaction]
    forwarded_blocks: list[Block]
    cpu_power: float = 0.0

    def __init__(self, id, is_slow_network=False, is_slow_cpu=False):
        self.id = id
        self.is_slow_network = is_slow_network
        self.is_slow_cpu = is_slow_cpu
        self.crypto_coins = INITIAL_COINS
        self.neighbours = {}

        self.forwarded_blocks = []
        self.forwarded_txns = []

        self.block_chain = BlockChain(self)

    def connect(self, peer: "Peer", link: Link):
        # self.connected_peers.append(peer)
        self.neighbours[peer] = link

    def disconnect(self, peer):
        # self.connected_peers.remove(peer)
        self.neighbours.pop(peer)

    def __repr__(self):
        return f"Peer(id={self.id})"

    @property
    def connected_peers(self):
        return list(self.neighbours.keys())

    def create_txn(self, timestamp):
        to_peer = np.random.choice(self.connected_peers)
        amount = random.uniform(0, self.crypto_coins)
        self.crypto_coins -= amount
        return Transaction(self, to_peer, amount, timestamp)

    def __forward_txn_to_peer(self, txn: Transaction, peer: "Peer"):
        '''
        Forward a transaction to given peer.
        '''
        delay = self.neighbours[peer].get_delay(txn)
        new_event = Event("receive_transaction", simulation.clock,
                          delay, peer.receive_txn, (txn, self), f"{self.id}->{peer.id}; Δ:{delay}ms")
        simulation.enqueue(new_event)

    def broadcast_txn(self, txn):
        '''
        Broadcast a transaction to all connected peers.
        '''
        # logger.info(f"Broadcasting transaction: {txn}")
        for peer in self.connected_peers:
            self.__forward_txn_to_peer(txn, peer)

    def forward_txn(self, txn, peers):
        '''
        Forward a transaction to given peers.
        '''
        for peer in peers:
            self.__forward_txn_to_peer(txn, peer)

    def broadcast_block(self, block: Block):
        '''
        Broadcast a block to all connected peers.
        '''
        logger.info(f"Broadcasting block: {block}")
        for peer in self.connected_peers:
            self.__forward_block_to_peer(block, peer)

    def __forward_block_to_peer(self, block: Block, peer: "Peer"):
        '''
        Forward a block to given peer.
        '''
        delay = self.neighbours[peer].get_delay(block)
        new_event = Event("receive_block", simulation.clock,
                          delay, peer.receive_block, (block, self), f"{self.id}->{peer.id}; Δ:{delay}ms")
        simulation.enqueue(new_event)

    def forward_block(self, block, peers):
        '''
        Forward a block to given peers.
        '''
        for peer in peers:
            self.__forward_block_to_peer(block, peer)

    def receive_block(self, block: Block, source: "Peer"):
        '''
        Receive a block from another peer.
        validate the block
        forward the block to other peers if needed* avoid loop
        '''
        logger.info(
            f"Received block: from:{self.id} block_id:{block.block_id}")

        if block in self.forwarded_blocks:
            return

        self.block_chain.add_block(block)

        self.forwarded_blocks.append(block)
        self.forward_block(
            block, list(filter(lambda x: x != source, self.connected_peers)))

    def receive_txn(self, txn: Transaction, source: "Peer"):
        '''
        Receive a transaction from another peer.
        validate the transaction
        forward the transaction to other peers if needed* avoid loop
        '''
        logger.info(
            f"Received transaction: from:{self.id} txn_id:{txn.txn_id}")

        if txn in self.forwarded_txns:
            return

        self.block_chain.add_transaction(txn)

        self.forwarded_txns.append(txn)
        self.forward_txn(
            txn, list(filter(lambda x: x != source, self.connected_peers)))
